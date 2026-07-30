#!/usr/bin/env python3
"""okf_coldtest.py — materializa un entorno aislado para el test en frío (Nivel 3).

Copia SOLO el bundle OKF (p.ej. `knowledge/`) + el entrypoint (`AGENTS.md`/`CLAUDE.md`
si existen) a un directorio limpio, **sin código ni `.git`**. Sirve para correr la
"prueba de fuego": un agente/CLI que solo ve el bundle responde preguntas del proyecto.

Solo stdlib; no requiere `pip install`. Cross-platform.

Por qué una copia y no `git worktree`: un worktree retiene acceso a `.git`, así que un
agente podría leer el código con `git show`. Una copia limpia sin `.git`, no.

ALCANCE DEL AISLAMIENTO (honesto): este entorno es ideal para abrir una **CLI/IA nueva**
con esta carpeta como raíz — ahí el código no está al alcance. Para un **subagente del
mismo proceso** (que ve todo el filesystem) el aislamiento sigue siendo por instrucción;
el entorno limpio reduce fugas accidentales y permite chequear que las citas caigan
dentro del bundle.

El script materializa el entorno y deja un prompt CON PLACEHOLDERS — las preguntas
concretas del proyecto las completa quien corre el test (o el skill okf-verify), porque
requieren criterio.

Uso:
  python3 okf_coldtest.py [BUNDLE_DIR]          # default: knowledge
  python3 okf_coldtest.py knowledge --out DIR   # destino explícito (si no, temp)
  python3 okf_coldtest.py --git                 # además hace un repo git limpio
  python3 okf_coldtest.py --out DIR --force     # sobreescribe DIR no vacío

Exit: 0 ok; 2 error de uso.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ENTRYPOINTS = ("AGENTS.md", "CLAUDE.md")

PROMPT = """\
Tenés acceso SOLO a esta carpeta: {dest}
Es un bundle de conocimiento OKF (markdown + frontmatter). NO leas código de ningún
otro lado. Empezá por {bundle}/index.md (y AGENTS.md si está) y navegá los conceptos.

Respondé estas preguntas usando SOLO el bundle, y CITÁ el archivo de cada respuesta.
Si algo no está, decí "NO ESTÁ EN EL CONTEXTO" en vez de inventar.
  1. <pregunta operativa: cómo se corre / se levanta / se testea algo>
  2. <pregunta de diseño: por qué se eligió X sobre Y>
  3. <pregunta de dominio/datos del proyecto>
  4. <trampa: algo que NO esté en el bundle, para ver si lo admite>
"""


def die(msg: str) -> int:
    print(f"okf_coldtest: {msg}", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="okf_coldtest")
    ap.add_argument("bundle", nargs="?", default="knowledge")
    ap.add_argument("--out", default=None, help="Directorio destino (default: temporal).")
    ap.add_argument("--git", action="store_true", help="Inicializar un repo git limpio en el destino.")
    ap.add_argument("--force", action="store_true", help="Sobreescribir --out si no está vacío.")
    args = ap.parse_args(argv[1:])

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        return die(f"no existe el bundle '{bundle}'")
    if not (bundle / "index.md").exists():
        print(f"okf_coldtest: aviso — '{bundle}' no tiene index.md raíz", file=sys.stderr)

    if args.out:
        dest = Path(args.out)
        # `--force` hacía `shutil.rmtree(dest)` sin mirar QUÉ era dest: apuntarlo al repo
        # (o a `.`) borraba el código y el `.git` del usuario y después crasheaba, así que
        # el stacktrace le hacía creer que no había pasado nada. Un flag que dice
        # "sobreescribir el destino" no puede significar "borrar tu repo".
        _d, _b = dest.resolve(), bundle.resolve()
        _unsafe = (
            "es el bundle mismo" if _d == _b else
            "contiene al bundle" if _d in _b.parents else
            "está adentro del bundle" if _b in _d.parents else
            "es el directorio actual" if _d == Path.cwd().resolve() else
            "es un repo git (tiene .git/)" if (dest / ".git").exists() else
            "tiene un archivo que no puso este script" if dest.is_dir() and any(
                c.name not in ("knowledge", "README.md") for c in dest.iterdir()) else ""
        )
        if dest.exists() and any(dest.iterdir()):
            if _unsafe:
                return die(f"me niego a escribir en '{dest}': {_unsafe}.\n"
                           "  El destino tiene que ser un directorio nuevo o uno que este "
                           "script haya creado antes.\n"
                           "  Omití --out y te armo uno temporal.")
            if not args.force:
                return die(f"'{dest}' no está vacío (usá --force para sobreescribir)")
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = Path(tempfile.mkdtemp(prefix="okf-cold-"))

    # Copiar SOLO el bundle + entrypoints; nada de código ni .git del repo original.
    # Se excluye todo lo de prefijo `_` (derivados, y las specs efímeras de `_changes/`):
    # no es bundle conforme, y una spec de trabajo en curso es NORMATIVA sobre el futuro —
    # un agente en frío la leería como descripción del presente y respondería mal.
    shutil.copytree(bundle, dest / bundle.name, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", "_*"))
    copied = []
    for name in ENTRYPOINTS:
        src = bundle.parent / name
        if src.is_file():
            shutil.copy2(src, dest / name)
            copied.append(name)

    if args.git:
        try:
            subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
            subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
            subprocess.run(
                ["git", "-c", "user.email=okf@local", "-c", "user.name=OKF",
                 "commit", "-q", "-m", "OKF bundle snapshot (cold-test)"],
                cwd=dest, check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"okf_coldtest: aviso — no se pudo inicializar git ({e})", file=sys.stderr)

    n_files = sum(1 for p in (dest / bundle.name).rglob("*") if p.is_file())
    entry = f" + {', '.join(copied)}" if copied else " (sin AGENTS.md/CLAUDE.md)"
    print(f"Entorno de test en frío creado: {dest}")
    print(f"  Copiado: {bundle.name}/{entry}")
    print(f"  {n_files} archivo(s) del bundle, sin código" +
          (" (repo git limpio inicializado)" if args.git else " ni .git"))
    print()
    excluidos = sorted(p.name for p in bundle.iterdir() if p.name.startswith("_"))
    if excluidos:
        print()
        print(f"  OJO: se excluyó {', '.join(excluidos)} (prefijo `_`: derivados y specs de")
        print("  trabajo en curso, que son normativas sobre el FUTURO — un agente en frío las")
        print("  leería como estado presente). Un link colgado hacia ahí NO es un defecto del")
        print("  bundle: decíselo al agente, o vas a recibirlo como hallazgo.")
    print()
    print("Prompt para una CLI/IA nueva (o un subagente restringido a esta carpeta):")
    print()
    print(PROMPT.format(dest=dest, bundle=bundle.name))
    print(f"Limpieza: rm -rf {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
