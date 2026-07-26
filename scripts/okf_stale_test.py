#!/usr/bin/env python3
"""okf_stale_test.py — ¿`okf_stale.py` encuentra el drift, y se calla cuando no hay?

Las dos mitades importan igual. Un detector que no encuentra es inútil; uno que **inventa**
es peor, porque se deja de correr en dos semanas — que es exactamente por qué el Nivel 4 de
verificación no se corre hoy. Este test siembra cada señal a propósito sobre un repo git
temporal y verifica que aparezca, y después corre sobre un bundle limpio y verifica que no
aparezca nada.

Kit-only (vive en `scripts/`, no se instala). Correlo al tocar `templates/scripts/okf_stale.py`.

Uso:  python3 scripts/okf_stale_test.py
Exit: 0 si los casos se comportan como corresponde, 1 si no.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
STALE = KIT / "templates" / "scripts" / "okf_stale.py"


def run(cwd: Path, *args: str, env_date: str | None = None) -> None:
    env = None
    if env_date:
        import os
        env = {**os.environ, "GIT_AUTHOR_DATE": env_date, "GIT_COMMITTER_DATE": env_date}
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, env=env)


def concept(path: Path, *, ts: str, resource: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = [f"type: Reference", f'title: "{path.stem}"', f"description: Un concepto de prueba.",
          f"timestamp: {ts}"]
    if resource is not None:
        fm.append(f"resource: {resource}")
    path.write_text("---\n" + "\n".join(fm) + "\n---\n\n# Cuerpo\n", encoding="utf-8")


def build(root: Path, *, dirty: bool) -> None:
    """Arma un repo con bundle. dirty=True siembra las tres señales a propósito."""
    root.mkdir(parents=True, exist_ok=True)
    run(root, "git", "init", "-q", ".")
    run(root, "git", "config", "user.email", "t@t")
    run(root, "git", "config", "user.name", "t")
    src = root / "src"; src.mkdir()
    (src / "motor.js").write_text("// v1\n", encoding="utf-8")
    k = root / "knowledge"; k.mkdir()
    (k / "index.md").write_text("# Reference\n\n* [sano](sano.md) - Un concepto de prueba.\n", encoding="utf-8")

    # concepto SANO: timestamp posterior al último commit de su fuente
    concept(k / "sano.md", ts="2026-03-01T00:00:00Z", resource="src/motor.js")
    if dirty:
        concept(k / "roto.md", ts="2026-03-01T00:00:00Z", resource="src/se-borro.js")
        concept(k / "churn.md", ts="2026-01-01T00:00:00Z", resource="src/motor.js")
        concept(k / "sello.md", ts="2026-01-01T00:00:00Z", resource="src/motor.js")
        concept(k / "sinfuente.md", ts="2026-01-01T00:00:00Z")

    run(root, "git", "add", "-A")
    run(root, "git", "commit", "-qm", "inicial", env_date="2026-02-01T12:00:00+0000")

    if dirty:
        # commits que tocan la fuente DESPUÉS del timestamp de churn.md → churn > 0
        for i in range(3):
            (src / "motor.js").write_text(f"// v{i+2}\n", encoding="utf-8")
            run(root, "git", "add", "-A")
            run(root, "git", "commit", "-qm", f"cambio {i}", env_date="2026-02-10T12:00:00+0000")
        # commit que toca sello.md después de su propio timestamp → sello podrido
        p = k / "sello.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nEditado sin re-sellar.\n", encoding="utf-8")
        run(root, "git", "add", "-A")
        run(root, "git", "commit", "-qm", "editar sin re-sellar", env_date="2026-02-15T12:00:00+0000")


def out(root: Path) -> str:
    r = subprocess.run([sys.executable, str(STALE), "knowledge"], cwd=root,
                       capture_output=True, text=True)
    return r.stdout + r.stderr


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="okf-stale-test-"))
    bad = 0
    try:
        dirty_root, clean_root = tmp / "conDrift", tmp / "limpio"
        build(dirty_root, dirty=True)
        build(clean_root, dirty=False)
        d, c = out(dirty_root), out(clean_root)

        casos = [
            ("encuentra el resource que ya no existe", "DRIFT CONFIRMADO" in d and "roto.md" in d),
            ("encuentra el sello podrido",             "SELLO PODRIDO" in d and "sello.md" in d),
            ("encuentra el churn de la fuente",        "SOSPECHOSOS" in d and "churn.md" in d),
            ("no deja invisible al que no tiene resource", "sinfuente.md" in d),
            ("no marca el concepto sano",              "sano.md" not in d.split("SIN FUENTE")[0]),
            ("sobre limpio no inventa drift",          "DRIFT CONFIRMADO" not in c),
            ("sobre limpio no inventa sello podrido",  "SELLO PODRIDO" not in c),
            ("sobre limpio no inventa sospechosos",    "SOSPECHOSOS" not in c),
        ]
        print(f"{'caso':<48}veredicto")
        for name, ok in casos:
            bad += not ok
            print(f"{name:<48}{'ok' if ok else '<<< MAL'}")
        if bad:
            print("\n--- salida con drift ---\n" + d + "\n--- salida limpia ---\n" + c)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nokf_stale_test: {8 - bad}/8 casos se comportan como corresponde")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
