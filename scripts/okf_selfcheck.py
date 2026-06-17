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
