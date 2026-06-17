#!/usr/bin/env python3
"""okf_lint.py — chequeador determinista de conformidad para un bundle OKF.

Parte del kit OKF de ingeniería de contexto. **Solo stdlib; no requiere `pip install`
ni PyYAML.** El frontmatter se valida con un validador determinista del *subconjunto
YAML* que aparece en frontmatter (escalares, listas/flow simples, comillas). Detecta los
errores reales —`:` sin comillas, comillas/brackets sin cerrar, tabs, líneas malformadas—
y da el **mismo veredicto en cualquier máquina** (no depende de qué tengas instalado). Lo
que ese subconjunto no cubre (YAML exótico, raro en frontmatter) pasa de forma uniforme:
es un gap de cobertura acotado, no una divergencia.

Requiere Python 3.8+ (sin librerías, solo el intérprete). Si la máquina no tiene
Python, este script no es necesario: el skill `okf-verify` hace estos mismos
chequeos de Nivel 1 leyendo los archivos, sin ejecutar nada.

Chequeos (OKF v0.1 — ver OKF-SPEC.md §8). FAIL (exit 1) = cualquier ERROR:
  ERROR  - concepto sin frontmatter o sin cerrar
  ERROR  - frontmatter con YAML inválido (`:` sin comillas, comilla/bracket sin cerrar, tab, línea malformada)
  ERROR  - `type` ausente o vacío
  ERROR  - cross-link que empieza con "/" (rompe en GitHub; usá relativo al archivo)
Todo lo demás es WARN (no hace fallar, salvo --strict):
  WARN   - falta title/description/timestamp en un concepto
  WARN   - `description` con más de una frase
  WARN   - index.md (no raíz) con frontmatter (solo se permite okf_version, en la raíz)
  WARN   - log.md con un heading de fecha que no es ISO (## YYYY-MM-DD)
  WARN   - cross-link relativo roto (la spec lo tolera, pero se reporta)
  WARN   - carpeta con conceptos sin index.md
  WARN   - concepto no listado en el index.md de su carpeta
  WARN   - carpeta vacía (sin conceptos debajo)
  WARN   - el bundle no tiene index.md raíz (navegación/entrypoint)

Convención: los archivos con prefijo "_" (p.ej. `_concept.md`) se IGNORAN — son
plantillas/borradores, no conceptos. El wiring de entrypoint a nivel repo
(AGENTS.md / puntero en README) lo evalúa el skill okf-verify, no este script.

Uso:
  python3 okf_lint.py [BUNDLE_DIR]      # default: ./knowledge
  python3 okf_lint.py --strict [DIR]    # trata los warnings como errores

Salida: 0 = limpio (warnings permitidos), 1 = errores (o warnings con --strict),
        2 = error de uso.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}
AUTHORING_DEFAULTS = ("title", "description", "timestamp")
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)")
TOPKEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_-]*):(.*)$")
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
ISO_DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")
URL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:")


def is_concept(p: Path) -> bool:
    """Un .md es concepto si no es reservado ni una plantilla/borrador (prefijo '_')."""
    return p.suffix == ".md" and p.name not in RESERVED and not p.name.startswith("_")


class Linter:
    def __init__(self, bundle: Path, strict: bool = False) -> None:
        self.bundle = bundle
        self.strict = strict
        self.issues: list[tuple[str, str, int, str]] = []

    def add(self, sev: str, path: Path, line: int, msg: str) -> None:
        rel = "." if path == self.bundle else str(path.relative_to(self.bundle))
        self.issues.append((sev, rel, line, msg))

    def _ignored(self, p: Path) -> bool:
        """True si p está dentro de (o es) algo con prefijo '_': plantillas/borradores
        (`_concept.md`) y carpetas derivadas o efímeras (`_generated/`, `_scratchpad.md`).
        El linter no los trata como conceptos del bundle conforme."""
        return any(part.startswith("_") for part in p.relative_to(self.bundle).parts)

    # ---- frontmatter ----
    @staticmethod
    def split_fm(text: str):
        lines = text.lstrip("﻿").splitlines()  # tolerar BOM UTF-8 (editores Windows)
        if not lines or lines[0].strip() != "---":
            return None, lines, 1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[1:i], lines[i + 1:], i + 2
        return "UNTERMINATED", lines, 1

    @staticmethod
    def top_keys(fm_lines: list[str]) -> dict[str, str]:
        keys: dict[str, str] = {}
        for ln in fm_lines:
            if not ln.strip() or ln[:1] in (" ", "\t", "-") or ln.lstrip().startswith("#"):
                continue
            m = TOPKEY_RE.match(ln)
            if m:
                keys[m.group(1)] = m.group(2).strip()
        return keys

    @staticmethod
    def validate_frontmatter(fm_lines: list[str]) -> list[str]:
        """Valida el subconjunto YAML del frontmatter (determinista, sin PyYAML).

        Detecta los errores reales que rompen el YAML del frontmatter; devuelve
        mensajes de error. Lo que no cubre pasa uniforme (gap, no divergencia).
        """
        errs: list[str] = []
        for ln in fm_lines:
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            leading = ln[: len(ln) - len(ln.lstrip())]
            if "\t" in leading:
                errs.append("tab en la indentación del frontmatter (YAML no permite tabs)")
                continue
            if ln[:1] in (" ", "-"):  # ítem de lista o línea indentada (frontmatter plano)
                continue
            if ln[:1] in ("\"", "'"):  # clave entrecomillada (YAML válido, raro); no la validamos
                continue
            m = TOPKEY_RE.match(ln)
            if not m:
                errs.append(f"línea de frontmatter no es 'clave: valor': {ln.strip()[:40]!r}")
                continue
            key, val = m.group(1), m.group(2).strip()
            if not val:
                continue
            head = val.split(" #", 1)[0]  # quitar comentario inline
            q = val[0]
            if q in "\"'":
                if val.find(q, 1) == -1:
                    errs.append(f"`{key}`: comilla sin cerrar")
            elif q == "[":
                if head.count("[") != head.count("]"):
                    errs.append(f"`{key}`: '[' sin cerrar")
            elif q == "{":
                if head.count("{") != head.count("}"):
                    errs.append(f"`{key}`: '{{' sin cerrar")
            elif ": " in head.rstrip() or head.rstrip().endswith(":"):
                errs.append(f"`{key}`: valor con ':' sin comillas — entrecomillalo o el YAML se rompe")
        return errs

    # ---- per-file ----
    def check_concept(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.add("ERROR", path, 1, "el archivo no es UTF-8")
            return
        fm, body, body_start = self.split_fm(text)
        if fm is None:
            self.add("ERROR", path, 1, "falta frontmatter (debe empezar con '---')")
            return
        if fm == "UNTERMINATED":
            self.add("ERROR", path, 1, "frontmatter sin cerrar (falta el '---' de cierre)")
            return
        fm_errs = self.validate_frontmatter(fm)
        if fm_errs:
            for msg in fm_errs:
                self.add("ERROR", path, 1, msg)
            return  # frontmatter inválido → la extracción de claves no es confiable
        keys = self.top_keys(fm)
        if not keys.get("type", "").strip():
            self.add("ERROR", path, 1, "falta `type` (o está vacío) — único requisito duro de OKF")
        for k in AUTHORING_DEFAULTS:
            if not keys.get(k, "").strip():
                self.add("WARN", path, 1, f"falta `{k}` (recomendado al escribir)")
        ts = keys.get("timestamp", "").strip().strip('"').strip("'")
        if ts and not ISO_DT_RE.match(ts):
            self.add("WARN", path, 1, f"`timestamp` no parece ISO 8601: '{ts}'")
        desc = keys.get("description", "")
        if desc and len(desc) > 200:
            self.add("WARN", path, 1, "`description` muy larga (>200 chars) — acortala a una frase")
        elif desc and re.search(r"[.!?]\s+[A-ZÁÉÍÓÚ¿¡]", desc):
            self.add("WARN", path, 1, "`description` parece tener más de una frase")
        self.check_links(path, body, body_start)

    def check_index(self, path: Path, is_root: bool) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, _body, _ = self.split_fm(text)
        if fm not in (None, "UNTERMINATED") and not is_root:
            self.add("WARN", path, 1, "index.md no debería llevar frontmatter (salvo okf_version en la raíz)")
        self.check_links(path, text.splitlines(), 1)

    def check_log(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        for i, ln in enumerate(text.splitlines(), 1):
            s = ln.strip()
            if s.startswith("## "):
                date = s[3:].strip()
                if not ISO_DATE_RE.fullmatch(date):
                    self.add("WARN", path, i, f"heading de fecha no ISO (## YYYY-MM-DD): '{date}'")

    def check_links(self, path: Path, lines: list[str], start_line: int) -> None:
        in_fence = False
        in_comment = False
        for idx, ln in enumerate(lines):
            lineno = start_line + idx
            work = ln
            # cerrar un comentario HTML multi-línea ya abierto
            if in_comment:
                end = work.find("-->")
                if end == -1:
                    continue  # toda la línea sigue comentada
                work = work[end + 3:]
                in_comment = False
            # quitar comentarios HTML que abren en esta línea (cerrados o no)
            while "<!--" in work:
                a = work.find("<!--")
                b = work.find("-->", a + 4)
                if b == -1:
                    work = work[:a]
                    in_comment = True
                    break
                work = work[:a] + work[b + 3:]
            s = work.lstrip()
            if s.startswith("```") or s.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if ln.startswith("    ") or ln.startswith("\t"):
                continue  # code-block indentado (≥4 espacios / tab): tratar como código
            work = re.sub(r"`[^`]*`", "", work)  # quitar inline-code
            for m in LINK_RE.finditer(work):
                target = m.group(1).strip()
                if not target or target.startswith(URL_PREFIXES) or target.startswith("#"):
                    continue
                if target.startswith("/"):
                    self.add("ERROR", path, lineno,
                             f"link absoluto '{target}': empieza con '/', rompe en GitHub; usá relativo al archivo")
                    continue
                rel = target.split("#", 1)[0]
                if not rel:
                    continue
                if not (path.parent / rel).exists():
                    self.add("WARN", path, lineno, f"link roto: '{target}' no existe")

    # ---- directory-level ----
    def check_dirs(self) -> None:
        dirs = {self.bundle}
        for p in self.bundle.rglob("*"):
            if p.is_dir():
                dirs.add(p)
        for d in sorted(dirs):
            if self._ignored(d):
                continue  # carpeta con prefijo '_' (derivada/efímera): fuera del bundle conforme
            if not any(True for _ in d.rglob("*.md")):
                self.add("WARN", d, 0, "carpeta vacía (sin conceptos)")
                continue
            concepts = [c for c in d.iterdir() if c.is_file() and is_concept(c)]
            index = d / "index.md"
            if concepts and not index.exists():
                self.add("WARN", d, 0, "carpeta con conceptos sin index.md")
            if concepts and index.exists():
                itext = index.read_text(encoding="utf-8", errors="replace")
                linked = set()
                for m in LINK_RE.finditer(itext):
                    tgt = m.group(1).strip().split("#", 1)[0]
                    if tgt and not tgt.startswith(("http://", "https://", "/")):
                        linked.add((index.parent / tgt).resolve())
                for c in concepts:
                    if c.resolve() not in linked:
                        self.add("WARN", index, 0, f"el concepto '{c.name}' no está linkeado en el index")

    def check_navigable(self) -> None:
        # El linter valida que el bundle sea navegable (index.md raíz). El wiring
        # de entrypoint a nivel repo (AGENTS.md / puntero en README) lo verifica el
        # skill okf-verify, que tiene el contexto para saber si es un repo de código.
        if not (self.bundle / "index.md").exists():
            self.add("WARN", self.bundle, 0,
                     "el bundle no tiene index.md raíz (hace falta para navegación/entrypoint)")

    # ---- run / report ----
    def run(self) -> int:
        if not self.bundle.is_dir():
            print(f"okf_lint: no existe el directorio '{self.bundle}'", file=sys.stderr)
            return 2
        md_files = sorted(self.bundle.rglob("*.md"))
        if not md_files:
            print(f"okf_lint: no se encontraron .md bajo '{self.bundle}'", file=sys.stderr)
            return 2
        for p in md_files:
            if self._ignored(p):
                continue  # plantilla/borrador o carpeta '_' (p.ej. _generated/): no es un concepto
            if p.name in RESERVED:
                if p.name == "index.md":
                    self.check_index(p, is_root=(p.parent == self.bundle))
                elif p.name == "log.md":
                    self.check_log(p)
                continue
            self.check_concept(p)
        self.check_dirs()
        self.check_navigable()
        return self.report()

    def report(self) -> int:
        errors = [i for i in self.issues if i[0] == "ERROR"]
        warns = [i for i in self.issues if i[0] == "WARN"]
        for sev, rel, line, msg in sorted(self.issues, key=lambda x: (x[1], x[2])):
            loc = f"{rel}:{line}" if line else rel
            print(f"  {sev:5} {loc} — {msg}")
        if not self.issues:
            print("  (sin problemas)")
        print(f"\nokf_lint: {len(errors)} error(es), {len(warns)} warning(s) en '{self.bundle}'")
        if errors or (warns and self.strict):
            return 1
        return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:]]
    strict = "--strict" in args
    if strict:
        args.remove("--strict")
    bundle = Path(args[0]) if args else Path("knowledge")
    return Linter(bundle, strict=strict).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
