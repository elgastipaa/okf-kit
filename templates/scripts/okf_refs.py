#!/usr/bin/env python3
"""okf_refs.py — ¿el bundle nombra cosas que ya no existen?

Determinista, cero dependencias, cero tokens. **No dice si un concepto es VERDAD**: dice si
sus referencias están vivas. Caza el drift más común y más barato —el de renombres y
borrados—, que es el que convierte un `code-of-record` del glosario en una mentira sin que
nadie se entere.

Es el hueco que quedaba entre las otras tres herramientas: `okf_lint.py` valida estructura,
`okf_stale.py` rankea por antigüedad del sello (una prioridad, no un hecho) y `okf_coldtest.py`
le pregunta a un modelo (cuesta tokens y no es determinista).

Chequea, dentro del bundle:

  1. `resource:` del frontmatter, cuando apunta al repo y no a una URL.
  2. Paths entre backticks (`src/lib/x.ts`), con soporte de `*` y `**`.
  3. Símbolos entre backticks (`nombreDeFuncion()`) contra las definiciones del repo —
     **opt-in con `--symbols`**: es la parte con más falsos positivos.

Un path cuenta como referencia al repo si su **primer segmento existe en la raíz**. No hay
lista blanca de carpetas que mantener: se adapta a cualquier layout.

Las excepciones NO se editan adentro de este archivo (es material instalado y se sella con
hash): van por `--ignore`, repetible.

Uso:
    python3 scripts/okf_refs.py [knowledge] [--repo .] [--symbols] [--ignore SUBSTR]...
Exit: 0 si todas las referencias resuelven, 1 si hay alguna muerta, 2 si el uso es inválido.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Un símbolo entre backticks, con paréntesis: `hacerAlgo()`. Los paréntesis son lo que lo
# distingue de un término de dominio cualquiera escrito en código.
SYMBOL_RE = re.compile(r"`([A-Za-z_$][\w$]*)\(\)`")
# Un path entre backticks: tiene que traer al menos una barra, y nada de espacios.
PATH_RE = re.compile(r"`([^`\s]*/[^`\s]*)`")
RESOURCE_RE = re.compile(r"^resource:\s*(.+)$", re.M)

# Definiciones por lenguaje. No pretende ser un parser: alcanza con el nombre que sigue a la
# palabra clave, porque lo único que se pregunta es "¿este nombre existe en algún lado?".
DEF_RES = (
    re.compile(r"(?:function|const|let|var|class|type|interface|enum)\s+([A-Za-z_$][\w$]*)"),
    re.compile(r"(?:def|class)\s+([A-Za-z_][\w]*)"),          # Python
    re.compile(r"func\s+(?:\([^)]*\)\s*)?([A-Za-z_][\w]*)"),  # Go
    re.compile(r"(?:fn|struct|trait|impl)\s+([A-Za-z_][\w]*)"),  # Rust
    # métodos y propiedades de objeto, indentados: `nombre(` / `nombre:`
    re.compile(r"^\s{2,}([a-zA-Z_$][\w$]*)\s*[(:]", re.M),
)
CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs",
                 ".java", ".kt", ".rb", ".php", ".cs", ".swift"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
             ".next", "target", "vendor", ".mypy_cache", ".pytest_cache"}


BRACE_RE = re.compile(r"\{([^{}/]+)\}")


def expand_braces(ref: str) -> list[str]:
    """`a/{x,y}.js` → ['a/x.js', 'a/y.js']. Taquigrafía habitual al documentar, no un glob."""
    m = BRACE_RE.search(ref)
    if not m:
        return [ref]
    out = []
    for opt in m.group(1).split(","):
        out.extend(expand_braces(ref[:m.start()] + opt.strip() + ref[m.end():]))
    return out


def glob_exists(repo: Path, ref: str) -> bool:
    """¿El path existe? Con `*`/`**` alcanza con que matchee algo.

    El matcheo se hace a mano, segmento por segmento, y NO con `Path.glob`: glob interpreta
    `[...]` como clase de caracteres, así que una ruta dinámica de Next —
    `src/app/player/[sessionId]/*-block.tsx`— daba "no existe" con los archivos ahí. Fue el
    único hallazgo de la primera validación contra un bundle real, y era falso.
    """
    ref = ref.rstrip(".,;:")
    if not ref:
        return True
    variants = expand_braces(ref)
    if len(variants) > 1:
        return all(glob_exists(repo, v) for v in variants)
    if "*" not in ref:
        return (repo / ref).exists()

    candidates = [repo]
    for seg in ref.split("/"):
        if not seg or seg == ".":
            continue
        nxt: list[Path] = []
        for base in candidates:
            if not base.is_dir():
                continue
            if seg == "**":
                nxt.append(base)
                nxt.extend(d for d in base.rglob("*") if d.is_dir())
            elif "*" in seg or "?" in seg:
                # Todo literal menos `*` y `?`: los corchetes NO son clase de caracteres.
                rx = re.compile("^" + "".join(
                    ".*" if c == "*" else "." if c == "?" else re.escape(c)
                    for c in seg) + "$")
                try:
                    nxt.extend(c for c in base.iterdir() if rx.match(c.name))
                except OSError:
                    continue
            else:
                cand = base / seg
                if cand.exists():
                    nxt.append(cand)
        candidates = nxt
        if not candidates:
            return False
    return bool(candidates)


# Un doc que ENSEÑA un formato escribe rutas de ejemplo: `_changes/NNNN-<slug>.md`,
# `src/{{modulo}}/x.ts`. No son referencias, son plantillas — reportarlas es ruido garantizado
# en cualquier bundle que documente convenciones de nombres.
PLACEHOLDER_RE = re.compile(r"<[^>]*>|\{\{|\bNNNN\b|\bXXXX\b|\.{3}")


# Nombrar algo muerto **a propósito** es un uso legítimo y frecuente: un triage de docs viejos,
# una capa declarada no-autoritativa, un runbook que avisa "este reporte lista archivos que ya
# no existen". Una referencia muerta solo es un problema si el documento **la afirma como
# viva**. Sin esto, los 8 hallazgos de la primera validación contra un bundle real eran 8
# falsos positivos — y un chequeo que grita en falso se apaga a la semana.
DEAD_CONTEXT_RE = re.compile(
    r"no existe|no existen|nunca existi|ya no |dejó de |dejo de |se borr|se elimin|"
    r"borrad|eliminad|muert|obsolet|deprecad|se llamaba|antes era|renombr|no está|no estan",
    re.I)


def looks_like_repo_path(repo: Path, ref: str) -> bool:
    """¿Esto apunta a este repo, o es un nombre cualquiera con barra?

    Regla: el PRIMER segmento tiene que existir en la raíz. Así `src/lib/x.ts` se chequea y
    `Ctrl/C`, `and/or` o `https://…` no. Sin lista blanca que mantener por repo.
    """
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", ref) or ref.startswith(("/", "#", "~")):
        return False
    if PLACEHOLDER_RE.search(ref):
        return False
    first = ref.split("/", 1)[0].lstrip("./")
    if not first or first == "..":
        return False
    return (repo / first).exists()


def build_symbol_index(repo: Path) -> set[str]:
    names: set[str] = set()
    for p in repo.rglob("*"):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix not in CODE_SUFFIXES:
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for rx in DEF_RES:
            names.update(m.group(1) for m in rx.finditer(src))
    return names


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("bundle", nargs="?", default="knowledge")
    ap.add_argument("--repo", default=".", help="raíz del repo contra la que se resuelve")
    ap.add_argument("--symbols", action="store_true",
                    help="chequear también `simbolo()` contra las definiciones del repo")
    ap.add_argument("--ignore", action="append", default=[],
                    help="no reportar referencias que contengan este texto (repetible)")
    a = ap.parse_args()

    bundle, repo = Path(a.bundle), Path(a.repo).resolve()
    if not bundle.is_dir():
        print(f"okf_refs: no existe el bundle '{bundle}'", file=sys.stderr)
        return 2
    if not repo.is_dir():
        print(f"okf_refs: no existe el repo '{repo}'", file=sys.stderr)
        return 2

    docs = sorted(p for p in bundle.rglob("*.md") if ".git" not in p.parts)
    symbols = build_symbol_index(repo) if a.symbols else set()
    problems: list[tuple[Path, int, str, str]] = []

    def ignored(ref: str) -> bool:
        return any(pat in ref for pat in a.ignore)

    for doc in docs:
        text = doc.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        m = RESOURCE_RE.search(text)
        if m:
            ref = m.group(1).strip().strip('"').strip("'")
            if (looks_like_repo_path(repo, ref) and not glob_exists(repo, ref)
                    and not ignored(ref)):
                problems.append((doc, text[:m.start()].count("\n") + 1, "resource", ref))

        for i, line in enumerate(lines, 1):
            # Ventana de ±1 línea: en prosa envuelta a 90 columnas el "ya no existe" cae
            # tanto antes como después del path. Medido: con solo la línea anterior quedaban
            # 2 de 8 falsos positivos, y los dos tenían la negación en la línea siguiente.
            ctx = " ".join(lines[max(0, i - 2): i + 1])
            if DEAD_CONTEXT_RE.search(ctx):
                continue
            for mm in PATH_RE.finditer(line):
                ref = mm.group(1)
                if (looks_like_repo_path(repo, ref) and not glob_exists(repo, ref)
                        and not ignored(ref)):
                    problems.append((doc, i, "path", ref))
            if a.symbols:
                for mm in SYMBOL_RE.finditer(line):
                    name = mm.group(1)
                    if name not in symbols and not ignored(f"{name}()"):
                        problems.append((doc, i, "símbolo", f"{name}()"))

    if not problems:
        extra = f", {len(symbols)} símbolos indexados" if a.symbols else ""
        print(f"okf_refs: todas las referencias resuelven ({len(docs)} docs{extra}).")
        if not a.symbols:
            print("  (los símbolos `foo()` no se chequearon: agregá --symbols)")
        return 0

    print(f"okf_refs: {len(problems)} referencia(s) muerta(s)\n", file=sys.stderr)
    for doc, line, kind, ref in problems:
        print(f"  {doc}:{line} — {kind}: {ref} no existe en el repo", file=sys.stderr)
    print("\nEl bundle nombra algo que ya no está. **Gana el código**: corregí el concepto.\n"
          "Si la referencia es a algo externo (una API del browser, una lib), sacala de la\n"
          "corrida con --ignore en vez de editar este script, que es material instalado.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
