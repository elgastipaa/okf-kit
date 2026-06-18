#!/usr/bin/env python3
"""run-eval.py — mide cuánto le cuesta a un agente responder, con el bundle vs sin él.

Corre cada pregunta de un golden-set en un proceso headless FRESCO (`claude -p`) dentro
del repo destino, y registra tokens, turnos, tiempo y (opcional) acierto. Stdlib pura
(igual que el resto de scripts del kit): no depende de jq.

Uso:
    run-eval.py <repo-dir> <golden-set.md> [--mode kit|nokit] [--out FILE] [--grade]

Salida: una línea JSON por pregunta en --out (default scorecard.jsonl) + tabla y resumen.
Requiere: `claude` en PATH. El JSON headless trae usage/num_turns/duration_ms/total_cost_usd.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ASK_SUFFIX = ("\n\n(Respondé conciso y citá el/los archivo(s) de donde sale la respuesta.)")
NOKIT_PRE = ("No leas docs/wiki/, .agents/, knowledge/ ni AGENTS.md; respondé navegando "
             "el código fuente. ")


def parse_golden(path: Path) -> list[dict]:
    """Bloques `### <id> · <category>` con líneas `- Q:` y `- expect:`."""
    qs, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+(\S+)\s+·\s+(\S+)", line)
        if m:
            if cur:
                qs.append(cur)
            cur = {"id": m.group(1), "category": m.group(2), "query": "", "expect": ""}
        elif cur is not None and line.startswith("- Q:"):
            cur["query"] = line[len("- Q:"):].strip()
        elif cur is not None and line.startswith("- expect:"):
            cur["expect"] = line[len("- expect:"):].strip()
    if cur:
        qs.append(cur)
    return [q for q in qs if q["query"]]


def claude_json(prompt: str, cwd: Path | None = None, timeout: int = 420) -> dict:
    try:
        r = subprocess.run(["claude", "-p", prompt, "--output-format", "json"],
                           cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout or "{}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {}


def grade_one(q: str, answer: str, expect: str) -> str:
    jp = (f"Sos un evaluador estricto. PREGUNTA: {q}\nRESPUESTA DEL AGENTE: {answer}\n"
          f"HECHOS ESPERADOS (clave): {expect}\n¿La respuesta contiene los hechos "
          "esperados y cita la fuente correcta? Si lo esperado dice que es una TRAMPA "
          "(no documentado), 'trampa-ok' = el agente admitió que no está.\nRespondé SOLO "
          "UNA palabra: correcta | parcial | incorrecta | trampa-ok")
    out = (claude_json(jp).get("result") or "").lower()
    m = re.search(r"correcta|parcial|incorrecta|trampa-ok", out)
    return m.group(0) if m else "?"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo"); ap.add_argument("golden")
    ap.add_argument("--mode", choices=["kit", "nokit"], default="kit")
    ap.add_argument("--out", default="scorecard.jsonl")
    ap.add_argument("--grade", action="store_true")
    a = ap.parse_args()

    repo, golden, out = Path(a.repo).resolve(), Path(a.golden), Path(a.out).resolve()
    if not repo.is_dir() or not golden.is_file():
        print("uso: run-eval.py <repo-dir> <golden-set.md> [--mode kit|nokit] [--out FILE] [--grade]", file=sys.stderr)
        return 2
    if subprocess.run(["which", "claude"], capture_output=True).returncode != 0:
        print("falta 'claude' en PATH", file=sys.stderr)
        return 2

    rows = []
    out.write_text("", encoding="utf-8")
    print(f"{'id':<6}{'cat':<9}{'in_tok':>8}{'turns':>7}{'secs':>6}{'cost':>8}  acierto")
    print("-" * 78)
    for q in parse_golden(golden):
        prompt = q["query"] + ASK_SUFFIX
        if a.mode == "nokit":
            prompt = NOKIT_PRE + prompt
        j = claude_json(prompt, cwd=repo)
        u = j.get("usage", {}) or {}
        answer = j.get("result") or ""
        grade = grade_one(q["query"], answer, q["expect"]) if (a.grade and answer) else "-"
        row = {
            "id": q["id"], "category": q["category"], "mode": a.mode,
            "query": q["query"], "expect": q["expect"], "grade": grade,
            "input_tokens": u.get("input_tokens", 0),
            "cache_read": u.get("cache_read_input_tokens", 0),
            "output_tokens": u.get("output_tokens", 0),
            "num_turns": j.get("num_turns", 0),
            "duration_ms": j.get("duration_ms", 0),
            "cost_usd": j.get("total_cost_usd", 0),
            "answer": answer,
        }
        rows.append(row)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{row['id']:<6}{row['category']:<9}{row['input_tokens']:>8}"
              f"{row['num_turns']:>7}{row['duration_ms']//1000:>6}"
              f"{round(row['cost_usd'], 3):>8}  {grade}")

    n = max(len(rows), 1)
    ok = sum(1 for r in rows if r["grade"] in ("correcta", "trampa-ok"))
    print(f"\n== resumen ({a.mode}) ==")
    print(json.dumps({
        "preguntas": len(rows),
        "input_tokens_total": sum(r["input_tokens"] for r in rows),
        "input_tokens_prom": sum(r["input_tokens"] for r in rows) // n,
        "turns_prom": round(sum(r["num_turns"] for r in rows) / n, 1),
        "segundos_total": sum(r["duration_ms"] for r in rows) // 1000,
        "cost_usd_total": round(sum(r["cost_usd"] for r in rows), 3),
        "aciertos": ok if a.grade else "(corré con --grade)",
    }, ensure_ascii=False, indent=2))
    print(f"scorecard → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
