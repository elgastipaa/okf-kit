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
  ERROR  - marcador de conflicto de merge sin resolver (<<<<<<< / ======= / >>>>>>>)
  ERROR  - cross-link que empieza con "/" (rompe en GitHub; usá relativo al archivo)
Todo lo demás es WARN (no hace fallar, salvo --strict):
  WARN   - falta title/description/timestamp en un concepto
  WARN   - `description` con más de una frase
  WARN   - `authority` con un valor fuera de {normative, descriptive}
  WARN   - index.md (no raíz) con frontmatter (solo se permite okf_version, en la raíz)
  WARN   - log.md con un heading de fecha que no es ISO (## YYYY-MM-DD)
  WARN   - cross-link relativo roto (la spec lo tolera, pero se reporta)
  WARN   - carpeta con conceptos sin index.md
  WARN   - concepto no listado en el index.md de su carpeta
  WARN   - subcarpeta no listada en el index.md de su carpeta padre (invisible al navegar)
  WARN   - entrada del index.md cuyo texto no coincide con la `description` del concepto
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
# Vocabulario CERRADO de `authority` (OKF-SPEC.md §3.1). Sin esto, `authority: banana`
# pasaba en silencio: una clave que se escribe y nadie lee no declara nada.
AUTHORITY_VALUES = ("normative", "descriptive")
# `origen` declara de dónde salió el porqué de una decisión. Ver OKF-SPEC §3.1.
ORIGEN_VALUES = ("dictado", "reconstruido")
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)")
# Una entrada de index: `* [Título](archivo.md) - description del concepto`. El guion
# puede ser ASCII o em-dash, y el bullet `*` o `-`.
INDEX_ENTRY_RE = re.compile(
    r"^[ \t]*[*+-][ \t]*\[[^\]]*\]\([ \t]*([^)\s#]+)[^)]*\)[ \t]*[-–—:][ \t]*"
    # El texto sigue hasta la próxima línea que NO sea continuación: envolver la prosa a
    # 90 columnas es la norma (los docs del kit lo hacen), y cortar en el primer \n
    # producía un falso positivo que mostraba los dos textos idénticos.
    r"(.+?(?:\n[ \t]+\S[^\n]*)*)[ \t]*$", re.M)
# El espacio después de `:` NO es opcional: `type:concept` es un ESCALAR en YAML, no un
# mapping, así que un frontmatter así no tiene ninguna clave. Sin esto, el linter
# bendecía conceptos que cualquier parser real lee sin metadata.
TOPKEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_-]*):(\s.*|)$")
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
ISO_DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")
URL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:")


def strip_code(text: str) -> str:
    """El texto sin bloques cercados ni inline-code: ahí los `[x](y)` son ejemplos, no links."""
    out, fenced = [], False
    for ln in text.splitlines():
        s = ln.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            fenced = not fenced
            continue
        out.append("" if fenced else re.sub(r"`[^`]*`", "", ln))
    return "\n".join(out)


def is_concept(p: Path) -> bool:
    """Un .md es concepto si no es reservado ni una plantilla/borrador (prefijo '_')."""
    return p.suffix == ".md" and p.name not in RESERVED and not p.name.startswith("_")


