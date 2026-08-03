#!/usr/bin/env python3
"""okf_selfcheck.py — meta-linter del PROPIO kit OKF (herramienta de desarrollo).

NO se instala en repos destino (vive en `scripts/`, no en `templates/`).
Valida la consistencia INTERNA del kit — lo que las revisiones en frío encontraron que
nadie chequeaba y por eso los bugs aparecían reactivamente:

- el linter pasa limpio sobre el bundle dogfood `knowledge/`;
- `kit_version` está sembrado donde corresponde (no se "cae" en ejemplos/skills);
- el keep-alive y la capa de futuro coinciden entre el contrato y los skills;
- la rama normativa de la regla de autoridad no se cae de donde se afirma;
- el contrato entra en su presupuesto y la instalación mínima no queda coja;
- el material instalado no cita rutas que solo existen en el kit;
- toda referencia `reference/*.md` resuelve.

REGLAS DE DISEÑO de este archivo (violarlas produce un gate que miente, que es peor
que no tener gate — una revisión en frío encontró siete asserts así):

1. **Un archivo que falta hace FALLAR, no pasar.** Leer con `read_required`; nunca
   evaluar una condición sobre `""`.
2. **Los comentarios HTML no cuentan como contenido**: la instalación los borra. Todo
   chequeo de contenido pasa primero por `strip_comments`.
3. **El mensaje del assert no puede afirmar más de lo que el código mide.** Si el
   chequeo es "estos 5 literales", el mensaje dice literales, no "no menciona X".
4. **El nombre del assert es estable**; el detalle del fallo va aparte (CI diffeable).
5. Todo assert nuevo se acompaña de la rotura que debería cazar, probada a mano.

Uso:  python3 scripts/okf_selfcheck.py
Exit: 0 si todo pasa, 1 si hay algún FAIL.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
results: list[tuple[bool, str, str]] = []

# El material que se COPIA al repo destino. `okf-init`/`okf-migrate` quedan afuera a
# propósito: corren en el bootstrap, con el kit todavía en disco.
# Inventario LITERAL, no un glob de lo que existe: con el glob, borrar un archivo instalado
# le borraba sus asserts y el gate seguía diciendo OK con un denominador más chico (104 → 102).
# Un archivo que falta tiene que FALLAR, no desaparecer del reporte (regla de diseño 1).
INSTALLED = [
    "templates/AGENTS.md",
    "templates/CLAUDE.md",
    "templates/agents/okf-reviewer.md",
    *(f"templates/knowledge/{n}.md" for n in (
        "_change", "_checks", "_concept", "_decision", "_generated", "_glossary",
        "_reference", "_roadmap", "_runbook", "index", "log")),
    *(f"templates/skills/{s}/SKILL.md" for s in ("okf-update", "okf-verify", "okf-plan")),
]

# Y que el inventario no se quede corto en silencio si mañana se agrega un template.
_on_disk = sorted(
    p.relative_to(KIT).as_posix()
    for p in [
        *(KIT / "templates" / "knowledge").glob("*.md"),
        *(KIT / "templates" / "agents").glob("*.md"),
        *(KIT / "templates" / "skills").glob("*/SKILL.md"),
        KIT / "templates" / "AGENTS.md", KIT / "templates" / "CLAUDE.md",
    ] if p.is_file()
)
_uninventoried = [f for f in _on_disk
                  if f not in INSTALLED and "okf-init" not in f and "okf-migrate" not in f]


def check(ok: bool, name: str, detail: str = "") -> None:
    results.append((bool(ok), name, detail))


def read(rel: str) -> str:
    """Contenido, o '' si no existe. Solo para chequeos donde ausente == vacío."""
    p = KIT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def read_required(rel: str) -> str | None:
    """Contenido, o None si el archivo NO existe — el consumidor debe fallar, no pasar."""
    p = KIT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None


# Un comentario HTML termina en el PRIMER `-->` que no esté dentro del propio comentario.
# El `.*?` ingenuo se trunca cuando el cuerpo del comentario cita un `-->` (bug real de
# 0.6.0: falseó la medición del presupuesto y tres mensajes de assert).
_COMMENT_RE = re.compile(r"<!--(?:(?!-->).)*-->", re.S)


def strip_comments(text: str) -> str:
    return _COMMENT_RE.sub("", text)


def frontmatter(text: str) -> str:
    """El bloque de frontmatter, o '' si no hay. Evita confundir el cuerpo con el header."""
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    return m.group(1) if m else ""


def numbered_steps(text: str) -> str:
    """Solo los pasos numerados (`1. …`) y sus continuaciones: donde vive un procedimiento.

    Evita que un token suelto en cualquier párrafo dé por presente un paso que se borró.
    """
    out, inside = [], False
    for ln in text.splitlines():
        if re.match(r"^\s*\d+\.\s", ln):
            inside = True
        elif inside and ln.strip() and not ln.startswith((" ", "\t")):
            inside = False
        if inside:
            out.append(ln)
    return "\n".join(out)


def near(text: str, *tokens: str, window: int = 400) -> bool:
    """¿Los tokens coocurren en una misma ventana? Presencia suelta no es afirmación.

    Colapsa los espacios primero: en markdown envuelto a 90 columnas una frase se parte en
    dos líneas, y buscar el literal fallaría por un salto de línea — un assert que falla por
    el formato del texto es un impuesto, no una red.
    """
    text = re.sub(r"\s+", " ", text)
    first, rest = tokens[0], tokens[1:]
    for m in re.finditer(re.escape(first), text):
        chunk = text[max(0, m.start() - window): m.start() + window]
        if all(t in chunk for t in rest):
            return True
    return False


# ---------------------------------------------------------------- 0. Los archivos existen
# Sin esto, cualquier assert de contenido sobre un archivo borrado "pasa" con el texto vacío.
_missing = [rel for rel in INSTALLED if not (KIT / rel).is_file()]
for rel in ("templates/AGENTS.md", "templates/skills/okf-plan/SKILL.md",
            "templates/skills/okf-update/SKILL.md", "templates/skills/okf-verify/SKILL.md",
            "templates/knowledge/_change.md", "templates/knowledge/_roadmap.md",
            "templates/knowledge/_checks.md",
            "reference/verification.md", "OKF-SPEC.md", "GUIDE.md", "VERSION"):
    if not (KIT / rel).is_file():
        _missing.append(rel)
check(not _missing, "existen los archivos que el resto de los asserts consume",
      f"faltan: {', '.join(sorted(set(_missing)))}" if _missing else "")
check(not _uninventoried,
      "todo el material instalado está en el inventario literal INSTALLED",
      f"en disco pero sin asserts: {', '.join(_uninventoried)}" if _uninventoried else "")

# ------------------------------------------------- 0b. Los comentarios HTML están bien formados
# Un `-->` dentro del cuerpo de un comentario es markup INVÁLIDO: por regla de HTML el primer
# `-->` lo cierra, así que ningún parser puede desambiguarlo — y el resto del comentario pasa a
# leerse como contenido, falseando en silencio el presupuesto y los mensajes de otros asserts
# (pasó de verdad en 0.6.0). Se detecta por el resto: sacados los comentarios bien formados,
# afuera no puede quedar ningún delimitador suelto.
for rel in INSTALLED:
    txt = read_required(rel)
    outside = strip_comments(txt) if txt is not None else ""
    stray = [d for d in ("<!--", "-->") if d in outside]
    check(txt is not None and not stray, f"{rel} tiene los comentarios HTML bien formados",
          f"delimitador suelto fuera de comentario ({', '.join(stray)}): "
          "¿un `-->` escrito dentro del cuerpo de un comentario?" if stray else "")

# ---------------------------------------------------------------- 1. Linter sobre el dogfood
if (KIT / "knowledge").is_dir():
    r = subprocess.run(
        [sys.executable, "templates/scripts/okf_lint.py", "knowledge", "--strict"],
        cwd=KIT, capture_output=True, text=True,
    )
    check(r.returncode == 0, "linter pasa limpio (--strict) sobre el bundle dogfood knowledge/",
          (r.stdout + r.stderr).strip() if r.returncode != 0 else "")
else:
    check(False, "linter pasa limpio (--strict) sobre el bundle dogfood knowledge/",
          "no se montó el dogfood knowledge/")

# El assert de arriba mide "el linter no se queja". Un linter VACÍO tampoco se queja: salía
# 0 y el gate declaraba 104/104 con la herramienta más usada del kit destruida. Hay que
# probar que el linter FUNCIONA, no solo que calla — se lo corre contra una rotura conocida.
with tempfile.TemporaryDirectory() as _tmp:
    _b = Path(_tmp) / "knowledge"
    _b.mkdir(parents=True)
    (_b / "index.md").write_text("# Concept\n\n* [Roto](roto.md) - Sin type.\n", encoding="utf-8")
    (_b / "roto.md").write_text("---\ntitle: Sin type\n---\n\ncuerpo\n", encoding="utf-8")
    _r = subprocess.run([sys.executable, "templates/scripts/okf_lint.py", str(_b)],
                        cwd=KIT, capture_output=True, text=True)
    check(_r.returncode == 1 and "type" in (_r.stdout + _r.stderr),
          "el linter DETECTA una rotura conocida (no solo calla ante el dogfood)",
          f"exit={_r.returncode}; un linter vacío o roto pasaría este bundle sin `type`")

# ---------------------------------------------------------------- 2. kit_version
ver = (read_required("VERSION") or "").strip()
check(bool(ver), "VERSION existe y no está vacío")

for rel, tok in [
    ("templates/knowledge/index.md", "kit_version"),
    ("templates/knowledge/log.md", "KIT_VERSION"),
    ("templates/skills/okf-init/SKILL.md", "kit_version"),
    ("reference/examples.md", "kit_version"),
]:
    txt = read_required(rel)
    # Sin comentarios: si `kit_version` solo vive en el comentario de instalación, el
    # archivo instalado queda SIN el sello — que es justo lo que este assert cubre.
    ok = txt is not None and tok.lower() in strip_comments(txt).lower()
    check(ok, f"{rel} siembra kit_version fuera de los comentarios",
          "el archivo no existe" if txt is None else ("solo aparece en un comentario HTML" if not ok else ""))

# El valor real, y en el FRONTMATTER (no en un ejemplo del cuerpo)
_dogfood_index = read_required("knowledge/index.md")
_fm = frontmatter(_dogfood_index or "")
_m = re.search(r'^kit_version:\s*(.+)$', _fm, re.M)
_stamped = None
if _m:
    _raw = _m.group(1).strip()
    _raw = re.sub(r"\s+#.*$", "", _raw).strip()          # comentario YAML al final
    _stamped = _raw.strip("\"'").strip()
check(_stamped == ver and bool(ver),
      "el dogfood knowledge/index.md estampa kit_version == VERSION en su frontmatter",
      f"VERSION={ver!r} pero el frontmatter estampa {_stamped!r}" if _stamped != ver else "")

# ---------------------------------------------------------------- 3. Keep-alive
# Los tokens tienen que estar en los PASOS del procedimiento, no sueltos en cualquier
# párrafo (borrar el paso de `log.md` pasaba desapercibido porque `log.md` aparecía en
# otra sección del mismo archivo).
KEEPALIVE_TOKENS = ["index.md", "log.md", "{type}", "frontmatter"]
for rel in ["templates/AGENTS.md", "templates/skills/okf-update/SKILL.md"]:
    txt = read_required(rel)
    steps = numbered_steps(strip_comments(txt)) if txt is not None else ""
    missing = [t for t in KEEPALIVE_TOKENS if t not in steps]
    check(txt is not None and not missing,
          f"{rel} describe el keep-alive completo en sus pasos numerados",
          "el archivo no existe" if txt is None else (f"falta en los pasos: {', '.join(missing)}" if missing else ""))

# ---------------------------------------------------------------- 3b. Capa de futuro
FUTURE_TOKENS = ["_changes/", "roadmap", "harvest"]
for rel in [
    "templates/AGENTS.md",
    "templates/skills/okf-plan/SKILL.md",
    "templates/knowledge/_change.md",
]:
    txt = read_required(rel)
    body = strip_comments(txt).lower() if txt is not None else ""
    missing = [t for t in FUTURE_TOKENS if t not in body]
    check(txt is not None and not missing,
          f"{rel} nombra las tres piezas de la capa de futuro (_changes/, roadmap, harvest)",
          "el archivo no existe" if txt is None else (f"falta: {', '.join(missing)}" if missing else ""))

# --------------------------------- 3b2. El disparador de scope creep chequea existencia
# Medido: sin este chequeo, el agente anota como "por hacer" algo que el código ya tiene, y
# esa premisa falsa queda ESCRITA en el roadmap (ver el cambio 0001). La regla general
# "gana el código" ya está en el contrato, pero el disparador la salteaba.
for rel in ["templates/AGENTS.md", "templates/skills/okf-plan/SKILL.md"]:
    txt = read_required(rel)
    body = strip_comments(txt).lower() if txt is not None else ""
    ok = near(body, "después", "ya existe", window=300)
    check(ok, f"{rel} exige chequear si la idea ya existe antes de anotarla en Después",
          "el archivo no existe" if txt is None else ("el disparador no menciona el chequeo" if not ok else ""))

# ---------------------------------------------------------------- 3c. Contrato: presupuesto
# Se mide lo que queda INSTALADO: sin el comentario TEMPLATE y sin las líneas de
# marcadores OKF:*, que son andamiaje de instalación y se borran siempre.
BUDGET = 7000
_agents_raw = read_required("templates/AGENTS.md") or ""
# Solo el comentario de CABECERA (el de instalación). Los marcadores OKF:* también son
# comentarios HTML: si los borrara acá, no quedaría nada que contar más abajo.
_agents_body = re.sub(r"^\s*<!--(?:(?!-->).)*-->\s*", "", _agents_raw, count=1, flags=re.S)
_agents_installed = re.sub(r"^[ \t]*<!--\s*OKF:.*?-->[ \t]*\n", "", _agents_body, flags=re.M)
check(0 < len(_agents_installed) <= BUDGET,
      "templates/AGENTS.md instalado entra en el presupuesto",
      f"{len(_agents_installed)}/{BUDGET} chars ≈ {len(_agents_installed)//4} tokens por turno")

# El techo está escrito también en prosa, en dos archivos: que no derive del valor real.
for rel in ["templates/AGENTS.md", "templates/skills/okf-verify/SKILL.md"]:
    txt = read_required(rel)
    check(txt is not None and str(BUDGET) in txt,
          f"{rel} declara el mismo techo que el gate ({BUDGET})",
          "no menciona el número" if txt is not None and str(BUDGET) not in txt else "")

# ---------------------------------------------------------------- 3d. Marcadores
# Solo cuentan los marcadores que ocupan su propia línea en el CUERPO: los que el
# comentario de cabecera cita como documentación no son marcadores reales (contarlos
# permitía que un par citado compensara un par borrado, enmascarando el fallo).
_MARK_RE = re.compile(r"^[ \t]*<!-- OKF:future-layer:(start|end) -->[ \t]*$", re.M)
_marks = _MARK_RE.findall(_agents_body)
_starts, _ends = _marks.count("start"), _marks.count("end")
_alternating = all(m == ("start" if i % 2 == 0 else "end") for i, m in enumerate(_marks))
check(_starts == _ends and _starts >= 3 and _alternating,
      "templates/AGENTS.md marca la capa de futuro con pares start/end alternados",
      f"{_starts} start / {_ends} end, alternados={_alternating} (mínimo 3 pares)")

# Los conteos escritos en prosa tienen que seguir al número real de marcadores. `okf-init`
# y el `GUIDE` quedaron afuera a propósito: el recorte lo ejecuta `okf_install.py`, así que ya
# no describen los marcadores. Los dos que quedan son los que SÍ enseñan el recorte a mano (el
# comentario del template y la referencia del camino manual).
for rel in ["templates/AGENTS.md", "reference/manual-install.md"]:
    txt = read_required(rel) or ""
    ok = f"{2 * _starts} líneas" in txt and (f"{_starts} pares" in txt or f"{_starts} bloques" in txt)
    check(ok, f"{rel} declara el número real de marcadores ({2 * _starts} líneas / {_starts} bloques)",
          "el conteo en prosa no coincide con los marcadores del template" if not ok else "")

# La instalación MÍNIMA (sin los bloques) no puede quedar hablando de la capa.
_minimal = re.sub(
    r"^[ \t]*<!-- OKF:future-layer:start -->[ \t]*$.*?^[ \t]*<!-- OKF:future-layer:end -->[ \t]*$",
    "", _agents_body, flags=re.S | re.M)
ORPHAN_TOKENS = ("_changes/", "okf-plan", "roadmap.md", "rumbo vigente", "cambio activo",
                 "harvest", "trabajo en curso")
_orphans = [t for t in ORPHAN_TOKENS if t in _minimal.lower()]
check(not _orphans,
      "el contrato sin los bloques marcados no contiene ninguno de los términos de la capa",
      f"huérfanos: {', '.join(_orphans)}" if _orphans else "")

# ---------------------------------------------------------------- 3e. Rama normativa
_spec = read_required("OKF-SPEC.md")
check(_spec is not None and "3.5" in _spec and "normativ" in _spec.lower(),
      "OKF-SPEC.md define la regla canónica de autoridad (§3.5 descriptivo vs normativo)")

# No alcanza con que los tokens aparezcan sueltos: tienen que coocurrir con la salida que
# la regla prescribe. (Un texto que NIEGA la regla contiene los mismos tokens.)
for rel in [
    "templates/AGENTS.md",
    "templates/skills/okf-update/SKILL.md",
    "templates/skills/okf-verify/SKILL.md",
]:
    txt = read_required(rel)
    body = strip_comments(txt).lower() if txt is not None else ""
    ok = near(body, "normativ", "supersede") and (
        "violación" in body or "arreglar el código" in body)
    check(ok, f"{rel} afirma la rama normativa con su salida (superseder / arreglar el código)",
          "el archivo no existe" if txt is None else ("los términos no coocurren, o falta la salida" if not ok else ""))

_guide = read_required("GUIDE.md")
check(_guide is not None and "3.5" in _guide and "normativ" in _guide.lower(),
      "GUIDE.md enseña la regla de autoridad y apunta al canónico (§3.5)")

# ------------------------- 3j. El Nivel 2 tiene método, y solo "Ahora" del rumbo se audita
# El drift descriptivo es el único smell que necesita procedimiento (un concepto que
# contradice el código se ve igual de prolijo que uno correcto) y el que más riesgo de
# deriva tiene: vive duplicado entre la reference del kit y el skill instalado.
for rel in ["reference/verification.md", "templates/skills/okf-verify/SKILL.md"]:
    body = strip_comments(read_required(rel) or "").lower()
    ok = near(body, "okf_stale", "contradicción", window=900)
    check(ok, f"{rel} da método al Nivel 2 (rankear con okf_stale + buscar la contradicción)",
          "falta el método o no nombra la herramienta que lo hace barato" if not ok else "")
    # Auditar el rumbo entero sería puro falso positivo: solo "Ahora" afirma estado del código.
    # Hay que exigir la mitad de INCLUSIÓN ("solo la sección Ahora"), no solo la de exclusión:
    # con la exclusión sola, borrar la regla de inclusión pasaba desapercibido (lo cazó la
    # inyección, no la lectura).
    ok2 = near(body, "solo la sección", "ahora", window=120) and near(body, "intención pura")
    check(ok2, f"{rel} limita la auditoría del rumbo a la sección \"Ahora\"",
          "falta la mitad de inclusion (solo la seccion Ahora) o la de exclusion (intencion pura)" if not ok2 else "")

# `okf-verify` manda a correr okf_stale.py: si la instalación no lo copia, manda a la nada.
# `okf-verify` manda a correr okf_stale.py: quien instala tiene que copiarlo. Son los dos
# caminos de instalación — el skill (que delega al script) y la referencia manual.
for rel in ["reference/manual-install.md", "templates/skills/okf-init/SKILL.md"]:
    check("okf_stale.py" in (read_required(rel) or ""),
          f"{rel} instala okf_stale.py en el repo destino",
          "okf-verify lo manda a correr y no estaría" )

# --------------------------------- 3i. Existe camino de ACTUALIZACIÓN, no solo de instalación
# El bundle lo mantiene `okf-update`, pero el material instalado (contrato, skills, scripts)
# se fosiliza en la revisión con la que el repo nació. Sin este camino, `kit_version` es una
# clave que se estampa y nadie usa.
_upg = read_required("reference/upgrading.md")
check(_upg is not None and "kit_version" in _upg and "material instalado" in _upg.lower(),
      "reference/upgrading.md documenta cómo subir el material instalado",
      "falta el doc o no distingue material instalado de contenido" if not _upg else "")
_init = read_required("templates/skills/okf-init/SKILL.md") or ""
check("upgrading.md" in _init and "kit_version" in _init,
      "okf-init rutea a la actualización cuando el bundle ya existe con kit_version viejo",
      "sigue mandando a okf-update, que no puede tocar el material instalado" if "upgrading.md" not in _init else "")
check("upgrading.md" in (read_required("GUIDE.md") or ""),
      "GUIDE.md ofrece el camino de actualización entre init y migrate")

# ------------------------------- 3k. El instalador: se verifica la SALIDA, no el template
# Todos los asserts de recorte de arriba miden el TEMPLATE. Lo que llega al repo destino es
# la salida del instalador, y ahí es donde históricamente se rompía (un marcador que
# sobrevive, un `{{KIT_VERSION}}` sin sellar, un bundle que no lintea el día uno). Se
# instala de verdad en un tmpdir y se mira el resultado.
_INSTALLER = "scripts/okf_install.py"
check((KIT / _INSTALLER).is_file(), f"{_INSTALLER} existe (la plomería del init es determinista)")

if (KIT / _INSTALLER).is_file():
    for _mode, _flags in (("completa", []), ("mínima", ["--minimal"])):
        with tempfile.TemporaryDirectory() as _tmp:
            _dst = Path(_tmp) / "repo"
            _dst.mkdir()
            subprocess.run(["git", "init", "-q", str(_dst)], capture_output=True)
            _r = subprocess.run(
                [sys.executable, _INSTALLER, str(_dst), "--name", "Proyecto de Prueba", *_flags],
                cwd=KIT, capture_output=True, text=True,
            )
            check(_r.returncode == 0,
                  f"okf_install.py deja una instalación {_mode} que el linter acepta (--strict)",
                  (_r.stdout + _r.stderr).strip()[-700:] if _r.returncode != 0 else "")

            # Andamiaje y sellos, sobre TODO lo escrito (no solo el contrato).
            _files = [p for p in _dst.rglob("*") if p.is_file() and ".git/" not in p.as_posix()]
            _residue = sorted({
                f"{p.relative_to(_dst)}:{tok}"
                for p in _files for tok in ("OKF:future-layer", "{{KIT_VERSION}}")
                if tok in p.read_text(encoding="utf-8", errors="replace")
            })
            check(not _residue,
                  f"la instalación {_mode} no deja andamiaje ni el placeholder de versión",
                  f"quedó: {', '.join(_residue)}" if _residue else "")

            # El chequeo de arriba busca dos tokens LITERALES, así que un tercer tipo de
            # andamiaje pasaba invisible: el comentario de cabecera de un template. Es el
            # que le explica al lector cómo instalar el kit — en el repo destino no tiene
            # ningún sentido, y en el caso del CLAUDE.md se pagaba en cada turno. La regla
            # general: si un archivo instalado EMPIEZA con un comentario HTML, es andamiaje.
            _headers = sorted(
                str(p.relative_to(_dst)) for p in _files
                if p.suffix == ".md"
                and p.read_text(encoding="utf-8", errors="replace").lstrip().startswith("<!--")
            )
            check(not _headers,
                  f"la instalación {_mode} no deja comentarios de template en la cabecera",
                  f"empiezan con un comentario: {', '.join(_headers)}" if _headers else "")

            # Nada del bundle contesta "¿cómo sé que esto anda?" salvo este archivo, y va
            # SIEMPRE — incluida la instalación mínima, que es la del perfil "andá directo
            # al código". Que exista en completa y falte en mínima sería el bug de la lente C
            # otra vez, así que se mide en las dos.
            _chk = _dst / "knowledge" / "checks.md"
            check(_chk.is_file(),
                  f"la instalación {_mode} siembra knowledge/checks.md",
                  "sin él, 'verificar' significa pasar el linter del bundle y nada pregunta "
                  "nunca si el código anda")

            _idx = (_dst / "knowledge" / "index.md")
            _got = re.search(r'^kit_version:\s*"?([^"\s]+)"?', frontmatter(
                _idx.read_text(encoding="utf-8") if _idx.is_file() else ""), re.M)
            check(_got is not None and _got.group(1) == ver,
                  f"la instalación {_mode} estampa kit_version == VERSION",
                  f"esperaba {ver!r}, encontré {_got.group(1)!r}" if _got else "no hay kit_version")

            # La mínima no puede quedar hablando de una capa que no instaló — mismo
            # criterio que el assert del template, pero medido sobre el archivo instalado.
            if _flags:
                _inst_agents = (_dst / "AGENTS.md")
                _o = [t for t in ORPHAN_TOKENS
                      if t in _inst_agents.read_text(encoding="utf-8", errors="replace").lower()]
                check(not _o, "el AGENTS.md de una instalación mínima no menciona la capa de futuro",
                      f"huérfanos: {', '.join(_o)}" if _o else "")
                for _absent in ("knowledge/roadmap.md", ".claude/skills/okf-plan/SKILL.md"):
                    check(not (_dst / _absent).exists(),
                          f"la instalación mínima no instala {_absent}")

# El instalador NO puede pisar el entrypoint ni el hook del usuario: es pérdida de datos
# irreversible si no estaba commiteado, y para ese repo existe `okf-migrate`. Se mide sobre
# la conducta real, no sobre la prosa (una pasada adversarial lo encontró destruyendo un
# AGENTS.md con la ubicación de los secretos, un CLAUDE.md y un pre-commit con los tests).
if (KIT / _INSTALLER).is_file():
    with tempfile.TemporaryDirectory() as _tmp:
        _dst = Path(_tmp) / "repo"
        _dst.mkdir()
        subprocess.run(["git", "init", "-q", str(_dst)], capture_output=True)
        (_dst / "AGENTS.md").write_text("# Mi contrato propio\n- No toques legacy/\n", encoding="utf-8")
        _hook = _dst / ".git" / "hooks" / "pre-commit"
        _hook.parent.mkdir(parents=True, exist_ok=True)
        _hook.write_text("#!/bin/sh\nnpm test\n", encoding="utf-8")
        _r = subprocess.run([sys.executable, _INSTALLER, str(_dst), "--name", "X"],
                            cwd=KIT, capture_output=True, text=True)
        check(_r.returncode == 2 and "No toques legacy/" in (_dst / "AGENTS.md").read_text(),
              "okf_install.py aborta en vez de pisar un AGENTS.md escrito a mano",
              f"exit={_r.returncode}; el contrato del usuario "
              f"{'sobrevivió' if 'legacy' in (_dst / 'AGENTS.md').read_text() else 'SE PERDIÓ'}")
        # --force sobre un archivo que git NO tiene es igual de irreversible que no usarlo:
        # "commiteá antes" es un paso que falla en silencio (un hook que aborta el commit).
        _rf = subprocess.run([sys.executable, _INSTALLER, str(_dst), "--name", "X", "--force"],
                             cwd=KIT, capture_output=True, text=True)
        check(_rf.returncode == 2 and "No toques legacy/" in (_dst / "AGENTS.md").read_text(),
              "okf_install.py con --force no borra un entrypoint que git no puede devolver",
              f"exit={_rf.returncode}; el contrato del usuario "
              f"{'sobrevivió' if 'legacy' in (_dst / 'AGENTS.md').read_text() else 'SE PERDIÓ'}")

        # Commiteado, --force sí instala — pero el hook ajeno sigue sin pisarse. El commit
        # va con --no-verify a propósito: el fixture tiene un hook que falla, que es
        # exactamente el escenario que motivó el assert de arriba.
        for _cmd in (["git", "-C", str(_dst), "add", "-A"],
                     ["git", "-C", str(_dst), "-c", "user.email=gate@okf", "-c",
                      "user.name=gate", "commit", "-qm", "fixture", "--no-verify"]):
            subprocess.run(_cmd, capture_output=True)
        _r2 = subprocess.run([sys.executable, _INSTALLER, str(_dst), "--name", "X", "--force"],
                             cwd=KIT, capture_output=True, text=True)
        check(_r2.returncode == 0 and "npm test" in _hook.read_text(encoding="utf-8"),
              "okf_install.py no pisa un pre-commit que no es del kit (ni con --force)",
              f"exit={_r2.returncode}; " + ("le apagó los tests al usuario sin avisar"
                                            if "npm test" not in _hook.read_text() else ""))

# El contrato tiene que poder ACTUALIZARSE sin perder lo del usuario: si no, cada repo se
# queda con el texto del día que se instaló y ninguna mejora del kit le llega nunca. Se mide
# sobre la conducta real —instalar, escribir contenido propio, envejecer el kit, upgradear—
# porque las dos mitades pueden fallar solas: no reemplazar, o reemplazar de más.
if (KIT / _INSTALLER).is_file():
    with tempfile.TemporaryDirectory() as _tmp:
        _dst = Path(_tmp) / "repo"
        _dst.mkdir()
        for _c in (["git", "init", "-q", str(_dst)],
                   ["git", "-C", str(_dst), "config", "user.email", "gate@okf"],
                   ["git", "-C", str(_dst), "config", "user.name", "gate"]):
            subprocess.run(_c, capture_output=True)
        subprocess.run([sys.executable, _INSTALLER, str(_dst), "--name", "X"],
                       cwd=KIT, capture_output=True, text=True)
        _ag = _dst / "AGENTS.md"
        _txt = _ag.read_text(encoding="utf-8")
        # Contenido del usuario en sus tres formas: una sección que el kit siembra vacía,
        # y una sección entera que el kit no conoce.
        _txt = re.sub(r"(## Reglas duras\n\n).*?(\n\n## Capas)", r"\1- SECRETO_DEL_USUARIO\2",
                      _txt, flags=re.S)
        _txt = re.sub(r"(## Capas NO autoritativas\n\n).*?(\n\n## 1\.)", r"\1- BASURA_DEL_USUARIO\2",
                      _txt, flags=re.S)
        _txt += "\n## Seccion propia\n\nSECCION_DEL_USUARIO\n"
        # Envejecemos el kit: prosa que la versión actual ya no tiene.
        _txt = _txt.replace("**Guardrails:**", "PROSA_VIEJA_DEL_KIT\n\n**Guardrails:**", 1)
        _ag.write_text(_txt, encoding="utf-8")
        for _c in (["git", "-C", str(_dst), "add", "-A"],
                   ["git", "-C", str(_dst), "commit", "-qm", "fixture"]):
            subprocess.run(_c, capture_output=True)
        subprocess.run([sys.executable, _INSTALLER, str(_dst), "--upgrade"],
                       cwd=KIT, capture_output=True, text=True)
        _got = _ag.read_text(encoding="utf-8")
        _kept = [m for m in ("SECRETO_DEL_USUARIO", "BASURA_DEL_USUARIO", "SECCION_DEL_USUARIO")
                 if m not in _got]
        check(not _kept,
              "okf_install.py --upgrade conserva el contenido del usuario en el contrato",
              f"se perdió: {', '.join(_kept)}" if _kept else "")
        check("PROSA_VIEJA_DEL_KIT" not in _got,
              "okf_install.py --upgrade reemplaza la prosa vieja del kit en el contrato",
              "el contrato quedó con el texto de la versión anterior")

        # La maquinaria (skills, linter, hook) también es reemplazable — y también puede
        # haberla editado el usuario. Pisarla en silencio es la misma pérdida de datos que
        # el contrato, un nivel más abajo. Se mide sobre la conducta: editar y upgradear.
        _skill = _dst / ".claude" / "skills" / "okf-update" / "SKILL.md"
        _skill.write_text(_skill.read_text(encoding="utf-8").rstrip()
                          + "\n\nREGLA_PROPIA_DEL_USUARIO\n", encoding="utf-8")
        _victim = _dst / "scripts" / "okf_lint.py"
        _before = _victim.read_text(encoding="utf-8")
        for _c in (["git", "-C", str(_dst), "add", "-A"],
                   ["git", "-C", str(_dst), "commit", "-qm", "edits", "--no-verify"]):
            subprocess.run(_c, capture_output=True)
        subprocess.run([sys.executable, _INSTALLER, str(_dst), "--upgrade"],
                       cwd=KIT, capture_output=True, text=True)
        check("REGLA_PROPIA_DEL_USUARIO" in _skill.read_text(encoding="utf-8"),
              "okf_install.py --upgrade no pisa material instalado que el usuario editó",
              "le borró su edición sin avisar")
        check(_victim.read_text(encoding="utf-8") == _before,
              "okf_install.py --upgrade deja intacto lo que no cambió",
              "reescribió un archivo que no hacía falta tocar")

# El contrato tiene que MANDAR a correr los chequeos: sembrar el archivo y no rutearlo lo
# vuelve un documento que nadie abre. Se mide sobre el contrato instalado, no sobre el
# template, porque el recorte de --minimal podría llevárselo.
_MARKED_BLOCK = re.compile(
    r"^[ \t]*<!--\s*OKF:future-layer:start\s*-->[ \t]*\n.*?"
    r"^[ \t]*<!--\s*OKF:future-layer:end\s*-->[ \t]*\n", re.S | re.M)


def _installed_contract(minimal: bool) -> str:
    """El contrato tal como queda instalado, con o sin la capa de futuro."""
    txt = _MARKED_BLOCK.sub("", _agents_body) if minimal else _agents_body
    return re.sub(r"^[ \t]*<!--\s*OKF:.*?-->[ \t]*\n", "", txt, flags=re.M)


for _mini in (False, True):
    _c = _installed_contract(_mini)
    # Se exige el IMPERATIVO, no las palabras sueltas: "existe un archivo de chequeos"
    # contiene los mismos términos y no manda a nadie a hacer nada.
    check("checks.md" in _c and near(_c, "checks.md", "corré", "listo"),
          f"el contrato {'mínimo' if _mini else 'completo'} manda a correr los chequeos del repo",
          "el archivo se siembra pero nadie lo abre")

# Una verdad, un lugar: si el skill vuelve a describir la plomería en prosa, hay dos
# fuentes que van a derivar (la regla dura #1 del kit y su causa raíz de bugs).
_init_txt = read_required("templates/skills/okf-init/SKILL.md") or ""
# El procedimiento de este skill vive en headings `## N.`, no en items de lista: se mide ahí
# (buscarlo con numbered_steps daba un FAIL que no era el que el assert dice cuidar).
_init_steps = [s for s in re.split(r"^## ", strip_comments(_init_txt), flags=re.M)
               if re.match(r"\d+\.", s)]
check(any("okf_install.py" in s for s in _init_steps),
      "okf-init delega la plomería al instalador en un paso de su procedimiento",
      "ningún paso nombra okf_install.py: la prosa volvió a ser la fuente del procedimiento")
_restated = [t for t in ("chmod +x", "OKF:future-layer") if t in strip_comments(_init_txt)]
check(not _restated, "okf-init no re-statea los pasos mecánicos que ahora son del instalador",
      f"vuelve a describir: {', '.join(_restated)}" if _restated else "")

# ------------------------------------------- 3l. Distribución como plugin de Claude Code
# El plugin es el PROPIO repo del kit (`"source": "./"`) y apunta a `templates/skills/` con
# rutas custom: si copiara los skills, habría dos copias = la deriva que el kit existe para
# evitar. Lo que hay que cuidar es que esas rutas resuelvan y que la versión no derive.
_PLUGIN = ".claude-plugin/plugin.json"
_MARKET = ".claude-plugin/marketplace.json"
_pl_raw, _mk_raw = read_required(_PLUGIN), read_required(_MARKET)
_pl: dict = {}
_mk: dict = {}
try:
    _pl = json.loads(_pl_raw) if _pl_raw else {}
    _mk = json.loads(_mk_raw) if _mk_raw else {}
    _json_err = ""
except json.JSONDecodeError as e:
    _json_err = str(e)
check(bool(_pl) and bool(_mk) and not _json_err,
      "los manifiestos del plugin existen y son JSON válido",
      _json_err or "falta plugin.json o marketplace.json")

# Segunda copia de la versión (VERSION es la fuente): sin este assert, `/plugin install`
# entrega una revisión y el bundle estampa otra.
check(_pl.get("version") == ver, f"{_PLUGIN} declara la misma versión que VERSION",
      f"VERSION={ver!r} pero el plugin declara {_pl.get('version')!r}")

# Un `skills` que no resuelve = plugin instalado sin procedimientos, en silencio.
_pl_skills = _pl.get("skills") or []
_bad_skill = [s for s in _pl_skills if not (KIT / str(s).lstrip("./")).is_dir()]
check(_pl_skills and not _bad_skill, f"los skills que declara {_PLUGIN} existen en disco",
      f"no resuelven: {', '.join(_bad_skill)}" if _bad_skill else "no declara ninguno")

# El plugin ship**ea solo el par de BOOTSTRAP: `okf-update`/`okf-verify`/`okf-plan` se COPIAN
# al repo destino, porque quien clone ese repo sin el plugin tiene que seguir teniéndolos
# (decisión 0013). Shippearlos por plugin sería una dependencia oculta del entorno.
_leaked = sorted(s for s in map(str, _pl_skills)
                 if any(k in s for k in ("okf-update", "okf-verify", "okf-plan")))
check(not _leaked, f"{_PLUGIN} no ship**ea los procedimientos que van instalados en el repo",
      f"los ship**ea por plugin: {', '.join(_leaked)}" if _leaked else "")

_mk_sources = [p.get("source") for p in (_mk.get("plugins") or [])]
check(_mk_sources and all(isinstance(s, str) and (KIT / s).is_dir() for s in _mk_sources),
      f"{_MARKET} apunta a un directorio de plugin que existe",
      f"sources: {_mk_sources}")

# --------------------------- 3m. La auditoría no se auto-aprueba (revisión con contexto fresco)
# Los Niveles 2 y 4 son los únicos que auditan trabajo que el propio agente pudo haber hecho, y
# los dos donde el sesgo pesa más. Si `okf-verify` deja de delegarlos, el nivel sigue "corriendo"
# y deja de encontrar: un gate que se autoaprueba es peor que no tenerlo.
_REVIEWER = "templates/agents/okf-reviewer.md"
_rev = read_required(_REVIEWER)
check(_rev is not None, f"{_REVIEWER} existe (el revisor con contexto fresco se instala)")
_rev_body = strip_comments(_rev or "").lower()
check(near(_rev_body, "contradicción", "refutar", window=900),
      f"{_REVIEWER} le da la consigna refutatoria, no confirmatoria",
      "sin eso es un lector, no un auditor")
# Un revisor que arregla lo que encuentra vuelve a ser el autor: la asimetría ES el mecanismo.
check("disallowedtools" in (_rev or "").lower() and near(_rev_body, "no podés editar"),
      f"{_REVIEWER} no puede editar (declarado en frontmatter y en el cuerpo)",
      "si arregla lo que encuentra, vuelve a ser el autor")

_verify = strip_comments(read_required("templates/skills/okf-verify/SKILL.md") or "").lower()
# Se mide la INSTRUCCIÓN, no la coocurrencia: el bloque del reporte también nombra al
# revisor, así que un assert laxo se satisfacía desde ahí con la delegación ya borrada
# (lo cazó la inyección, no la lectura).
check(near(_verify, "delegalos", "okf-reviewer", "2 y 4", window=500),
      "okf-verify manda a DELEGAR los niveles 2 y 4 al revisor con contexto fresco",
      "la instrucción de delegar no nombra al revisor y los niveles: el auto-review volvió "
      "a ser el default")
# Vendor-neutral: sin subagentes tiene que haber salida equivalente (la misma del Nivel 3).
check(near(_verify, "subagentes", "prompt", window=400),
      "okf-verify ofrece la salida sin subagentes (prompt para una CLI nueva)",
      "quedaría atado a una herramienta con subagentes")

# ---------------------------------------------------------------- 3f. Autosuficiencia
# El material instalado no puede citar rutas que solo existen en el kit: el repo destino
# no las recibe. Se listan por nombre exacto — un charclass genérico (`templates/[a-z]+/`)
# dejaba pasar `templates/AGENTS.md` y marcaba como error el `templates/` del repo destino.
KIT_ONLY = [
    r"reference/[a-z][a-z0-9-]*\.md",
    r"templates/(?:AGENTS|CLAUDE)\.md",
    r"templates/(?:knowledge|skills|scripts|ci|hooks|eval)/",
    r"scripts/okf_(?:selfcheck|install)\.py",
    r"OKF-SPEC\.md", r"GUIDE\.md", r"DEVELOPING\.md",
]
_kitpath_re = re.compile("(" + "|".join(KIT_ONLY) + ")")
for rel in INSTALLED:
    txt = read_required(rel)
    body = strip_comments(txt) if txt is not None else ""
    hits = sorted({m.group(1) for m in _kitpath_re.finditer(body)})
    check(txt is not None and not hits, f"{rel} no cita rutas que solo existen en el kit",
          "el archivo no existe" if txt is None else (f"cita: {', '.join(hits)}" if hits else ""))

# ---------------------------------------------------------------- 3g. Formato del reporte
# Duplicado a propósito (la copia instalada tiene que funcionar sin el kit — decisión 0013),
# así que las dos copias tienen que coincidir carácter por carácter.
_fmt_re = re.compile(r"```(?:markdown|md)\r?\n(# OKF Verification Report.*?)```", re.S)
_fmt_ref = _fmt_re.search(read_required("reference/verification.md") or "")
_fmt_skill = _fmt_re.search(read_required("templates/skills/okf-verify/SKILL.md") or "")
if not _fmt_ref or not _fmt_skill:
    _fmt_detail = ("no encontré el bloque en "
                   + ("reference/verification.md" if not _fmt_ref else "okf-verify"))
elif _fmt_ref.group(1) != _fmt_skill.group(1):
    _fmt_detail = "las dos copias divergieron"
else:
    _fmt_detail = ""
check(not _fmt_detail, "el formato del reporte coincide entre verification.md y okf-verify",
      _fmt_detail)

# ---------------------------------------------------------------- 3h. Auto-aplicación
own_agents = (read_required("AGENTS.md") or "").lower()
check("roadmap.md" in own_agents and "_changes/" in own_agents,
      "el AGENTS.md del kit rutea a su propia capa de futuro (roadmap.md + _changes/)")
check((KIT / "knowledge" / "roadmap.md").is_file(),
      "el dogfood tiene su propio knowledge/roadmap.md (el kit se auto-aplica la capa)")

# ---------------------------------------------------------------- 4. Referencias
# El denominador es derivado: si el scan deja de encontrar referencias, los asserts
# desaparecen sin un solo FAIL. El piso convierte ese silencio en un fallo.
ref_re = re.compile(r"reference/([a-z][a-z0-9-]*\.md)")
referenced: set[str] = set()
for md in KIT.rglob("*.md"):
    if md.is_relative_to(KIT / "knowledge"):  # el bundle dogfood se lintea aparte
        continue
    for m in ref_re.finditer(md.read_text(encoding="utf-8", errors="replace")):
        referenced.add(m.group(1))
check(len(referenced) >= 6, "el scan de referencias encontró algo que verificar",
      f"solo {len(referenced)} referencias — ¿cambió el layout o el naming?")
for name in sorted(referenced):
    check((KIT / "reference" / name).is_file(), f"referencia reference/{name} resuelve")

# ---- reporte ----
failed = [n for ok, n, _ in results if not ok]
for ok, n, detail in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {n}" + (f"\n          → {detail}" if detail and not ok else ""))
print(f"\nokf_selfcheck: {len(results) - len(failed)}/{len(results)} OK"
      + (f", {len(failed)} FAIL" if failed else ""))
sys.exit(1 if failed else 0)
