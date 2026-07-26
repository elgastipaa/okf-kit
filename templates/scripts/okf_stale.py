#!/usr/bin/env python3
"""okf_stale.py — ¿dónde conviene buscar divergencia entre el bundle y el código?

NO es un linter y NO da pass/fail: `okf_lint.py` responde "¿es OKF válido?", esto responde
"¿por dónde empiezo a buscar drift?". Auditar un bundle entero contra el código es caro —
por eso las auditorías no se corren— así que este script convierte "revisá todo, alguna vez"
en una lista corta y ordenada, calculada **sin leer código y sin gastar un token**: solo
git + el frontmatter que el bundle ya tiene.

Usa dos señales:

1. **`resource:` que ya no existe** → drift CONFIRMADO, no sospecha. El concepto apunta a un
   archivo que se movió o se borró. Es gratis de detectar y siempre es un hallazgo real.
2. **`timestamp` anterior al último commit del propio concepto, con ≥2 commits** → el sello
   de frescura está podrido: alguien **editó** el concepto sin actualizarlo (un concepto
   creado con fecha retroactiva no cuenta: es legítimo), así que las otras señales (que se
   calculan *desde* ese timestamp) están midiendo mal. Se detecta en la primera corrida real
   de este script, sobre su propio repo.
3. **Churn desde el `timestamp`** → cuántos commits tocaron esa fuente desde que el concepto
   se escribió. No prueba que el concepto esté mal: dice dónde es más probable que lo esté.

Los conceptos sin `resource:` local no se pueden rankear así, y **no quedan invisibles**:
salen en su propio bloque ordenados por antigüedad.

Uso:
    okf_stale.py [bundle] [--top N] [--repo DIR]

Exit: 0 siempre que pueda correr (no es un gate). 2 si no hay git o no encuentra el bundle.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RESERVED = {"index.md", "log.md"}


def frontmatter(text: str) -> dict[str, str]:
    """Claves de primer nivel del frontmatter. Sin PyYAML, igual que okf_lint."""
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([a-z_][a-z0-9_]*):\s*(.*)$", line)
        if km:
            out[km.group(1)] = km.group(2).strip().strip("\"'")
    return out


def concepts(bundle: Path):
    for p in sorted(bundle.rglob("*.md")):
        if p.name in RESERVED or any(part.startswith("_") for part in p.relative_to(bundle).parts):
            continue
        yield p


def git(repo: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def resolve(repo: Path, concept: Path, resource: str) -> Path | None:
    """`resource` puede ser relativo a la raíz del repo o al concepto. URLs no aplican."""
    if not resource or re.match(r"^[a-z]+://", resource):
        return None
    for cand in (repo / resource, concept.parent / resource):
        if cand.exists():
            return cand.resolve()
    return (repo / resource).resolve()  # inexistente: lo devolvemos para poder reportarlo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", nargs="?", default="knowledge")
    ap.add_argument("--top", type=int, default=10, help="cuántos sospechosos listar (default 10)")
    ap.add_argument("--repo", default=".", help="raíz del repo (default: cwd)")
    ap.add_argument("--rotate", action="store_true",
                    help="rota la ventana de los conceptos sin fuente por semana ISO, para que\ncon el tiempo se cubran todos en vez de mirar siempre los mismos")
    a = ap.parse_args()

    repo, bundle = Path(a.repo).resolve(), Path(a.bundle)
    if not bundle.is_dir():
        print(f"no encuentro el bundle '{bundle}'", file=sys.stderr)
        return 2
    if git(repo, "rev-parse", "--git-dir") is None:
        print("esto necesita un repo git (usa el historial para medir churn)", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    broken, unstamped, suspects, no_source = [], [], [], []

    for c in concepts(bundle):
        fm = frontmatter(c.read_text(encoding="utf-8", errors="replace"))
        ts = parse_ts(fm.get("timestamp", ""))
        days = (now - ts).days if ts else None
        rel = c.relative_to(bundle).as_posix()
        res = fm.get("resource", "")
        target = resolve(repo, c, res)

        if res and target is not None and not target.exists():
            broken.append((rel, res))
            continue

        # El sello de frescura miente si el concepto se commiteó después de su propio
        # timestamp: todas las señales de abajo se calculan DESDE ese valor. Se compara por
        # DÍA, no por instante: los timestamps se escriben a medianoche y el commit del mismo
        # día llega horas después — marcarlo sería un falso positivo, y un detector que
        # inventa hallazgos se deja de correr.
        # Solo cuenta si el concepto se MODIFICÓ después (≥2 commits): un concepto creado con
        # timestamp retroactivo —fechado el día en que se decidió la cosa, commiteado después—
        # es legítimo y frecuente, y marcarlo taparía su clasificación real.
        if ts is not None:
            ncommits = git(repo, "rev-list", "--count", "HEAD", "--", str(c.resolve()))
            last = git(repo, "log", "-1", "--format=%aI", "--", str(c.resolve()))
            last_dt = parse_ts(last) if last else None
            if last_dt and last_dt.date() > ts.date() and (ncommits or "0").isdigit() and int(ncommits or 0) >= 2:
                unstamped.append((rel, ts.date().isoformat(), last_dt.date().isoformat()))
                continue
        if target is None or ts is None:
            no_source.append((days if days is not None else -1, rel,
                              "sin resource local" if target is None else "timestamp inválido"))
            continue

        rel_target = target.relative_to(repo).as_posix() if target.is_relative_to(repo) else str(target)
        n = git(repo, "rev-list", "--count", "HEAD", f"--since={ts.isoformat()}", "--", rel_target)
        churn = int(n) if n and n.isdigit() else 0
        suspects.append((churn, days, rel, rel_target))

    print(f"okf_stale — bundle '{bundle}' · {len(broken)+len(unstamped)+len(suspects)+len(no_source)} conceptos\n")

    if broken:
        print("DRIFT CONFIRMADO — el `resource` ya no existe (se movió o se borró)")
        for rel, res in broken:
            print(f"  {rel}\n      resource: {res}")
        print()

    if unstamped:
        print("SELLO PODRIDO — el concepto se editó después de su propio `timestamp`")
        print("  (las demás señales se calculan desde ese valor, así que miden mal)")
        for rel, declared, real in unstamped:
            print(f"  {rel}\n      declara {declared} · último commit {real}")
        print()

    if suspects:
        suspects.sort(key=lambda r: (-r[0], -(r[1] or 0)))
        shown = [s for s in suspects if s[0] > 0][: a.top]
        if shown:
            print("SOSPECHOSOS — la fuente cambió desde que se escribió el concepto")
            print(f"  {'commits':>7} {'días':>5}  concepto → resource")
            for churn, days, rel, tgt in shown:
                print(f"  {churn:>7} {days if days is not None else '?':>5}  {rel} → {tgt}")
            print()
        quiet = len(suspects) - len(shown)
        if quiet:
            print(f"  ({quiet} conceptos con fuente sin cambios desde su timestamp — nada que mirar)\n")

    if no_source:
        no_source.sort(key=lambda r: -r[0])
        # Sin --rotate se ven siempre los más viejos: si esos están bien, tapan al resto para
        # siempre. Rotando por semana ISO la cobertura avanza, y sigue siendo reproducible
        # dentro de la misma semana (dos corridas el mismo día dan lo mismo).
        window = no_source
        if a.rotate and len(no_source) > a.top:
            off = (now.isocalendar().week * a.top) % len(no_source)
            window = no_source[off:] + no_source[:off]
        etiqueta = "por antigüedad, ventana rotada por semana" if a.rotate else "por antigüedad"
        print(f"SIN FUENTE LOCAL — no se pueden rankear por churn; van {etiqueta}")
        for days, rel, why in window[: a.top]:
            print(f"  {days if days >= 0 else '?':>5} días  {rel}  ({why})")
        print()

    print("Esto NO dice que estos conceptos estén mal: dice dónde es más probable que lo estén.")
    print("Confirmarlo requiere leer el código — `okf-verify` Nivel 2 (drift descriptivo) y")
    print("Nivel 4 (cumplimiento). Y quién tiene razón, el doc o el código, lo decide el usuario.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
