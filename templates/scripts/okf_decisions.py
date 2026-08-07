#!/usr/bin/env python3
"""okf_decisions.py — ¿el código sigue cumpliendo lo que las decisiones prescriben?

Corre en la dirección contraria a todo lo demás del kit. Una decisión `accepted` es
**normativa** (`OKF-SPEC` §3.5): un hallazgo acá **no** significa "el documento quedó viejo",
significa que **el código está en violación**. El fix es arreglar el código, o superseder la
decisión con una nueva. Editar el documento para que coincida con lo que el código hace hoy es
exactamente el modo de falla que este script existe para cazar.

Cada decisión declara en su frontmatter cómo se la falsea:

    verify: npm test -- prescripcion
    verify: none
    verify_note: por qué no se puede chequear mecánicamente

El valor no está en correrlo: está en que **al escribir la decisión hay que contestar "¿cómo
sabría que alguien la rompió?"**, que es cuando alguien todavía se acuerda de qué la protege.
Saber cuáles NO se pueden chequear también es información: son las que dependen de que alguien
las lea.

⚠️  **ESTE SCRIPT EJECUTA COMANDOS ESCRITOS EN MARKDOWN.** En tu propio repo eso es igual que
un `npm script`. En un PR que viene de un fork, es **ejecución de código arbitrario**: alguien
puede editar un `verify:` y correr lo que quiera en tu runner. Por eso **el kit NO lo agrega
al CI** — el linter sí, porque no ejecuta nada. Si lo vas a poner en CI, que sea solo para
ramas del propio repo, y mirá antes qué se va a correr:

    python3 scripts/okf_decisions.py --list

Uso:
    python3 scripts/okf_decisions.py [knowledge/decisions] [--repo .] [--list]
                                     [--only SUBSTR] [--quiet] [--timeout SEGS]
Exit: 0 si ninguna decisión está violada, 1 si hay alguna, 2 si el uso es inválido.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.S)


def field(fm: str, name: str) -> str:
    """El valor de una clave del frontmatter, sin las comillas de YAML.

    Se desenvuelve SOLO si las comillas envuelven el valor entero: un `.strip('"')` ingenuo
    se comía la comilla de cierre de un comando como `grep -q "PASS.*algo"` y el shell
    recibía una cadena sin terminar. Las 20 "violaciones" del primer dogfood eran eso.
    """
    m = re.search(rf"^{name}:\s*(.+)$", fm, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    # Un `#` dentro de comillas es parte del valor, no un comentario YAML.
    if not (len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'"):
        v = v.split(" #", 1)[0].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("dir", nargs="?", default="knowledge/decisions")
    ap.add_argument("--repo", default=".", help="dónde se ejecutan los comandos")
    ap.add_argument("--list", action="store_true",
                    help="mostrar qué se ejecutaría, SIN ejecutar nada")
    ap.add_argument("--only", help="solo las decisiones cuyo nombre contenga este texto")
    ap.add_argument("--quiet", action="store_true", help="solo lo que falla")
    ap.add_argument("--timeout", type=int, default=600, help="segundos por comando")
    a = ap.parse_args()

    d, repo = Path(a.dir), Path(a.repo).resolve()
    if not d.is_dir():
        print(f"okf_decisions: no existe '{d}'", file=sys.stderr)
        return 2

    files = sorted(p for p in d.glob("*.md") if p.name != "index.md")
    if a.only:
        files = [p for p in files if a.only in p.name]

    missing: list[Path] = []
    unverifiable: list[tuple[Path, str]] = []
    violated: list[tuple[Path, str, str]] = []
    ran = 0

    for f in files:
        m = FM_RE.match(f.read_text(encoding="utf-8"))
        if not m:
            continue
        fm = m.group(1)
        if field(fm, "status").lower() != "accepted":
            continue
        verify = field(fm, "verify")
        if not verify:
            missing.append(f)
            continue
        if verify.lower() == "none":
            unverifiable.append((f, field(fm, "verify_note")))
            continue
        if a.list:
            print(f"  {f.name}\n      $ {verify}")
            ran += 1
            continue
        try:
            r = subprocess.run(verify, shell=True, cwd=repo, capture_output=True,
                               text=True, timeout=a.timeout)
        except subprocess.TimeoutExpired:
            violated.append((f, verify, f"el comando excedió {a.timeout}s"))
            continue
        except OSError as e:
            violated.append((f, verify, f"no se pudo ejecutar: {e}"))
            continue
        ran += 1
        if r.returncode != 0:
            tail = (r.stdout + r.stderr).strip().splitlines()
            violated.append((f, verify, "\n      ".join(tail[-8:]) or f"exit {r.returncode}"))
        elif not a.quiet:
            print(f"  ok       {f.name}")

    if a.list:
        print(f"\nokf_decisions: {ran} comando(s) se ejecutarían con --repo {repo}.")
        print("Miralos antes de correr esto en un runner: son texto de un markdown.")
        return 0

    for f, note in (unverifiable if not a.quiet else []):
        print(f"  (sin chequeo) {f.name} — {note or 'sin motivo declarado'}")
    sys.stdout.flush()

    if missing and not a.quiet:
        print("\nSin `verify:` (nadie sabría si el código dejó de cumplirlas):", file=sys.stderr)
        for f in missing:
            print(f"  {f.name}", file=sys.stderr)

    if violated:
        print(f"\n*** {len(violated)} decisión(es) VIOLADAS por el código:\n", file=sys.stderr)
        for f, cmd, detail in violated:
            print(f"  {f}\n      $ {cmd}\n      {detail}\n", file=sys.stderr)
        print("Una decisión `accepted` es NORMATIVA: el bug es el código, no el documento.\n"
              "Arreglá el código, o superseder la decisión con una nueva que diga por qué\n"
              "cambió. **No edites la decisión para que coincida con el código de hoy.**",
              file=sys.stderr)
        sys.stderr.flush()

    print(f"\nokf_decisions: {ran} chequeada(s), {len(violated)} violada(s), "
          f"{len(unverifiable)} sin chequeo mecánico, {len(missing)} sin declarar.")
    return 1 if violated else 0


if __name__ == "__main__":
    sys.exit(main())