class Linter:
    def __init__(self, bundle: Path, strict: bool = False,
                 skip: tuple[str, ...] = ()) -> None:
        self.bundle = bundle
        self.strict = strict
        self.skip = set(skip)
        self.issues: list[tuple[str, str, int, str, str]] = []
        # description de cada concepto, para cruzarla contra el texto de su entrada de index
        self.descriptions: dict[Path, str] = {}

    def add(self, sev: str, path: Path, line: int, msg: str, rid: str = "misc") -> None:
        """`rid` es el **id estable** de la regla: lo que se puede silenciar con `--skip`.

        El mensaje es prosa, cambia y está en castellano; el id no. Sin él, callar una regla
        obliga a forkear el kit. Los ids viven en el código y NO en un YAML paralelo a
        propósito: speccy externalizó sus reglas a datos y mantiene además una copia para
        documentarlas, que ya divergió — externalizar no salva de la deriva, duplicar sí la causa.
        """
        if rid in self.skip:
            return
        rel = "." if path == self.bundle else str(path.relative_to(self.bundle))
        self.issues.append((sev, rel, line, msg, rid))

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
            self.add("ERROR", path, 1, "el archivo no es UTF-8", rid="encoding")
            return
        fm, body, body_start = self.split_fm(text)
        if fm is None:
            self.add("ERROR", path, 1, "falta frontmatter (debe empezar con '---')", rid="frontmatter-missing")
            return
        if fm == "UNTERMINATED":
            self.add("ERROR", path, 1, "frontmatter sin cerrar (falta el '---' de cierre)", rid="frontmatter-unclosed")
            return
        fm_errs = self.validate_frontmatter(fm)
        if fm_errs:
            for msg in fm_errs:
                self.add("ERROR", path, 1, msg, rid="frontmatter-yaml")
            return  # frontmatter inválido → la extracción de claves no es confiable
        keys = self.top_keys(fm)
        if not keys.get("type", "").strip():
            self.add("ERROR", path, 1, "falta `type` (o está vacío) — único requisito duro de OKF", rid="type-required")
        for k in AUTHORING_DEFAULTS:
            if not keys.get(k, "").strip():
                self.add("WARN", path, 1, f"falta `{k}` (recomendado al escribir)", rid="field-recommended")
        ts = keys.get("timestamp", "").strip().strip('"').strip("'")
        if ts and not ISO_DT_RE.match(ts):
            self.add("WARN", path, 1, f"`timestamp` no parece ISO 8601: '{ts}'", rid="timestamp-iso")
        # Una decisión RECONSTRUIDA del código no puede ser normativa. Es el estado que
        # produjo la peor falla que midió este kit: un agente redactó un "Contexto"
        # convincente para algo que nadie decidió, quedó `accepted` —o sea normativo— y el
        # contrato le habría dicho a alguien que su código viola una decisión inexistente.
        # Por eso es ERROR y no WARN: un warning se ignora, y esto no se puede ignorar.
        origen = keys.get("origen", "").split(" #", 1)[0].strip().strip('"').strip("'").lower()
        status = keys.get("status", "").split(" #", 1)[0].strip().strip('"').strip("'").lower()
        if origen and origen not in ORIGEN_VALUES:
            self.add("WARN", path, 1,
                     f"`origen: {origen}` no está en el vocabulario "
                     f"({' | '.join(ORIGEN_VALUES)}) — no declara nada", rid="origen-vocab")
        if origen == "reconstruido" and status == "accepted":
            self.add("ERROR", path, 1,
                     "`origen: reconstruido` con `status: accepted`: una razón deducida del "
                     "código NO manda sobre el código. Dejala en `proposed` hasta que alguien "
                     "que sepa la confirme — o, si nadie sabe por qué, no escribas una "
                     "decisión: dejá la pregunta abierta", rid="origen-reconstruido-normativo")
        auth = keys.get("authority", "").split(" #", 1)[0].strip().strip('"').strip("'").lower()
        if auth and auth not in AUTHORITY_VALUES:
            self.add("WARN", path, 1,
                     f"`authority: {auth}` no está en el vocabulario "
                     f"({' | '.join(AUTHORITY_VALUES)}) — no declara nada", rid="authority-vocab")
        desc = keys.get("description", "")
        self.descriptions[path.resolve()] = desc.strip().strip('"').strip("'")
        if desc and len(desc) > 200:
            self.add("WARN", path, 1, "`description` muy larga (>200 chars) — acortala a una frase", rid="description-long")
        elif desc and re.search(r"[.!?]\s+[A-ZÁÉÍÓÚ¿¡]", desc):
            self.add("WARN", path, 1, "`description` parece tener más de una frase", rid="description-multi")
        self.check_conflict_markers(path, body, body_start)
        self.check_links(path, body, body_start)

    def check_index(self, path: Path, is_root: bool) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, _body, _ = self.split_fm(text)
        if fm not in (None, "UNTERMINATED") and not is_root:
            self.add("WARN", path, 1, "index.md no debería llevar frontmatter (salvo okf_version en la raíz)", rid="index-frontmatter")
        self.check_conflict_markers(path, text.splitlines(), 1)
        self.check_links(path, text.splitlines(), 1)

    def check_conflict_markers(self, path: Path, lines: list[str], start: int) -> None:
        """Un merge sin resolver deja DOS verdades afirmadas como vigentes en el mismo doc.

        Pasaba limpio por el linter, por `--strict` y por el hook: un agente que lea ese
        concepto no tiene forma de saber cuál de las dos rige.
        """
        for i, ln in enumerate(lines):
            if re.match(r"^(<{7}[ \t]|={7}$|>{7}[ \t])", ln.rstrip("\n")):
                self.add("ERROR", path, start + i,
                         "marcador de conflicto de merge sin resolver", rid="merge-conflict")
                return

    def check_log(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        for i, ln in enumerate(text.splitlines(), 1):
            s = ln.strip()
            if s.startswith("## "):
                date = s[3:].strip()
                if not ISO_DATE_RE.fullmatch(date):
                    self.add("WARN", path, i, f"heading de fecha no ISO (## YYYY-MM-DD): '{date}'", rid="log-date-iso")

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
            # Un code-block indentado se trata como código, PERO un ítem de lista anidado
            # (`    * ...`) no lo es: tratarlo así escondía links absolutos —el único ERROR
            # de links que define la spec— con solo indentarlos.
            if (ln.startswith("    ") or ln.startswith("\t")) and not re.match(
                    r"^[ \t]+[*+-][ \t]|^[ \t]+\d+\.[ \t]", ln):
                continue
            work = re.sub(r"`[^`]*`", "", work)  # quitar inline-code
            for m in LINK_RE.finditer(work):
                target = m.group(1).strip()
                if not target or target.startswith(URL_PREFIXES) or target.startswith("#"):
                    continue
                if target.startswith("/"):
                    self.add("ERROR", path, lineno,
                             f"link absoluto '{target}': empieza con '/', rompe en GitHub; usá relativo al archivo", rid="link-absolute")
                    continue
                rel = target.split("#", 1)[0]
                if not rel:
                    continue
                if not (path.parent / rel).exists():
                    self.add("WARN", path, lineno, f"link roto: '{target}' no existe", rid="link-broken")

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
                self.add("WARN", d, 0, "carpeta vacía (sin conceptos)", rid="dir-empty")
                continue
            concepts = [c for c in d.iterdir() if c.is_file() and is_concept(c)]
            index = d / "index.md"
            if concepts and not index.exists():
                self.add("WARN", d, 0, "carpeta con conceptos sin index.md", rid="dir-no-index")
            if index.exists():
                itext = index.read_text(encoding="utf-8", errors="replace")
                linked = set()
                for m in LINK_RE.finditer(itext):
                    tgt = m.group(1).strip().split("#", 1)[0]
                    if tgt and not tgt.startswith(("http://", "https://", "/")):
                        linked.add((index.parent / tgt).resolve())
                for c in concepts:
                    if c.resolve() not in linked:
                        self.add("WARN", index, 0, f"el concepto '{c.name}' no está linkeado en el index", rid="concept-unlinked")
                # Una subcarpeta que el index del padre no lista es un subárbol INVISIBLE
                # para quien navega desde el entrypoint: el contenido existe y nadie llega.
                for sub in sorted(p for p in d.iterdir() if p.is_dir()):
                    if self._ignored(sub) or not any(True for _ in sub.rglob("*.md")):
                        continue
                    if (sub / "index.md").resolve() not in linked and sub.resolve() not in linked:
                        self.add("WARN", index, 0,
                                 f"la subcarpeta '{sub.name}/' no está listada en este index "
                                 "(invisible al navegar desde la raíz)", rid="subdir-unlisted")
                self.check_index_descriptions(index, itext)

    @staticmethod
    def _norm(s: str) -> str:
        """Normaliza para comparar prosa: espacios, énfasis markdown y punto final."""
        s = re.sub(r"[*_`]", "", s)
        s = re.sub(r"\s+", " ", s).strip().rstrip(".")
        return s.lower()

    def check_index_descriptions(self, index: Path, itext: str) -> None:
        """El texto de cada entrada del index debe ser la `description` del concepto.

        El index es lo PRIMERO que lee un agente: si su resumen dice otra cosa que el
        concepto, lo rutea mal (o lo hace bajar a un archivo que no necesitaba). Hasta
        ahora podían divergir sin aviso.
        """
        for m in INDEX_ENTRY_RE.finditer(itext):
            target, text = m.group(1).strip(), m.group(2).strip()
            if target.startswith(("http://", "https://", "/")):
                continue
            desc = self.descriptions.get((index.parent / target).resolve())
            if not desc:
                continue  # no es un concepto de este bundle, o no declara description
            if self._norm(text) != self._norm(desc):
                self.add("WARN", index, 0,
                         f"la entrada de '{target}' no coincide con su `description` "
                         f"(index: {text[:60]!r} · concepto: {desc[:60]!r})", rid="index-desc-drift")

    def check_navigable(self) -> None:
        # El linter valida que el bundle sea navegable (index.md raíz). El wiring
        # de entrypoint a nivel repo (AGENTS.md / puntero en README) lo verifica el
        # skill okf-verify, que tiene el contexto para saber si es un repo de código.
        root = self.bundle / "index.md"
        if not root.exists():
            self.add("WARN", self.bundle, 0,
                     "el bundle no tiene index.md raíz (hace falta para navegación/entrypoint)", rid="root-index-missing")
            return
        self.check_reachable(root)

    def check_reachable(self, root: Path) -> None:
        """¿Se llega a cada concepto navegando DESDE la raíz?

        Los demás chequeos de índice son **locales**: verifican que cada carpeta liste lo
        suyo. Eso deja pasar un subárbol entero invisible — basta una carpeta intermedia sin
        `index.md` para cortar la cadena, y abajo todo puede estar perfectamente indexado
        contra un índice al que nadie llega. El contenido existe, el gate da verde y el agente
        nunca lo encuentra, que es la única forma de fallar que importa en una capa de
        contexto.
        """
        seen: set[Path] = set()
        queue = [root.resolve()]
        while queue:                                   # BFS con visited-set: los cross-links
            cur = queue.pop()                          # entre conceptos hacen ciclos.
            if cur in seen or not cur.is_file():
                continue
            seen.add(cur)
            try:
                text = cur.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in LINK_RE.finditer(strip_code(text)):
                tgt = m.group(1).strip().split("#", 1)[0]
                if not tgt or tgt.startswith(URL_PREFIXES) or tgt.startswith("/"):
                    continue
                dest = (cur.parent / tgt).resolve()
                if dest.is_dir():                      # link a carpeta ⇒ entra por su índice
                    dest = dest / "index.md"
                try:                                   # nunca salir del bundle
                    dest.relative_to(self.bundle.resolve())
                except ValueError:
                    continue
                queue.append(dest)
        for p in sorted(self.bundle.rglob("*.md")):
            if self._ignored(p) or p.name in RESERVED or not is_concept(p):
                continue
            if p.resolve() not in seen:
                self.add("WARN", p, 0,
                         "no se llega a este concepto navegando desde el index.md raíz "
                         "(subárbol invisible: existe y nadie lo encuentra)", rid="unreachable")

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
        for sev, rel, line, msg, rid in sorted(self.issues, key=lambda x: (x[1], x[2])):
            loc = f"{rel}:{line}" if line else rel
            # El id va en la salida para que se pueda copiar a `--skip` sin adivinarlo.
            print(f"  {sev:5} {loc} — {msg} [{rid}]")
        if not self.issues:
            print("  (sin problemas)")
        print(f"\nokf_lint: {len(errors)} error(es), {len(warns)} warning(s) en '{self.bundle}'")
        if errors or (warns and self.strict):
            return 1
        return 0


def pack(bundle: Path) -> int:
    """Emite el bundle entero como UN markdown, cada archivo una sola vez.

    Sirve para dárselo a una IA de una sentada (o para medir su tamaño) sin depender de una
    herramienta externa de npm.

    La decisión que hace que esto no sea un `cat *.md` es de `resolve.js` de speccy:
    **cada archivo se inlinea UNA vez y los links entre ellos quedan como punteros**. Un pack
    que inline cada link produce N copias del mismo concepto — o sea, fabrica la deriva que
    el kit existe para evitar, dentro del propio archivo que se le da al agente.

    El recorrido es el mismo BFS de alcanzabilidad, así que el orden del pack es el orden en
    que se navega desde la raíz, y lo inalcanzable queda al final y **señalado**: si el pack
    lo mostrara mezclado, taparía el problema que el linter reporta.
    """
    # Todo resuelto desde el arranque: el BFS compara rutas absolutas y `_ignored` hace
    # `relative_to`, así que mezclar relativas con absolutas revienta.
    bundle = bundle.resolve()
    root = bundle / "index.md"
    if not root.is_file():
        print(f"okf_lint: {bundle}/index.md no existe — sin raíz no hay orden de navegación",
              file=sys.stderr)
        return 2
    lint = Linter(bundle)
    order: list[Path] = []
    seen: set[Path] = set()
    queue = [root.resolve()]
    while queue:
        cur = queue.pop(0)                       # FIFO: el orden de lectura, no el de pila
        if cur in seen or not cur.is_file() or cur.suffix != ".md":
            continue
        try:
            cur.relative_to(bundle)
        except ValueError:
            continue                             # nunca sale del bundle
        if lint._ignored(cur):
            continue
        seen.add(cur); order.append(cur)
        for m in LINK_RE.finditer(strip_code(cur.read_text(encoding="utf-8", errors="replace"))):
            tgt = m.group(1).strip().split("#", 1)[0]
            if not tgt or tgt.startswith(URL_PREFIXES) or tgt.startswith("/"):
                continue
            dest = (cur.parent / tgt).resolve()
            queue.append(dest / "index.md" if dest.is_dir() else dest)

    rest = [p for p in sorted(bundle.rglob("*.md"))
            if not lint._ignored(p) and p.resolve() not in seen]
    # `log.md` y compañía NO se linkean desde el índice por diseño: marcarlos como
    # inalcanzables sería una falsa alarma que hace creer que el bundle está roto.
    extra = [p for p in rest if p.name in RESERVED]
    unreachable = [p for p in rest if p.name not in RESERVED]
    out = [f"# Bundle empaquetado: {bundle.name}\n",
           f"_{len(order)} archivos alcanzables desde index.md" +
           (f", {len(unreachable)} INALCANZABLES" if unreachable else "") + "._\n"]
    for group, files in (("", order), ("Archivos reservados (no se linkean por diseño)", extra),
                         ("INALCANZABLES desde index.md — el agente no llega a esto", unreachable)):
        if not files:
            continue
        if group:
            out.append(f"\n---\n\n# {group}\n")
        for f in files:
            out.append(f"\n---\n\n## `{f.relative_to(bundle).as_posix()}`\n")
            out.append(f.read_text(encoding="utf-8", errors="replace").rstrip() + "\n")
    text = "".join(out)
    print(text)
    print(f"okf_lint --pack: {len(order) + len(rest)} archivos, {len(text)} chars "
          f"(~{len(text) // 4} tokens)", file=sys.stderr)
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:]]
    strict = "--strict" in args
    if strict:
        args.remove("--strict")
    # `--skip id1,id2`: callar una regla por su id estable, sin forkear el kit. Los ids se
    # imprimen entre corchetes en cada hallazgo, así que se copian de la salida.
    skip: tuple[str, ...] = ()
    for a in list(args):
        if a.startswith("--skip="):
            skip += tuple(x.strip() for x in a.split("=", 1)[1].split(",") if x.strip())
            args.remove(a)
        elif a == "--skip":
            i = args.index(a)
            if i + 1 >= len(args):
                print("okf_lint: --skip necesita una lista de ids (ej: --skip dir-empty,log-date-iso)",
                      file=sys.stderr)
                return 2
            skip += tuple(x.strip() for x in args[i + 1].split(",") if x.strip())
            del args[i:i + 2]
    do_pack = "--pack" in args
    if do_pack:
        args.remove("--pack")
    bundle = Path(args[0]) if args else Path("knowledge")
    if do_pack:
        return pack(bundle)
    return Linter(bundle, strict=strict, skip=skip).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
