#!/usr/bin/env python3
"""okf_install.py — instala el MATERIAL del kit OKF en un repo destino (o lo actualiza).

Herramienta de desarrollo del kit: vive en `scripts/`, NO se copia a repos destino
(igual que `okf_selfcheck.py`). Solo stdlib, sin `pip install`
(decisión 0004): el kit sigue siendo markdown + git y este script no es obligatorio —
el camino manual del `GUIDE.md` sigue existiendo.

QUÉ HACE Y QUÉ NO — el corte es **mecánico vs criterio**:

  Hace (determinista, y por eso no se paga en tokens ni se ejecuta mal):
    - copia el contrato `AGENTS.md` + shim `CLAUDE.md`, recortando el andamiaje
      (comentario de cabecera y marcadores `OKF:future-layer`);
    - siembra el esqueleto `knowledge/` (index + log + roadmap) con el `kit_version`
      y las fechas estampadas, y el resultado pasa el linter desde el segundo cero;
    - copia los skills (renombrándolos si van a `docs/okf/`), los scripts, el CI
      y el git hook (con su `chmod +x`);
    - con `--upgrade`, reemplaza esa maquinaria sin tocar el bundle ni `AGENTS.md`.

  NO hace (es criterio, y se queda en el agente — ver `templates/skills/okf-init/`):
    - **sembrar los conceptos**: el *por qué* del proyecto, que es todo el valor;
    - completar los `{{placeholders}}` del contrato y del roadmap;
    - decidir el perfil (`--profile` solo reporta qué carpetas corresponden);
    - el merge del `AGENTS.md` al actualizar (`reference/upgrading.md` §4).

FUENTE DE VERDAD: este archivo es la fuente única del procedimiento MECÁNICO. El
skill `okf-init` **delega** acá y no lo re-statea — si vuelve a describir estos pasos
en prosa, hay dos fuentes que van a derivar (la causa raíz de los bugs del kit; lo
verifica un assert de `okf_selfcheck.py`).

Uso:
  python3 scripts/okf_install.py <repo-destino> [--profile codigo] [--name "Mi Proyecto"]
  python3 scripts/okf_install.py <repo-destino> --minimal      # sin capa de futuro
  python3 scripts/okf_install.py <repo-destino> --no-claude    # skills a docs/okf/
  python3 scripts/okf_install.py <repo-destino> --upgrade      # solo la maquinaria
  python3 scripts/okf_install.py <repo-destino> --dry-run      # no escribe nada

Exit: 0 ok · 1 el linter no pasó sobre lo instalado · 2 error de uso
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]

# Carpetas recomendadas por perfil (`reference/profiles.md`). El instalador NO las crea:
# una carpeta vacía es un WARN del linter y, peor, un lugar que nadie llenó. Las reporta
# para que el agente las cree a medida que siembra conceptos de verdad.
PROFILES = {
    "codigo": ["architecture", "decisions", "domain", "schema", "runbooks", "references"],
    "datos": ["datasets", "tables", "references/metrics", "references/joins", "glossary"],
    "wiki": ["<un dir por tema>", "playbooks", "glossary"],
    "mixto": ["<combiná los de arriba, o inventá los que el dominio pida>"],
}

SKILLS_ALWAYS = ["okf-update", "okf-verify"]
SKILL_FUTURE = "okf-plan"
# Subagentes. Van al repo destino y NO los shippea el plugin, por lo mismo que los skills de
# mantenimiento: un clone sin el plugin tiene que seguir teniéndolos (decisión 0013).
AGENTS = ["okf-reviewer"]
SCRIPTS = ["okf_lint.py", "okf_coldtest.py", "okf_stale.py"]

# Un comentario HTML termina en el PRIMER `-->`. El `.*?` ingenuo se trunca cuando el
# cuerpo del comentario cita un `-->` (mismo bug que cazó el selfcheck en 0.6.0).
_COMMENT_RE = re.compile(r"<!--(?:(?!-->).)*-->", re.S)
_MARKER_LINE_RE = re.compile(r"^[ \t]*<!--\s*OKF:future-layer:(?:start|end)\s*-->[ \t]*\n", re.M)
_MARKED_BLOCK_RE = re.compile(
    r"^[ \t]*<!--\s*OKF:future-layer:start\s*-->[ \t]*\n"
    r".*?"
    r"^[ \t]*<!--\s*OKF:future-layer:end\s*-->[ \t]*\n",
    re.S | re.M,
)


class Plan:
    """Acumula las escrituras para poder ofrecer --dry-run sin duplicar la lógica."""

    def __init__(self, dry: bool) -> None:
        self.dry = dry
        self.actions: list[str] = []

    def write(self, path: Path, text: str, executable: bool = False) -> None:
        self.actions.append(f"escribir  {path}")
        if self.dry:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        if executable:
            path.chmod(path.stat().st_mode | 0o111)

    def copy(self, src: Path, dst: Path, executable: bool = False) -> None:
        self.write(dst, src.read_text(encoding="utf-8"), executable=executable)

    def mkdir(self, path: Path) -> None:
        self.actions.append(f"crear     {path}/")
        if not self.dry:
            path.mkdir(parents=True, exist_ok=True)

    def skip(self, why: str) -> None:
        self.actions.append(f"omitir    {why}")


def strip_header_comment(text: str) -> str:
    """Borra SOLO el comentario de cabecera (el de instrucciones de instalación).

    No usa `_COMMENT_RE` global: los marcadores `OKF:*` también son comentarios HTML y
    se tratan aparte, según el nivel de instalación.
    """
    return re.sub(r"^\s*<!--(?:(?!-->).)*-->\s*", "", text, count=1, flags=re.S)


def read_template(rel: str) -> str:
    p = KIT / "templates" / rel
    if not p.is_file():
        sys.exit(f"okf_install: falta el template '{p}' — ¿el kit está completo?")
    return p.read_text(encoding="utf-8")


def kit_version() -> str:
    v = (KIT / "VERSION").read_text(encoding="utf-8").strip()
    if not v:
        sys.exit("okf_install: VERSION está vacío — es la fuente de verdad de la versión")
    return v


# ------------------------------------------------------------------ transformaciones
def build_agents(version: str, minimal: bool, name: str | None) -> str:
    """El contrato instalado: sin comentario de cabecera y sin andamiaje de marcadores."""
    text = strip_header_comment(read_template("AGENTS.md"))
    if minimal:
        text = _MARKED_BLOCK_RE.sub("", text)
    text = _MARKER_LINE_RE.sub("", text)
    if name:
        text = text.replace("{{PROJECT_NAME}}", name)
    # Un marcador que sobrevive es andamiaje instalado: se paga en cada turno y manda
    # al agente a archivos que quizá no existen. Preferimos fallar acá.
    assert "OKF:future-layer" not in text, "quedó un marcador en el contrato instalado"
    return text


# Las secciones que escribe (y por lo tanto puede reemplazar) el kit. Todo lo demás
# —el título, las reglas duras, las capas no autoritativas y cualquier sección que haya
# agregado el usuario— es contenido suyo y se conserva palabra por palabra.
KIT_SECTIONS = ("## 1.", "## 2.", "## 3.", "## Procedimientos")


def split_contract(text: str) -> list[tuple[str | None, str]]:
    """El contrato como [(heading, bloque)], preservando orden y texto exacto.

    El primer bloque lleva `heading=None`: es el título + la descripción del proyecto.
    """
    out: list[tuple[str | None, str]] = []
    cur_head: str | None = None
    cur: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            out.append((cur_head, "".join(cur)))
            cur_head, cur = line.rstrip("\n"), [line]
        else:
            cur.append(line)
    out.append((cur_head, "".join(cur)))
    return out


def _is_kit_section(head: str | None) -> bool:
    return head is not None and head.startswith(KIT_SECTIONS)


def upgrade_contract(installed: str, version: str, minimal: bool) -> tuple[str, list[str], str | None]:
    """Reemplaza SOLO las secciones del kit; devuelve (texto, reemplazadas, motivo_de_aborto).

    Un `AGENTS.md` no se puede regenerar de cero: mezcla el texto del kit con contenido del
    usuario que no está en ningún lado más (sus reglas duras, dónde están los secretos). Por
    eso se hace por secciones y **ante cualquier forma inesperada se aborta**: perder eso es
    irreversible, y una actualización que borra trabajo es peor que no actualizar.
    """
    fresh = split_contract(build_agents(version, minimal, None))
    fresh_kit = {h: b for h, b in fresh if _is_kit_section(h)}
    old = split_contract(installed)

    # Migración one-time: hasta la 0.7.4 las capas no autoritativas vivían DENTRO de §1,
    # entrelazadas con la prosa del kit en el mismo párrafo. No hay forma mecánica de
    # separarlas (el usuario escribe antes y después de la frase fija), así que se pide el
    # movimiento a mano en vez de adivinar y borrar.
    heads = [h for h, _ in old if h]
    if not any(h.startswith("## Capas NO autoritativas") for h in heads):
        if "Capas NO autoritativas" in installed:
            return "", [], (
                "el contrato tiene las capas no autoritativas DENTRO de §1 (formato viejo), "
                "entrelazadas con el texto del kit.\n"
                "  → movelas a una sección propia `## Capas NO autoritativas` (después de "
                "`## Reglas duras`) y volvé a correr esto.\n"
                "  No lo hago yo: ahí hay texto tuyo mezclado con el mío y separarlo a ciegas "
                "puede borrarte contenido.")

    replaced, out = [], []
    for head, block in old:
        if _is_kit_section(head):
            # Se aparea por el PREFIJO (`## 2.`), no por el título completo: el título de una
            # sección cambia entre versiones y aparear por texto exacto abortaría de gusto.
            pref = next(p for p in KIT_SECTIONS if head.startswith(p))
            key = next((k for k in fresh_kit if k.startswith(pref)), None)
            if key is None:                     # sección del kit que ya no existe
                return "", [], (f"la sección {head!r} no existe en el kit v{version}. "
                                "Migrala a mano: puede tener contenido tuyo adentro.")
            new_block = fresh_kit.pop(key)
            out.append(new_block)
            # Se compara ANTES de sacar la clave: mirar el dict ya vaciado daba siempre
            # "cambió" y el upgrade no era idempotente (reportaba trabajo que no hizo).
            if new_block != block:
                replaced.append(head)
        else:
            out.append(block)
    # Secciones que el kit agregó en una versión posterior a la instalada.
    for head, block in fresh:
        if _is_kit_section(head) and head in fresh_kit:
            out.append(block); replaced.append(f"{head} (nueva)")
    return "".join(out), replaced, None


def build_claude() -> str:
    """El shim instalado: `@AGENTS.md` y nada más.

    Se construye igual que el contrato en vez de copiarse crudo. Copiado, el comentario de
    cabecera —que le explica al lector cómo instalar el kit— viajaba al repo destino y se
    pagaba en cada turno, contradiciendo al `GUIDE` que promete un shim de una línea.
    """
    text = strip_header_comment(read_template("CLAUDE.md"))
    assert "<!--" not in text, "quedó un comentario en el shim instalado"
    return text


def build_index(version: str, minimal: bool, name: str | None,
                roadmap_desc: str = "") -> str:
    """`knowledge/index.md`: version estampada, y sin links a carpetas que aún no existen.

    Las entradas de ejemplo del template apuntan a `decisions/index.md` etc.: dejarlas
    sería un link roto (WARN del linter) el día uno. Se reemplazan por una consigna.
    """
    text = strip_header_comment(read_template("knowledge/index.md"))
    text = text.replace("{{KIT_VERSION}}", version)
    # El comentario YAML de la línea de kit_version es instrucción de instalación.
    text = re.sub(r"(^kit_version:.*?)\s+#.*$", r"\1", text, flags=re.M)

    # La entrada del index es, por convención, la `description` del concepto — y el linter
    # ahora lo verifica. Se copia la del roadmap tal cual en vez de sembrar un segundo
    # placeholder: dos textos distintos para la misma frase divergen por construcción.
    roadmap_block = (
        "# Roadmap\n\n"
        f"* [Rumbo de {name or '{{proyecto}}'}](roadmap.md) - {roadmap_desc}\n"
    )
    # El formato de la entrada va en backticks a propósito: el linter quita el inline-code
    # antes de buscar links, así que la consigna no cuenta como link roto el día uno.
    subdirs_block = (
        "# Subdirectories\n\n"
        "{{una línea por carpeta a medida que la siembres, con este formato: "
        "`* [nombre](nombre/index.md) - qué hay en esta carpeta`}}\n"
    )
    # Se reconstruyen los dos bloques enteros en vez de parchear líneas: el template
    # los trae con ejemplos, y un parche por línea derivaría al primer cambio de ejemplo.
    # `checks.md` va SIEMPRE (también en --minimal): su entrada tiene que coincidir
    # palabra por palabra con su `description`, que el linter cruza.
    checks_block = (
        "# Runbook\n\n"
        "* [Cómo se comprueba que este repo anda](checks.md) - "
        "Los comandos que prueban que el código funciona, y qué cubre cada uno.\n"
    )
    head = text.split("# Roadmap", 1)[0].rstrip() + "\n\n"
    return head + ("" if minimal else roadmap_block + "\n") + checks_block + "\n" + subdirs_block


def build_log(version: str) -> str:
    text = strip_header_comment(read_template("knowledge/log.md"))
    text = text.replace("{{KIT_VERSION}}", version)
    # Un heading `## {{YYYY-MM-DD}}` es un WARN de fecha no-ISO: se estampa hoy.
    return text.replace("{{YYYY-MM-DD}}", datetime.date.today().isoformat())


def build_roadmap(name: str | None) -> str:
    text = strip_header_comment(read_template("knowledge/_roadmap.md"))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = text.replace("{{YYYY-MM-DDTHH:MM:SSZ}}", now)
    if name:
        text = text.replace("{{Rumbo de <proyecto>}}", f"Rumbo de {name}")
    # El ejemplo de "Ahora" linkea un `_changes/` que no existe todavía (link roto). En
    # una instalación nueva la verdad es que no hay nada en curso.
    text = re.sub(
        r"^- \{\{\[.*?\]\(_changes/.*?\)\s*—.*?\}\}$",
        "- (nada activo)", text, flags=re.M | re.S,
    )
    return text


def build_checks() -> str:
    """`knowledge/checks.md`: los comandos que prueban que el código anda.

    Se siembra SIEMPRE, incluida la instalación mínima. Es el único concepto que contesta
    "¿cómo sé que lo que escribí funciona?" — el resto del bundle dice qué hay y por qué.
    Y es lo único que un estudio independiente sobre archivos de contexto midió como
    ganancia real: la *configuración de tests no obvia* que el código no revela.
    """
    text = strip_header_comment(read_template("knowledge/_checks.md"))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return text.replace("{{YYYY-MM-DDTHH:MM:SSZ}}", now)


def agent_target(target: Path, no_claude: bool, agent: str) -> Path:
    """Sin subagentes, el revisor sigue sirviendo como procedimiento legible a mano."""
    if no_claude:
        return target / "docs" / "okf" / f"{agent}.md"
    return target / ".claude" / "agents" / f"{agent}.md"


def skill_target(target: Path, no_claude: bool, skill: str) -> Path:
    """Los tres SKILL.md se llaman igual: fuera de `.claude/skills/` hay que RENOMBRARLOS,
    y dejarlos fuera de `knowledge/` (traen frontmatter sin `type` y el linter los rechaza).
    """
    if no_claude:
        return target / "docs" / "okf" / f"{skill}.md"
    return target / ".claude" / "skills" / skill / "SKILL.md"


# ------------------------------------------------------------------ pasos de instalación
# El sello que llevan los archivos de maquinaria instalados. Guarda la versión **y el hash
# de lo que escribimos**: con la versión sola no se puede distinguir "es mi copia vieja" de
# "lo editaste vos", y ahí es donde OpenSpec pisa trabajo del usuario en silencio.
STAMP_MARK = "okf-kit:managed"
_STAMP_RE = re.compile(rf"^.*{re.escape(STAMP_MARK)} v(\S+) sha1:([0-9a-f]{{40}}).*$\n?",
                       re.M)
_COMMENT = {".md": "<!-- {} -->", ".py": "# {}", ".yml": "# {}", ".yaml": "# {}"}


def _stamped(path: Path, body: str, version: str) -> str:
    """El contenido con su sello al final, comentado según el tipo de archivo."""
    digest = hashlib.sha1(body.encode("utf-8")).hexdigest()
    tpl = _COMMENT.get(path.suffix, "# {}")
    sep = "" if body.endswith("\n") else "\n"
    return body + sep + tpl.format(
        f"{STAMP_MARK} v{version} sha1:{digest} — lo reemplaza `okf_install.py --upgrade`; "
        "si lo editás, deja de actualizarse solo") + "\n"


def classify_managed(dst: Path) -> str:
    """`ausente` | `intacto` | `editado` | `sin-sello`.

    Tres desenlaces y no dos: sin esto, un upgrade o pisa lo que el usuario tocó, o no
    actualiza nunca por miedo. `sin-sello` es material de un kit anterior al sellado — no se
    puede afirmar que lo editaron, así que se trata con la misma prudencia.
    """
    if not dst.is_file():
        return "ausente"
    txt = dst.read_text(encoding="utf-8", errors="replace")
    m = _STAMP_RE.search(txt)
    if not m:
        return "sin-sello"
    body = _STAMP_RE.sub("", txt)
    return "intacto" if hashlib.sha1(body.encode("utf-8")).hexdigest() == m.group(2) else "editado"


def install_machinery(plan: Plan, target: Path, *, minimal: bool, no_claude: bool,
                      want_ci: bool, want_hook: bool, version: str = "",
                      respect_edits: bool = False) -> None:
    """Skills + scripts + CI + hook. Es idéntico en instalación y en --upgrade.

    Con `respect_edits` (el camino de `--upgrade`) no pisa un archivo que el usuario editó:
    lo reporta y sigue. En una instalación fresca no aplica — no hay nada que respetar.
    """
    def put(src: Path, dst: Path, executable: bool = False) -> None:
        body = src.read_text(encoding="utf-8")
        if respect_edits:
            state = classify_managed(dst)
            if state in ("editado", "sin-sello"):
                plan.skip(f"{dst.relative_to(target)} ({'lo editaste' if state == 'editado' else 'sin sello del kit'}: NO se pisa)")
                return
        plan.write(dst, _stamped(dst, body, version) if version else body, executable=executable)
    skills = list(SKILLS_ALWAYS) + ([] if minimal else [SKILL_FUTURE])
    for skill in skills:
        put(KIT / "templates" / "skills" / skill / "SKILL.md",
            skill_target(target, no_claude, skill))
    for agent in AGENTS:
        put(KIT / "templates" / "agents" / f"{agent}.md",
            agent_target(target, no_claude, agent))
    for script in SCRIPTS:
        put(KIT / "templates" / "scripts" / script, target / "scripts" / script)
    if want_ci:
        put(KIT / "templates" / "ci" / "okf.yml",
            target / ".github" / "workflows" / "okf.yml")
    else:
        plan.skip(".github/workflows/okf.yml (--no-ci)")
    if not want_hook:
        plan.skip("git hook (--no-hook)")
    elif not (target / ".git").is_dir():
        plan.skip("git hook (el destino no es un repo git — SIN enforcement)")
    elif (target / ".git" / "hooks" / "pre-commit").is_file() and not _hook_is_ours(target):
        # Pisarlo apaga en silencio los tests o el lint-staged del usuario, y no se entera
        # hasta que mergea algo roto. La guarda existía y solo se consultaba en --upgrade.
        plan.skip("git hook (ya hay un pre-commit que NO es del kit: no se pisa — ver abajo)")
    else:
        put(KIT / "templates" / "hooks" / "pre-commit",
            target / ".git" / "hooks" / "pre-commit", executable=True)


def install_fresh(plan: Plan, target: Path, args, version: str) -> None:
    plan.write(target / "AGENTS.md", build_agents(version, args.minimal, args.name))
    plan.write(target / "CLAUDE.md", build_claude())
    roadmap = "" if args.minimal else build_roadmap(args.name)
    _m = re.search(r"^description:\s*(.+)$", roadmap, re.M)
    plan.write(target / "knowledge" / "index.md",
               build_index(version, args.minimal, args.name,
                           (_m.group(1).strip().strip('"') if _m else "")))
    plan.write(target / "knowledge" / "log.md", build_log(version))
    if not args.minimal:
        plan.write(target / "knowledge" / "roadmap.md", roadmap)
        # `_changes/` la ignora el linter; el `.gitkeep` la hace sobrevivir un clone.
        plan.write(target / "knowledge" / "_changes" / ".gitkeep", "")
    # Va SIEMPRE, también en --minimal: el perfil que dice "andá directo al código" es
    # justo el que más necesita saber con qué se comprueba que el código anda.
    plan.write(target / "knowledge" / "checks.md", build_checks())
    install_machinery(plan, target, version=version, minimal=args.minimal, no_claude=args.no_claude,
                      want_ci=not args.no_ci, want_hook=not args.no_hook)


def restamp_kit_version(plan: Plan, index: Path, version: str) -> str | None:
    """Reemplaza `kit_version` en el frontmatter. Devuelve la versión anterior."""
    text = index.read_text(encoding="utf-8")
    m = re.search(r"^kit_version:\s*(.+)$", text, re.M)
    old = m.group(1).strip().strip("\"'") if m else None
    if m:
        new = re.sub(r"^kit_version:\s*.+$", f'kit_version: "{version}"', text,
                     count=1, flags=re.M)
    else:
        # Sin la clave no hay de dónde saber con qué revisión nació: se siembra ahora.
        new = re.sub(r"^---\s*$", f'---\nkit_version: "{version}"', text, count=1, flags=re.M)
    plan.write(index, new)
    return old


def append_log_line(plan: Plan, log: Path, line: str) -> None:
    """Suma una línea bajo la fecha de hoy (más nuevo primero, como manda el formato)."""
    if not log.is_file():
        plan.skip(f"{log.name} (el repo no lo mantiene)")
        return
    text = log.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    if f"## {today}" in text:
        new = text.replace(f"## {today}\n", f"## {today}\n{line}\n", 1)
    elif "# Update Log" in text:
        new = text.replace("# Update Log\n", f"# Update Log\n\n## {today}\n{line}\n", 1)
    else:
        new = f"## {today}\n{line}\n\n" + text
    plan.write(log, new)


def install_upgrade(plan: Plan, target: Path, args, version: str) -> str | None:
    index = target / "knowledge" / "index.md"
    # El nivel de instalación se DETECTA, no se asume: meterle la capa de futuro a un repo
    # que la declinó sería decidir por el usuario (`reference/upgrading.md` §2).
    minimal = args.minimal or not (target / "knowledge" / "roadmap.md").is_file()
    no_claude = args.no_claude or (target / "docs" / "okf").is_dir()
    install_machinery(
        plan, target, version=version, minimal=minimal, no_claude=no_claude,
        # En upgrade sí se respeta lo que el usuario haya editado: la maquinaria es del kit,
        # pero si alguien la tocó, pisarla en silencio es la misma pérdida de datos que la
        # 0.7.4 arregló para el entrypoint, un nivel más abajo.
        respect_edits=True,
        want_ci=not args.no_ci and (target / ".github" / "workflows" / "okf.yml").is_file(),
        # Un pre-commit que no es nuestro no se pisa: puede ser del usuario.
        want_hook=not args.no_hook and _hook_is_ours(target),
    )
    # El contrato TAMBIÉN se actualiza: si no, cada repo se queda para siempre con el texto
    # del día que se instaló y ninguna mejora del kit le llega nunca.
    agents = target / "AGENTS.md"
    if agents.is_file() and _is_kit_entrypoint(agents):
        installed = agents.read_text(encoding="utf-8")
        unsaved = _uncommitted(target, ["AGENTS.md"])
        if unsaved:
            print("okf_install: AGENTS.md tiene cambios sin commitear, así que NO lo toco "
                  "(commitealo y volvé a correr esto para actualizarlo).", file=sys.stderr)
        elif unsaved is None:
            print("okf_install: el destino no es un repo git, así que NO toco el AGENTS.md "
                  "(sin git no hay forma de devolvértelo si algo sale mal).", file=sys.stderr)
        else:
            new, replaced, abort = upgrade_contract(installed, version, minimal)
            if abort:
                print(f"okf_install: no actualizo el AGENTS.md — {abort}", file=sys.stderr)
            elif replaced:
                plan.write(agents, new)
                print(f"  contrato: actualizadas {len(replaced)} sección(es) del kit "
                      f"({', '.join(s.replace('## ','') for s in replaced)}); "
                      "tus reglas duras y capas no autoritativas quedaron intactas")

    old = restamp_kit_version(plan, index, version)
    append_log_line(
        plan, target / "knowledge" / "log.md",
        f"* **Update**: material instalado del kit OKF actualizado "
        f"{f'de v{old} ' if old else ''}a v{version} (`okf_install.py --upgrade`).",
    )
    return old


# Una frase que el contrato instalado SIEMPRE trae y que nadie escribiría por su cuenta.
_KIT_ENTRYPOINT_MARK = "Empezá por [`knowledge/index.md`](knowledge/index.md)"


def _is_kit_entrypoint(path: Path) -> bool:
    """¿Este AGENTS.md/CLAUDE.md lo escribió el kit? El shim CLAUDE.md es `@AGENTS.md`.

    Se compara **sin el comentario de cabecera**: hasta esta versión el shim se copiaba
    crudo, así que en todo repo instalado con un kit anterior el `CLAUDE.md` trae adentro el
    comentario de template. Comparando el texto literal, esos repos quedaban clasificados
    como "escrito a mano" y el instalador los mandaba a migrar su propio shim.
    """
    txt = path.read_text(encoding="utf-8", errors="replace")
    return (_KIT_ENTRYPOINT_MARK in txt
            or strip_header_comment(txt).strip() == "@AGENTS.md")


def _uncommitted(target: Path, rels: list[str]) -> list[str] | None:
    """Cuáles de `rels` git NO puede devolver. `None` si el destino no es un repo git."""
    if subprocess.run(["git", "-C", str(target), "rev-parse", "--git-dir"],
                      capture_output=True).returncode != 0:
        return None
    r = subprocess.run(["git", "-C", str(target), "status", "--porcelain", "--", *rels],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return list(rels)          # ante la duda, tratarlo como no recuperable
    return sorted({ln[3:].strip().strip('"') for ln in r.stdout.splitlines() if ln.strip()})


def _hook_is_ours(target: Path) -> bool:
    hook = target / ".git" / "hooks" / "pre-commit"
    if not hook.is_file():
        return False
    return "OKF" in hook.read_text(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------ verificación y reporte
def lint(target: Path) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(target / "scripts" / "okf_lint.py"), "knowledge", "--strict"],
        cwd=target, capture_output=True, text=True,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def pending_placeholders(target: Path) -> list[str]:
    """Los `{{...}}` que quedaron: es exactamente el trabajo de criterio que falta."""
    out = []
    for rel in ("AGENTS.md", "knowledge/index.md", "knowledge/log.md", "knowledge/roadmap.md"):
        p = target / rel
        if p.is_file() and "{{" in p.read_text(encoding="utf-8", errors="replace"):
            out.append(rel)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        prog="okf_install.py",
        description="Instala (o actualiza) el material del kit OKF en un repo destino.",
    )
    ap.add_argument("target", help="ruta del repo DESTINO (nunca el kit)")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="codigo",
                    help="dominio del repo: define qué carpetas conviene sembrar (default: codigo)")
    ap.add_argument("--name", help="nombre del proyecto, para {{PROJECT_NAME}}")
    ap.add_argument("--minimal", action="store_true",
                    help="sin capa de futuro (ni roadmap.md, ni _changes/, ni okf-plan)")
    ap.add_argument("--no-claude", action="store_true",
                    help="los procedimientos van a docs/okf/ en vez de .claude/skills/")
    ap.add_argument("--no-ci", action="store_true", help="no instalar el workflow de CI")
    ap.add_argument("--no-hook", action="store_true", help="no instalar el git hook")
    ap.add_argument("--upgrade", action="store_true",
                    help="reemplazar solo la maquinaria (no toca AGENTS.md ni el bundle)")
    ap.add_argument("--force", action="store_true",
                    help="reemplazar un AGENTS.md/CLAUDE.md escrito a mano (commiteá antes)")
    ap.add_argument("--dry-run", action="store_true", help="mostrar el plan, no escribir nada")
    args = ap.parse_args(argv[1:])

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"okf_install: el destino '{target}' no existe o no es un directorio",
              file=sys.stderr)
        return 2
    # Igualdad exacta dejaba pasar `okf-kit/reference` (y un kit clonado dentro del repo).
    if target == KIT or KIT in target.parents or target in KIT.parents:
        print("okf_install: el destino no puede ser el kit, ni estar anidado con él — el kit "
              "tiene su propio knowledge/ dogfood. Apuntá al repo del usuario.", file=sys.stderr)
        return 2

    version = kit_version()

    # El `AGENTS.md`/`CLAUDE.md` de un repo con vida propia es contenido del USUARIO —
    # reglas, procedimientos, dónde están los secretos— y pisarlo es pérdida de datos
    # irreversible si no estaba commiteado. Para ese repo existe `okf-migrate`, que
    # consolida en vez de reemplazar.
    if not args.upgrade:
        _theirs = [f for f in ("AGENTS.md", "CLAUDE.md")
                   if (target / f).is_file() and not _is_kit_entrypoint(target / f)]
        # Con --force el reemplazo es deliberado, pero solo es *recuperable* si git lo tiene:
        # "commiteá antes" es un paso que puede fallar en silencio (un hook que aborta, un
        # `git add` que no incluyó el archivo) y el usuario se entera cuando ya no está.
        if _theirs and args.force:
            _unsaved = _uncommitted(target, _theirs)
            if _unsaved is None:
                print(f"okf_install: ojo — '{target}' no es un repo git, así que "
                      f"{' y '.join(_theirs)} se reemplaza SIN forma de recuperarlo. "
                      "Copiá el archivo afuera antes si te importa.", file=sys.stderr)
            elif _unsaved:
                print(f"okf_install: --force reemplazaría {' y '.join(_unsaved)}, que "
                      "**no está commiteado**: se perdería sin forma de recuperarlo.\n"
                      f"  → commitealo primero (verificá que el commit haya entrado: un hook "
                      f"que falla lo aborta en silencio), o\n"
                      "  → copiá el archivo afuera del repo y volvé a intentar.",
                      file=sys.stderr)
                return 2
        if _theirs and not args.force:
            print(f"okf_install: '{target}' ya tiene {' y '.join(_theirs)} escrito a mano y "
                  "NO se pisa.\n"
                  "  → ese repo es el caso de `okf-migrate`: consolida lo que ya tenés en un "
                  "bundle OKF en vez de reemplazarlo.\n"
                  "  → si vas por tu cuenta, la secuencia completa es:\n"
                  f"      1) commiteá (o copiá afuera) {' y '.join(_theirs)} — el paso 2 lo "
                  "reemplaza\n"
                  "      2) volvé a correr esto con --force (tu pre-commit NO se pisa ni así)\n"
                  "      3) re-mergeá lo tuyo: las reglas duras al AGENTS.md nuevo, el resto "
                  "al bundle\n"
                  "    Saltear el paso 3 pierde tu contexto aunque el archivo esté commiteado.",
                  file=sys.stderr)
            return 2

    bundle_exists = (target / "knowledge" / "index.md").is_file()
    if bundle_exists and not args.upgrade:
        print(f"okf_install: '{target}' ya tiene knowledge/index.md y no se pisa.\n"
              f"  → para subir la maquinaria a v{version}: agregá --upgrade\n"
              f"  → para mantener el CONTENIDO del bundle: el skill okf-update",
              file=sys.stderr)
        return 2
    if args.upgrade and not bundle_exists:
        print(f"okf_install: '{target}' no tiene knowledge/index.md, no hay nada que "
              "actualizar — corré sin --upgrade para instalar de cero.", file=sys.stderr)
        return 2

    plan = Plan(args.dry_run)
    old = install_upgrade(plan, target, args, version) if args.upgrade else \
        install_fresh(plan, target, args, version)

    print(f"okf-kit v{version} → {target}"
          f"{'  [DRY-RUN: no se escribió nada]' if args.dry_run else ''}\n")
    for a in plan.actions:
        print(f"  {a}")

    if args.dry_run:
        return 0

    code, out = lint(target)
    print(f"\nlinter (--strict) sobre knowledge/:\n{out}")
    if code != 0:
        print("\n⚠ el linter NO pasó sobre lo instalado — los archivos YA se escribieron.\n"
              "  Es un bug del kit, no del repo destino: reportalo.")

    print("\n" + "─" * 72)
    if args.upgrade:
        print(f"MAQUINARIA ACTUALIZADA{f' (venía de v{old})' if old else ''}. Falta lo que "
              "requiere criterio:\n"
              f"  1. Leer el CHANGELOG del kit {f'desde v{old} ' if old else ''}hasta "
              f"v{version} — dice si alguna regla cambió de forma.\n"
              "  2. Mergear el AGENTS.md a mano: se conservan el título, el stack, las reglas "
              "duras propias\n     y los {{placeholders}} completados; se reemplazan las "
              "secciones 1, 2, 3 y Procedimientos.\n"
              "     Mostrale al usuario qué conservás y qué reemplazás ANTES de escribir.\n"
              "     Procedimiento completo: reference/upgrading.md")
    else:
        folders = " ".join(PROFILES[args.profile])
        print(("ESQUELETO INSTALADO Y CONFORME" if code == 0 else "ESQUELETO INSTALADO")
              + ". Falta lo que requiere criterio (el valor real):\n"
              f"  1. Sembrar los conceptos — el *por qué* que el código no dice. Perfil "
              f"'{args.profile}':\n     {folders}\n"
              "     Creá cada carpeta con su index.md recién cuando tenga un concepto real "
              "adentro.\n"
              "  2. Sumar cada carpeta al `# Subdirectories` de knowledge/index.md.\n"
              "  3. Completar los {{placeholders}} que quedaron"
              + (f": {', '.join(pending_placeholders(target))}" if pending_placeholders(target)
                 else " (ninguno)") + "\n"
              "     En AGENTS.md: nombre/stack, reglas duras del proyecto y las capas NO "
              "autoritativas.\n"
              "     Preguntale al usuario lo que no se deduce de la fuente; no lo inventes.\n"
              "  4. Verificar: python3 scripts/okf_lint.py knowledge   (y el skill okf-verify)")
    if code != 0:
        print("\n⚠ el linter NO pasó sobre lo instalado — los archivos YA se escribieron.")
    return 1 if code else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
