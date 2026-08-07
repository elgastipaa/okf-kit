#!/usr/bin/env python3
"""okf_selfcheck_test.py — ¿el gate FALLA cuando tiene que fallar?

Un assert que nunca se probó rompiendo lo que dice cuidar es decoración: pasa siempre y
da una falsa sensación de red. Una revisión en frío del `okf_selfcheck.py` encontró
**siete** asserts así (pasaban sobre archivos borrados, se satisfacían desde comentarios
HTML que la instalación elimina, o se contentaban con dos substrings sueltos en un texto
que NEGABA la regla) más cinco que fallaban ante redacción legítima.

Este script inyecta cada rotura sobre una COPIA del kit y verifica el veredicto. Es
kit-only (vive en `scripts/`, no se instala en repos destino) y no toca el repo real.

**Al agregar un assert al selfcheck, agregá acá su caso** — la rotura concreta que
debería cazar, y, si el assert puede dar falso positivo, el caso legítimo que NO debe
romperlo. Es la diferencia entre una red y un adorno.

Uso:  python3 scripts/okf_selfcheck_test.py
Exit: 0 si todos los casos se comportan como corresponde, 1 si alguno no.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
CASES: list[tuple[str, bool, object]] = []


def case(name: str, expect_fail: bool):
    """expect_fail=True → el gate DEBE fallar. False → redacción legítima, debe pasar."""
    def deco(fn):
        CASES.append((name, expect_fail, fn))
        return fn
    return deco


def edit(d: Path, rel: str, old: str, new: str) -> None:
    p = d / rel
    t = p.read_text(encoding="utf-8")
    if old not in t:
        raise AssertionError(f"el caso no aplica: no encontré en {rel}: {old[:60]!r}")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


def append(d: Path, rel: str, text: str) -> None:
    p = d / rel
    p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")


# ---- archivos ausentes: el modo de falla más traicionero (el assert "pasa" sobre nada)
@case("archivo instalado borrado", True)
def _(d): (d / "templates/skills/okf-plan/SKILL.md").unlink()


# ---- comentarios HTML: la instalación los borra, así que no cuentan como contenido
@case("kit_version solo en un comentario HTML", True)
def _(d):
    # se lo saca del frontmatter (lo que se instala) dejándolo en el comentario (lo que se borra)
    p = d / "templates/knowledge/index.md"
    t = p.read_text(encoding="utf-8")
    body = re.sub(r"^kit_version:.*\n", "", t[t.index("-->"):], flags=re.M)
    p.write_text(t[:t.index("-->")] + body, encoding="utf-8")


@case("`-->` dentro del cuerpo de un comentario (markup inválido)", True)
def _(d):
    edit(d, "templates/AGENTS.md", "  - Si no instalaste",
         "  - Se escriben <!-- OKF:x --> así.\n  - Si no instalaste")


# ---- el valor real, en el lugar real
@case("kit_version en el cuerpo, no en el frontmatter", True)
def _(d):
    p = d / "knowledge/index.md"
    t = p.read_text(encoding="utf-8")
    ver = re.search(r'kit_version:\s*"?([^"\n]+)', t).group(1)
    p.write_text(re.sub(r'^kit_version:.*\n', "", t, flags=re.M)
                 + f'\n\nEjemplo:\nkit_version: "{ver}"\n', encoding="utf-8")


# ---- procedimientos: un paso borrado tiene que notarse aunque el token viva en otra sección
@case("el keep-alive pierde el paso de indexar el concepto", True)
def _(d):
    # Antes este caso apuntaba al paso de `log.md`; desde la 0.7.6 log.md es opt-in y salió
    # del keep-alive, así que el caso se reapuntó a un paso que SIGUE siendo obligatorio.
    # Un caso que prueba algo que ya no es regla no prueba nada.
    edit(d, "templates/skills/okf-update/SKILL.md",
         "4. **Actualizá el `index.md`**", "4. **Paso removido**")


# ---- la rama normativa: presencia de tokens ≠ afirmar la regla
@case("un texto que NIEGA la rama normativa", True)
def _(d):
    (d / "templates/skills/okf-verify/SKILL.md").write_text(
        "---\nname: okf-verify\n---\nNada es normativo y nunca hay que supersede nada.\n",
        encoding="utf-8")


# ---- marcadores de la capa de futuro
@case("la cabecera cita marcadores y se borra un par real", True)
def _(d):
    edit(d, "templates/AGENTS.md", "  andamiaje son las",
         "  ej: <!-- OKF:future-layer:start --> y <!-- OKF:future-layer:end -->\n  andamiaje son las")
    edit(d, "templates/AGENTS.md",
         "<!-- OKF:future-layer:start -->\n- **Planificar** trabajo futuro y cerrar cambios:"
         " `okf-plan`\n<!-- OKF:future-layer:end -->\n", "")


@case("un par de marcadores de más, sin actualizar la prosa", True)
def _(d):
    edit(d, "templates/AGENTS.md", "## Procedimientos",
         "<!-- OKF:future-layer:start -->\nextra\n<!-- OKF:future-layer:end -->\n\n## Procedimientos")


@case("el disparador de scope creep pierde el chequeo de existencia", True)
def _(d):
    edit(d, "templates/skills/okf-plan/SKILL.md",
         "**chequeá primero si ya existe en\n   el código**; si no existe, una línea", "una línea")


@case("okf-init vuelve a rutear a okf-update ante un bundle existente", True)
def _(d):
    edit(d, "templates/skills/okf-init/SKILL.md", "seguí `reference/upgrading.md`", "seguí `okf-update`")


@case("el Nivel 2 pierde su método", True)
def _(d):
    edit(d, "templates/skills/okf-verify/SKILL.md",
         "buscá la contradicción, no la confirmación", "revisá que todo esté bien")


@case("la auditoría del rumbo deja de limitarse a \"Ahora\"", True)
def _(d):
    edit(d, "reference/verification.md", "**Del rumbo, solo la sección \"Ahora\".**", "Auditá el rumbo entero.")


@case("la instalación deja de copiar okf_stale.py", True)
def _(d):
    edit(d, "reference/manual-install.md", "y **`okf_stale.py`** (rankea dónde buscar",
         "y ~~okf_stale~~ (rankea dónde buscar")


@case("el camino manual pierde el conteo de marcadores", True)
def _(d):
    edit(d, "reference/manual-install.md", "las 8 líneas de marcadores", "los marcadores")


@case("el instalador siembra dos placeholders para la misma frase", True)
def _(d):
    # index y roadmap describiendo lo mismo con textos distintos: divergen por construcción,
    # y el linter (que ahora cruza la entrada del index con la description) lo caza.
    edit(d, "scripts/okf_install.py",
         'f"* [Rumbo de {name or \'{{proyecto}}\'}](roadmap.md) - {roadmap_desc}\\n"',
         'f"* [Rumbo de {name or \'{{proyecto}}\'}](roadmap.md) - {{completá la description}}\\n"')


@case("término de la capa huérfano fuera de los marcadores", True)
def _(d):
    edit(d, "templates/AGENTS.md", "## Reglas duras",
         "Acordate del harvest al cerrar.\n\n## Reglas duras")


# ---- autosuficiencia del material instalado
@case("un skill cita templates/AGENTS.md", True)
def _(d): append(d, "templates/skills/okf-plan/SKILL.md", "\nVer templates/AGENTS.md.\n")


@case("un skill cita una ruta del kit con prefijo okf-kit/", True)
def _(d): append(d, "templates/skills/okf-verify/SKILL.md", "\nVer okf-kit/reference/verification.md.\n")


@case("un template de concepto cita reference/profiles.md", True)
def _(d): append(d, "templates/knowledge/_concept.md", "\nVer reference/profiles.md.\n")


# ---- constantes duplicadas entre el código y la prosa
@case("el presupuesto del script deja de coincidir con el declarado", True)
def _(d): edit(d, "scripts/okf_selfcheck.py", "BUDGET = 7000", "BUDGET = 8000")


# ---- cobertura que se encoge en silencio
@case("el scan de referencias se queda sin nada que verificar", True)
def _(d):
    for md in d.rglob("*.md"):
        t = md.read_text(encoding="utf-8", errors="replace")
        if "reference/" in t:
            md.write_text(t.replace("reference/", "ref-x/"), encoding="utf-8")


# ---- el instalador: lo que se verifica es la SALIDA, así que se rompe el que la produce
@case("el instalador no existe", True)
def _(d): (d / "scripts/okf_install.py").unlink()


@case("el instalador deja marcadores en el contrato instalado", True)
def _(d):
    edit(d, "scripts/okf_install.py", '    text = _MARKER_LINE_RE.sub("", text)\n', "")
    edit(d, "scripts/okf_install.py",
         '    assert "OKF:future-layer" not in text, "quedó un marcador en el contrato instalado"\n', "")


@case("el instalador no sella {{KIT_VERSION}}", True)
def _(d):
    edit(d, "scripts/okf_install.py",
         '    text = text.replace("{{KIT_VERSION}}", version)\n'
         '    # El comentario YAML de la línea de kit_version es instrucción de instalación.',
         '    # El comentario YAML de la línea de kit_version es instrucción de instalación.')


@case("la instalación mínima no recorta la capa de futuro", True)
def _(d):
    edit(d, "scripts/okf_install.py",
         "    if minimal:\n        text = _MARKED_BLOCK_RE.sub(\"\", text)",
         "    if False:\n        text = _MARKED_BLOCK_RE.sub(\"\", text)")


@case("el instalador produce un bundle que no lintea (link roto el día uno)", True)
def _(d):
    edit(d, "scripts/okf_install.py",
         '"`* [nombre](nombre/index.md) - qué hay en esta carpeta`}}\\n"',
         '"* [nombre](nombre/index.md) - qué hay en esta carpeta}}\\n"')


@case("la instalación mínima igual instala okf-plan", True)
def _(d):
    edit(d, "scripts/okf_install.py",
         "skills = list(SKILLS_ALWAYS) + ([] if minimal else [SKILL_FUTURE])",
         "skills = list(SKILLS_ALWAYS) + [SKILL_FUTURE]")


# ---- una verdad, un lugar: el skill delega, no re-statea
@case("okf-init deja de nombrar al instalador", True)
def _(d):
    edit(d, "templates/skills/okf-init/SKILL.md",
         "python3 <ruta-al-kit>/scripts/okf_install.py", "copiá los archivos a mano")


@case("okf-init vuelve a describir la plomería en prosa", True)
def _(d):
    append(d, "templates/skills/okf-init/SKILL.md",
           "\nAcordate de hacer `chmod +x` en el hook.\n")


# ---- pérdida de datos: lo que la pasada adversarial encontró destruyendo trabajo ajeno
@case("el instalador vuelve a pisar el AGENTS.md del usuario", True)
def _(d):
    edit(d, "scripts/okf_install.py", "        if _theirs and not args.force:",
         "        if False:")


@case("el instalador vuelve a pisar el pre-commit del usuario", True)
def _(d):
    edit(d, "scripts/okf_install.py",
         "    elif (target / \".git\" / \"hooks\" / \"pre-commit\").is_file() and not _hook_is_ours(target):",
         "    elif False:")


@case("el gate deja de probar que el linter FUNCIONA (linter vaciado)", True)
def _(d): (d / "templates/scripts/okf_lint.py").write_text("", encoding="utf-8")


@case("borrar material instalado ya no puede bajar el denominador", True)
def _(d): (d / "templates/knowledge/_decision.md").unlink()


@case("el template ofrece `confirmado` sin atarlo a declarar el hueco", True)
def _(d): edit(d, "templates/knowledge/_decision.md",
                "**Obliga a dejar la pregunta abierta**", "Podés dejar la pregunta abierta")


@case("la capa generada vuelve a existir solo en okf-init", True)
def _(d):
    p = d / "templates/skills/okf-migrate/SKILL.md"
    t = p.read_text(encoding="utf-8")
    a = t.index("## 5b. Los hechos volátiles se generan")
    b = t.index("## 6. Anti-duplicación")
    p.write_text(t[:a] + t[b:], encoding="utf-8")


@case("el instalador vuelve a sembrar un index que lista por type", True)
def _(d):
    # Se borra el bloque entero de la puerta en el instalador: cambiarle el título dejaría la
    # tabla, y lo que se paga en turnos es no tener la tabla.
    p = d / "scripts/okf_install.py"
    t = p.read_text(encoding="utf-8")
    a = t.index('    door = ("# Por dónde empezar\\n\\n"')
    b = t.index("    # La cabecera es todo lo anterior")
    p.write_text(t[:a] + '    door = ""\n' + t[b:], encoding="utf-8")


@case("okf-init deja de mandar a 1-3 archivos concretos", True)
def _(d): edit(d, "templates/skills/okf-init/SKILL.md",
                "**1-3 archivos concretos**", "**la carpeta que corresponda**")


@case("okf-init vuelve a no nombrar la capa generada", True)
def _(d):
    # Borrar solo el heading NO alcanza: el cuerpo sigue nombrando el patrón, y el assert
    # mira la sustancia y no el título. La regresión real es que el paso desaparezca.
    p = d / "templates/skills/okf-init/SKILL.md"
    t = p.read_text(encoding="utf-8")
    a = t.index("## 4. Generá los hechos volátiles")
    b = t.index("## 5. Completá lo que el instalador")
    p.write_text(t[:a] + t[b:], encoding="utf-8")


@case("el generado se pide sin su check de drift", True)
def _(d): edit(d, "templates/skills/okf-init/SKILL.md",
                "**sale con código ≠ 0 si difiere** del", "**se ve lindo** comparado con el")


@case("una referencia §N a la propia sección queda colgada", True)
def _(d): edit(d, "templates/skills/okf-init/SKILL.md", "ver §1)", "ver §9)")


@case("una referencia §N de un skill a otro queda colgada", True)
def _(d): edit(d, "templates/skills/okf-migrate/SKILL.md", "`okf-init` §1", "`okf-init` §9")


@case("el template de decisión vuelve a regalar `origen: dictado`", True)
def _(d): edit(d, "templates/knowledge/_decision.md",
                "origen: reconstruido", "origen: dictado")


@case("un template nuevo sin sus asserts (inventario corto)", True)
def _(d): (d / "templates/knowledge/_nuevo.md").write_text("---\ntype: X\n---\n", encoding="utf-8")


# ---- la auditoría no se auto-aprueba
@case("el revisor con contexto fresco no existe", True)
def _(d): (d / "templates/agents/okf-reviewer.md").unlink()


@case("el revisor pierde la consigna refutatoria", True)
def _(d):
    edit(d, "templates/agents/okf-reviewer.md",
         "**Buscá la contradicción, no la confirmación.**", "**Revisá que todo esté bien.**")


@case("el revisor puede editar lo que audita", True)
def _(d):
    edit(d, "templates/agents/okf-reviewer.md", "disallowedTools: Write, Edit, NotebookEdit", "model: sonnet")


@case("okf-verify deja de delegar los niveles que auditan trabajo propio", True)
def _(d):
    edit(d, "templates/skills/okf-verify/SKILL.md", "`okf-reviewer`, o, si tu herramienta",
         "vos mismo, o, si tu herramienta")


@case("okf-verify pierde la salida sin subagentes", True)
def _(d):
    edit(d, "templates/skills/okf-verify/SKILL.md",
         "si tu herramienta no tiene subagentes, entregale al usuario el prompt para\n> pegarlo en una CLI nueva",
         "usá el subagente y listo")


@case("el revisor cita una ruta que solo existe en el kit", True)
def _(d): append(d, "templates/agents/okf-reviewer.md", "\nVer reference/verification.md.\n")


# ---- distribución como plugin
@case("la versión del plugin deriva de VERSION", True)
def _(d): edit(d, ".claude-plugin/plugin.json", '"version": "', '"version": "9.9.9", "_v": "')


@case("el plugin apunta a un skill que no existe", True)
def _(d): edit(d, ".claude-plugin/plugin.json", "./templates/skills/okf-init", "./skills/okf-init")


@case("el plugin ship**ea los procedimientos que van instalados en el repo", True)
def _(d): edit(d, ".claude-plugin/plugin.json", '"./templates/skills/okf-migrate"',
               '"./templates/skills/okf-migrate",\n    "./templates/skills/okf-update"')


@case("el marketplace apunta a un plugin que no está ahí", True)
def _(d): edit(d, ".claude-plugin/marketplace.json", '"source": "./"', '"source": "./plugins/okf"')


@case("un manifiesto del plugin con JSON roto", True)
def _(d): edit(d, ".claude-plugin/plugin.json", '{\n  "name"', '{\n  "name",')


# ---- FALSOS POSITIVOS: redacción legítima que NO debe romper el gate
@case("el plugin declara metadata extra (keywords, homepage)", False)
def _(d): edit(d, ".claude-plugin/plugin.json", '"license": "Apache-2.0",',
               '"license": "Apache-2.0",\n  "homepage": "https://example.com",')


@case("okf-init menciona el hook sin describir su instalación", False)
def _(d):
    append(d, "templates/skills/okf-init/SKILL.md",
           "\nEl git hook queda instalado y corre con cualquier IA.\n")


@case("el instalador escribe un archivo extra que no es del bundle", False)
def _(d):
    edit(d, "scripts/okf_install.py",
         "    plan.write(target / \"CLAUDE.md\", build_claude())",
         "    plan.write(target / \"CLAUDE.md\", build_claude())\n"
         "    plan.write(target / \".editorconfig\", \"root = true\\n\")")


# ---- el contrato tiene que poder actualizarse sin perder lo del usuario
# ---- los chequeos del repo: el único concepto que contesta "¿esto anda?"
@case("la instalación deja de sembrar checks.md", True)
def _(d):
    edit(d, "scripts/okf_install.py",
         '    plan.write(target / "knowledge" / "checks.md", build_checks())', "    pass")


@case("el contrato siembra checks.md pero no manda a correrlo", True)
def _(d):
    # Un archivo sembrado y no ruteado es un documento que nadie abre: el agujero de la
    # lente C con un archivo más, no con un archivo menos.
    edit(d, "templates/AGENTS.md", "**Si tocaste código:** corré los chequeos de",
         "**Nota:** existe un archivo de chequeos en")


@case("okf-init deja de entregarle las preguntas abiertas al usuario", True)
def _(d):
    # El paso que el kit NO hizo cuando se aplico a un repo real. Sin el, lo que el agente
    # no pudo averiguar se reconstruye en silencio y queda escrito como un hecho.
    # La regresion realista no es cambiarle el titulo: es que el paso desaparezca en una
    # reescritura del skill. Cambiar solo el heading deja el cuerpo y el assert lo ve igual.
    f = d / "templates/skills/okf-init/SKILL.md"
    txt = f.read_text(encoding="utf-8")
    f.write_text(txt[:txt.index("## 7. Entregá las PREGUNTAS ABIERTAS")], encoding="utf-8")


@case("el rename de perfil se hace sin alias (rompe el CLI de quien ya lo usó)", True)
def _(d):
    edit(d, "scripts/okf_install.py", 'PROFILE_ALIASES = {"wiki": "concepto"}',
         "PROFILE_ALIASES = {}")


@case("log.md vuelve a sembrarse siempre", True)
def _(d):
    edit(d, "scripts/okf_install.py", "    if args.with_log:", "    if True:")


@case("una description de skill se infla y nadie la mide", True)
def _(d):
    # El canal que estaba invisible: las `description:` van al system prompt en CADA turno,
    # y el presupuesto del contrato no las contaba. Inflar una tiene que doler.
    edit(d, "templates/skills/okf-verify/SKILL.md", "description: >",
         "description: >\n  " + ("relleno que nadie midio. " * 40))


@case("--upgrade pisa la maquinaria que el usuario editó", True)
def _(d):
    # La forma ingenua: reemplazar siempre. Se lleva puestas las ediciones del usuario
    # sobre skills, linter o hook, y nunca se entera.
    edit(d, "scripts/okf_install.py",
         "        if respect_edits:",
         "        if False:")


@case("--upgrade regenera el contrato entero y borra lo del usuario", True)
def _(d):
    # La forma ingenua de "actualizar el contrato": pisarlo con el template. Se lleva puestas
    # las reglas duras, las capas no autoritativas y cualquier sección propia del usuario.
    edit(d, "scripts/okf_install.py",
         "            new, replaced, abort = upgrade_contract(installed, version, minimal)",
         "            new, replaced, abort = build_agents(version, minimal, None), ['todo'], None")


@case("--upgrade no toca el contrato, así que la mejora nunca llega", True)
def _(d):
    # El bug que motivó todo esto: --upgrade actualizaba la maquinaria y dejaba el contrato
    # congelado en el texto del día que se instaló.
    edit(d, "scripts/okf_install.py",
         "    if agents.is_file() and _is_kit_entrypoint(agents):",
         "    if False:")


@case("--force borra el entrypoint del usuario aunque git no lo tenga", True)
def _(d):
    # El escenario que lo motivó: el "commiteá antes" del mensaje de error puede fallar en
    # silencio (un hook que aborta el commit) y --force ejecuta igual, sin recuperación.
    edit(d, "scripts/okf_install.py",
         "        if _theirs and args.force:",
         "        if False and args.force:")


# ---- andamiaje de cabecera en el material instalado
@case("el shim CLAUDE.md se instala crudo, con su comentario de template", True)
def _(d):
    # Fue un bug real: `plan.copy` en vez de `plan.write(build_claude())` mandaba al repo
    # destino el comentario que explica cómo instalar el kit, y se pagaba en cada turno.
    edit(d, "scripts/okf_install.py",
         "    plan.write(target / \"CLAUDE.md\", build_claude())",
         "    plan.copy(KIT / \"templates\" / \"CLAUDE.md\", target / \"CLAUDE.md\")")


@case("un template instalado conserva su comentario de cabecera", True)
def _(d):
    # La regla es general, no sobre CLAUDE.md: cualquier archivo instalado que EMPIECE con
    # un comentario HTML es andamiaje. Acá se rompe por otro archivo distinto.
    edit(d, "scripts/okf_install.py",
         "    text = strip_header_comment(read_template(\"AGENTS.md\"))",
         "    text = read_template(\"AGENTS.md\")")


@case("un concepto del bundle usa un comentario HTML en el medio, no en la cabecera", False)
def _(d):
    # Redacción legítima: el assert mira solo el ARRANQUE del archivo. Un comentario más
    # abajo (una nota para el que edita) no es andamiaje de instalación.
    append(d, "templates/knowledge/log.md", "\n<!-- nota al pie para quien edite esto -->\n")


@case("kit_version con un comentario YAML al lado", False)
def _(d):
    p = d / "knowledge/index.md"
    t = p.read_text(encoding="utf-8")
    p.write_text(re.sub(r'^(kit_version:\s*)"([^"]+)"', r'\1\2  # de VERSION', t, flags=re.M),
                 encoding="utf-8")


@case("uso corriente de la palabra 'rumbo' en el contrato", False)
def _(d):
    edit(d, "templates/AGENTS.md", "## Reglas duras",
         "Si el usuario cambia el rumbo de la tarea, preguntá.\n\n## Reglas duras")


@case("un skill menciona el CHANGELOG.md del repo destino", False)
def _(d): append(d, "templates/skills/okf-update/SKILL.md",
                 "\nSi tu repo mantiene un CHANGELOG.md, actualizalo.\n")


@case("el bloque del reporte usa el fence ```md en las dos copias", False)
def _(d):
    for rel in ("reference/verification.md", "templates/skills/okf-verify/SKILL.md"):
        edit(d, rel, "```markdown\n# OKF Verification Report", "```md\n# OKF Verification Report")


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="okf-gate-test-"))
    print(f"{'caso':<58} {'espera':<7} {'real':<7} veredicto")
    bad = 0
    try:
        for name, expect_fail, fn in CASES:
            d = root / re.sub(r"\W+", "_", name)[:40]
            shutil.copytree(KIT, d, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            try:
                fn(d)
            except AssertionError as e:
                print(f"{name:<58} {'—':<7} {'—':<7} SETUP ROTO: {e}")
                bad += 1
                continue
            code = subprocess.run([sys.executable, "scripts/okf_selfcheck.py"], cwd=d,
                                  capture_output=True, text=True).returncode
            real_fail = code != 0
            ok = real_fail == expect_fail
            bad += not ok
            print(f"{name:<58} {'FAIL' if expect_fail else 'pasa':<7} "
                  f"{'FAIL' if real_fail else 'pasa':<7} {'ok' if ok else '<<< MAL'}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"\nokf_selfcheck_test: {len(CASES) - bad}/{len(CASES)} casos se comportan como corresponde")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
