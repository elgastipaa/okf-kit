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

import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
results: list[tuple[bool, str, str]] = []

# El material que se COPIA al repo destino. `okf-init`/`okf-migrate` quedan afuera a
# propósito: corren en el bootstrap, con el kit todavía en disco.
INSTALLED = sorted(
    p.relative_to(KIT).as_posix()
    for p in [
        KIT / "templates" / "AGENTS.md",
        KIT / "templates" / "CLAUDE.md",
        *(KIT / "templates" / "knowledge").glob("*.md"),
        *(KIT / "templates" / "skills" / s / "SKILL.md"
          for s in ("okf-update", "okf-verify", "okf-plan")),
    ]
    if p.is_file()
)


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
            "reference/verification.md", "OKF-SPEC.md", "GUIDE.md", "VERSION"):
    if not (KIT / rel).is_file():
        _missing.append(rel)
check(not _missing, "existen los archivos que el resto de los asserts consume",
      f"faltan: {', '.join(sorted(set(_missing)))}" if _missing else "")

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

# Los conteos escritos en prosa tienen que seguir al número real de marcadores.
for rel in ["templates/AGENTS.md", "GUIDE.md", "templates/skills/okf-init/SKILL.md"]:
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
for rel in ["GUIDE.md", "templates/skills/okf-init/SKILL.md"]:
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

# ---------------------------------------------------------------- 3f. Autosuficiencia
# El material instalado no puede citar rutas que solo existen en el kit: el repo destino
# no las recibe. Se listan por nombre exacto — un charclass genérico (`templates/[a-z]+/`)
# dejaba pasar `templates/AGENTS.md` y marcaba como error el `templates/` del repo destino.
KIT_ONLY = [
    r"reference/[a-z][a-z0-9-]*\.md",
    r"templates/(?:AGENTS|CLAUDE)\.md",
    r"templates/(?:knowledge|skills|scripts|ci|hooks|eval)/",
    r"scripts/okf_selfcheck\.py",
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
