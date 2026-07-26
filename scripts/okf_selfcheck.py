#!/usr/bin/env python3
"""okf_selfcheck.py — meta-linter del PROPIO kit OKF (herramienta de desarrollo).

NO se instala en repos destino (vive en `scripts/`, no en `templates/`).
Valida la consistencia INTERNA del kit — lo que la revisión de 4 lentes encontró que
nadie chequeaba y por eso los bugs aparecían reactivamente:

- el linter pasa limpio sobre el bundle dogfood `knowledge/`;
- `kit_version` está sembrado donde corresponde (no se "cae" en ejemplos/skills);
- el procedimiento keep-alive coincide entre `AGENTS.md` y `okf-update`
  (carpeta + frontmatter + `index.md` + `log.md` + agrupación `# {type}`);
- toda referencia `reference/*.md` resuelve.

Uso:  python3 scripts/okf_selfcheck.py
Exit: 0 si todo pasa, 1 si hay algún FAIL.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
results: list[tuple[bool, str]] = []


def check(ok: bool, name: str) -> None:
    results.append((bool(ok), name))


def read(rel: str) -> str:
    p = KIT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


# 1. El linter pasa limpio sobre el bundle dogfood knowledge/
if (KIT / "knowledge").is_dir():
    r = subprocess.run(
        [sys.executable, "templates/scripts/okf_lint.py", "knowledge", "--strict"],
        cwd=KIT, capture_output=True, text=True,
    )
    check(r.returncode == 0, "linter pasa limpio (--strict) sobre el bundle dogfood knowledge/")
else:
    check(False, "existe el bundle dogfood knowledge/ (falta: no se montó el dogfood)")

# 2. kit_version sembrado donde corresponde (no se cae)
check((KIT / "VERSION").is_file() and read("VERSION").strip() != "", "VERSION existe y no está vacío")
for rel, tok in [
    ("templates/knowledge/index.md", "kit_version"),
    ("templates/knowledge/log.md", "KIT_VERSION"),
    ("templates/skills/okf-init/SKILL.md", "kit_version"),
    ("reference/examples.md", "kit_version"),
]:
    check(tok.lower() in read(rel).lower(), f"{rel} referencia kit_version")

# 2b. el dogfood estampa kit_version == VERSION (no solo presencia: el valor real)
ver = read("VERSION").strip()
m = re.search(r'^kit_version:\s*["\']?([^"\'\n]+)', read("knowledge/index.md"), re.M)
stamped = (m.group(1).strip() if m else None)
check(stamped == ver,
      f"el dogfood knowledge/index.md estampa kit_version == VERSION ({ver})"
      + (f" — estampa '{stamped}'" if stamped != ver else ""))

# 3. El keep-alive coincide entre AGENTS.md y okf-update (mismos pasos clave)
KEEPALIVE_TOKENS = ["index.md", "log.md", "{type}", "frontmatter"]
for rel in ["templates/AGENTS.md", "templates/skills/okf-update/SKILL.md"]:
    body = read(rel)
    missing = [t for t in KEEPALIVE_TOKENS if t not in body]
    check(not missing, f"{rel} describe el keep-alive completo"
          + (f" (falta: {', '.join(missing)})" if missing else ""))

# 3b. La capa de futuro coincide entre el contrato, el skill okf-plan y el template
FUTURE_TOKENS = ["_changes/", "roadmap", "harvest"]
for rel in [
    "templates/AGENTS.md",
    "templates/skills/okf-plan/SKILL.md",
    "templates/knowledge/_change.md",
]:
    # sin los comentarios HTML: se borran al instalar, así que no cuentan como "lo describe"
    body = re.sub(r"<!--.*?-->", "", read(rel), flags=re.S).lower()
    missing = [t for t in FUTURE_TOKENS if t not in body]
    check(not missing, f"{rel} describe la capa de futuro (rumbo + _changes/ + harvest)"
          + (f" (falta: {', '.join(missing)})" if missing else ""))

# 3e. Presupuesto del contrato: AGENTS.md es lo ÚNICO que se carga en cada turno de cada
# sesión, así que su tamaño es el costo permanente del sistema (y un contrato largo se
# skimea). Se mide el texto que queda INSTALADO: sin el comentario TEMPLATE y sin las
# líneas de marcadores OKF:*, que son andamiaje de instalación y se borran siempre.
_agents_raw = read("templates/AGENTS.md")
_agents_body = re.sub(r"^<!--.*?-->\s*", "", _agents_raw, flags=re.S)  # sin el comentario TEMPLATE
_agents_installed = re.sub(r"^[ \t]*<!--\s*OKF:.*?-->[ \t]*\n", "", _agents_body, flags=re.M)
_budget = 7000
check(0 < len(_agents_installed) <= _budget,
      f"templates/AGENTS.md instalado dentro del presupuesto "
      f"({len(_agents_installed)}/{_budget} chars ≈ {len(_agents_installed)//4} tokens por turno)")

# 3f. Los marcadores de la capa de futuro están BALANCEADOS y no vacíos: son lo que hace
# mecánico el borrado en la instalación mínima (si derivan, el contrato mínimo queda roto —
# el blocker que encontró el cold-review de 0.6.0).
_marks = re.findall(r"<!-- OKF:future-layer:(start|end) -->", _agents_raw)
_starts = _marks.count("start")
_ends = _marks.count("end")
_well_nested = _starts == _ends and _starts >= 4 and all(
    m == ("start" if i % 2 == 0 else "end") for i, m in enumerate(_marks))
check(_well_nested,
      f"templates/AGENTS.md marca la capa de futuro para borrado mecánico "
      f"({_starts} start / {_ends} end, alternados y ≥4 pares)")

# Y la instalación MÍNIMA (borrando esos bloques) no puede dejar huérfano nada de la capa:
_minimal = re.sub(r"<!-- OKF:future-layer:start -->.*?<!-- OKF:future-layer:end -->", "",
                  _agents_body, flags=re.S)
_orphans = [t for t in ("_changes/", "okf-plan", "roadmap.md", "rumbo", "cambio activo")
            if t in _minimal]
check(not _orphans,
      "el contrato en instalación mínima no menciona la capa de futuro"
      + (f" (huérfanos: {', '.join(_orphans)})" if _orphans else ""))

# 3d. La rama NORMATIVA de la regla de autoridad no se cae en los archivos que la afirman
# (es la regla que más riesgo de deriva tiene: se enuncia en el contrato y en okf-update,
# y su fuente canónica es OKF-SPEC §3.5)
check("3.5" in read("OKF-SPEC.md") and "normativ" in read("OKF-SPEC.md").lower(),
      "OKF-SPEC.md define la regla canónica de autoridad (§3.5 descriptivo vs normativo)")
for rel in [
    "templates/AGENTS.md",
    "templates/skills/okf-update/SKILL.md",
    "templates/skills/okf-verify/SKILL.md",
]:
    body = read(rel).lower()
    check("normativ" in body and "supersede" in body,
          f"{rel} afirma la rama normativa (violación → arreglar código o superseder)")
# El GUIDE es el recorrido de bootstrap: si la regla no aparece ahí, nadie la aprende al
# instalar (se cayó una vez, y el CHANGELOG la daba por propagada).
check("3.5" in read("GUIDE.md") and "normativ" in read("GUIDE.md").lower(),
      "GUIDE.md enseña la regla de autoridad y apunta al canónico (§3.5)")

# 3g. El material INSTALADO es autosuficiente: no puede citar rutas que solo existen en el
# kit (reference/*.md, templates/*). El repo destino no las recibe — un puntero así manda al
# agente a un archivo inexistente meses después. okf-init/okf-migrate quedan exentos: corren
# con el kit en disco. (Los comentarios HTML de los templates también: se borran al usar.)
_kitpath_re = re.compile(
    r"(?<!okf-kit/)\b(reference/[a-z][a-z0-9-]*\.md|templates/[a-z_]+/"
    r"|OKF-SPEC\.md|GUIDE\.md|DEVELOPING\.md|CHANGELOG\.md)")
for rel in [
    "templates/AGENTS.md",
    "templates/skills/okf-update/SKILL.md",
    "templates/skills/okf-verify/SKILL.md",
    "templates/skills/okf-plan/SKILL.md",
]:
    body = re.sub(r"<!--.*?-->", "", read(rel), flags=re.S)  # sin comentarios de instalación
    hits = sorted({m.group(1) for m in _kitpath_re.finditer(body)})
    check(not hits, f"{rel} es autosuficiente (no cita rutas del kit)"
          + (f" — cita: {', '.join(hits)}" if hits else ""))

# 3h. El formato del reporte de verificación está duplicado a propósito (la copia instalada
# tiene que funcionar sin el kit — decisión 0013), así que las dos copias tienen que coincidir.
_fmt_re = re.compile(r"```markdown\n(# OKF Verification Report.*?)```", re.S)
_fmt_ref = _fmt_re.search(read("reference/verification.md"))
_fmt_skill = _fmt_re.search(read("templates/skills/okf-verify/SKILL.md"))
check(bool(_fmt_ref) and bool(_fmt_skill) and _fmt_ref.group(1) == _fmt_skill.group(1),
      "el formato del reporte coincide entre reference/verification.md y okf-verify")

# 3c. El kit SE APLICA a sí mismo la capa de futuro (no solo la distribuye)
own_agents = read("AGENTS.md").lower()
check("roadmap.md" in own_agents and "_changes/" in own_agents,
      "el AGENTS.md del kit rutea a su propia capa de futuro (roadmap.md + _changes/)")
check((KIT / "knowledge" / "roadmap.md").is_file(),
      "el dogfood tiene su propio knowledge/roadmap.md (el kit se auto-aplica la capa)")

# 4. Toda referencia reference/*.md resuelve
ref_re = re.compile(r"reference/([a-z][a-z0-9-]*\.md)")
referenced: set[str] = set()
for md in KIT.rglob("*.md"):
    if "knowledge" in md.parts:  # no escanear el bundle dogfood
        continue
    for m in ref_re.finditer(md.read_text(encoding="utf-8", errors="replace")):
        referenced.add(m.group(1))
for name in sorted(referenced):
    check((KIT / "reference" / name).is_file(), f"referencia reference/{name} resuelve")

# ---- reporte ----
failed = [n for ok, n in results if not ok]
for ok, n in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {n}")
print(f"\nokf_selfcheck: {len(results) - len(failed)}/{len(results)} OK"
      + (f", {len(failed)} FAIL" if failed else ""))
sys.exit(1 if failed else 0)
