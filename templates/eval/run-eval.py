#!/usr/bin/env python3
"""run-eval.py — mide cuánto le cuesta a un agente responder, con el bundle vs sin él.

Corre cada pregunta de un golden-set en un proceso headless FRESCO (`claude -p`) dentro
del repo destino, y registra tokens, turnos, tiempo y (opcional) acierto. Stdlib pura
(igual que el resto de scripts del kit): no depende de jq.

Uso:
    run-eval.py <repo-dir> <golden-set.md> [--mode kit|nokit|agentsmd] [--repeat N]
                [--out FILE] [--grade] [--layer PATH ...] [--agentsmd-file FILE]

Salida: una línea JSON por CORRIDA en --out (default scorecard.jsonl) + tabla y resumen.
Con --repeat N > 1 el resumen agrega por pregunta (mediana y dispersión) — que es la
única forma de distinguir una mejora real del ruido: en las mediciones de este kit el
ruido intra-condición fue de ~3,3 turnos por pregunta, así que un efecto medido con n=1
y menor a eso no es un efecto, es una corrida.

Requiere: `claude` en PATH (o el comando que indique OKF_EVAL_CLI).
El JSON headless trae usage/num_turns/duration_ms/total_cost_usd.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ASK_SUFFIX = ("\n\n(Respondé conciso y citá el/los archivo(s) de donde sale la respuesta.)")

# Lo que se APARTA del repo en los modos de comparación. No se le pide al agente que
# ignore la capa: pedírselo no mide "sin kit" — Claude Code auto-carga el contrato en el
# prefijo antes de que el agente decida nada, así que el brazo quedaba contaminado.
DEFAULT_LAYERS = ["knowledge", "AGENTS.md", "CLAUDE.md", "docs/wiki", ".agents"]

# El comando del juez/agente es configurable para poder correr el veredicto cross-vendor
# que `grade.md` exige. No viola la decisión de vendor-neutralidad: este harness es
# tooling de desarrollo opt-in que NO se instala en el repo destino.
CLI = os.environ.get("OKF_EVAL_CLI", "claude")


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


def claude_json(prompt: str, cwd: Path | None = None, timeout: int = 420) -> dict | None:
    """El JSON de `claude -p`, o **None si la corrida falló**.

    Devolver `{}` ante un fallo sería el peor bug posible en un harness de medición: una
    corrida que no corrió quedaría indistinguible de una que midió cero, y el scorecard
    saldría lleno de ceros con exit 0 — números que parecen datos. Acá el fallo se
    propaga y el error de `claude` se ve.
    """
    try:
        r = subprocess.run([CLI, "-p", prompt, "--output-format", "json"],
                           cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"  ! {CLI} excedió el timeout de {timeout}s", file=sys.stderr)
        return None
    except OSError as e:
        print(f"  ! no se pudo ejecutar {CLI}: {e}", file=sys.stderr)
        return None
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().splitlines()
        print(f"  ! {CLI} salió con código {r.returncode}: {err[-1] if err else '(sin salida)'}",
              file=sys.stderr)
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        head = (r.stdout or "").strip()[:200]
        print(f"  ! la salida de {CLI} no es JSON: {head!r}", file=sys.stderr)
        return None


def grade_one(q: str, answer: str, expect: str, repo: Path) -> dict:
    """Dos veredictos, verificando contra el código — no contra el parecido de texto.

    Corre **con `cwd=repo`**: sin eso el juez se ejecuta en el directorio del harness y no
    puede abrir ni un archivo del repo bajo prueba, así que degrada a matcheo de paráfrasis
    (y si usara tools, grepearía el repo equivocado).

    El segundo veredicto existe porque el primero no puede verlo: una respuesta que acepta
    una **premisa falsa de la pregunta** puede contener igual todos los hechos del `expect`,
    y salía `correcta`. Es el falso positivo que ya se documentó en el bundle.
    """
    jp = (
        "Sos un evaluador estricto y estás parado en el repo bajo prueba. **Verificá contra "
        "el código** antes de dictaminar: abrí los archivos que haga falta. No juzgues por "
        "parecido de texto.\n\n"
        f"PREGUNTA: {q}\n\nRESPUESTA DEL AGENTE: {answer}\n\n"
        f"HECHOS ESPERADOS (referencia, puede estar incompleta o decir 'a verificar contra "
        f"código'; ante la duda **manda el código**, no este campo): {expect}\n\n"
        "Dictaminá DOS cosas:\n"
        "1. hechos — correcta | parcial | incorrecta | trampa-ok | no-hay-razon-ok | inventada\n"
        "   'trampa-ok' = lo esperado dice que es una TRAMPA porque no existe, y el agente lo "
        "admitió.\n"
        "   Para preguntas de POR QUÉ, donde el ground truth lo dio una persona y el código NO "
        "contiene la razón:\n"
        "   'no-hay-razon-ok' = lo esperado dice que NO HAY una razón registrada, y el agente "
        "lo admitió en vez de inventar. Es CORRECTO.\n"
        "   'inventada' = el agente dio una explicación plausible que NO es la razón esperada, "
        "cuando lo esperado decía que no hay razón registrada. Suena bien y es falsa: es el "
        "peor resultado posible, peor que equivocarse, porque nadie la va a chequear.\n"
        "2. premisa — la PREGUNTA puede dar por sentado algo que en el código es FALSO. "
        "premisa-ok = no había premisa falsa, o el agente la corrigió. "
        "premisa-falsa-aceptada = el agente le siguió la corriente a algo que no existe.\n\n"
        "Respondé EXACTAMENTE dos líneas, sin nada más:\n"
        "hechos: <valor>\npremisa: <valor>"
    )
    j = claude_json(jp, cwd=repo)
    if j is None:
        return {"grade": "?", "premise": "?", "cost": 0.0, "turns": 0}
    out = (j.get("result") or "").lower()
    mg = re.search(r"no-hay-razon-ok|trampa-ok|incorrecta|inventada|correcta|parcial", out)
    mp = re.search(r"premisa-falsa-aceptada|premisa-ok", out)
    return {
        "grade": mg.group(0) if mg else "?",
        "premise": mp.group(0) if mp else "?",
        # El costo del juez es costo de la medición. Descartarlo hacía que una corrida
        # --grade subreportara ~1 llamada por pregunta.
        "cost": j.get("total_cost_usd", 0) or 0,
        "turns": j.get("num_turns", 0) or 0,
    }


# ---------------------------------------------------------------- brazos comparativos

def repo_fingerprint(repo: Path) -> str:
    """El estado del repo bajo prueba, para detectar si una corrida lo modificó.

    `claude -p` tiene herramientas de EDICIÓN, así que un agente contestando una pregunta
    puede "mejorar" un concepto del bundle mientras lo lee. Pasó de verdad: una corrida
    editó un concepto con datos que acababa de encontrar en el código. Eso cambia la
    condición **entre réplicas y entre brazos**, y una medición cuya condición se mueve sola
    no mide nada.
    """
    r = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def _git_out(repo: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout or "")


def check_recoverable(repo: Path, layers: list[str]) -> str | None:
    """¿Se puede apartar la capa sin arriesgar trabajo del usuario? Devuelve el motivo si NO.

    Regla: solo movemos archivos que git puede devolver. Si el repo no es git, o si la capa
    tiene cambios sin commitear, un corte de luz a mitad de la corrida dejaría al usuario sin
    su contexto y sin forma de recuperarlo. Ese trade no lo decide un harness de medición.
    """
    if _git_out(repo, "rev-parse", "--git-dir")[0] != 0:
        return (f"{repo} no es un repo git. Este modo aparta archivos del repo y los "
                "restaura al terminar; sin git no hay red si algo se corta.")
    present = [l for l in layers if (repo / l).exists()]
    if not present:
        return (f"ninguna de las capas {layers} existe en {repo}: no hay nada que apartar, "
                "así que este brazo mediría lo mismo que --mode kit.")
    code, dirty = _git_out(repo, "status", "--porcelain", "--", *present)
    if code != 0:
        return "no se pudo consultar `git status` sobre las capas"
    if dirty.strip():
        return ("hay cambios sin commitear en la capa que hay que apartar:\n"
                + "\n".join(f"    {l}" for l in dirty.strip().splitlines())
                + "\n  Commiteá o guardá eso antes de medir: el harness no mueve trabajo "
                  "que git no pueda devolver.")
    return None


class HiddenLayer:
    """Aparta la capa de contexto del repo mientras dura la corrida, y la devuelve siempre.

    El `finally` cubre también Ctrl-C y una excepción del harness. Si aun así algo queda a
    medias, imprime la ruta exacta del respaldo y el `git checkout` que lo arregla — nunca
    deja al usuario adivinando qué se movió.
    """

    def __init__(self, repo: Path, layers: list[str]):
        self.repo, self.layers, self.moved, self.tmp = repo, layers, [], None

    def __enter__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="okf-eval-hidden-"))
        for rel in self.layers:
            src = self.repo / rel
            if not src.exists():
                continue
            dst = self.tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            self.moved.append(rel)
        print(f"  · apartadas {len(self.moved)} rutas de la capa → {self.tmp}")
        return self

    def __exit__(self, *exc):
        failed = []
        for rel in self.moved:
            src, dst = self.tmp / rel, self.repo / rel
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
                shutil.move(str(src), str(dst))
            except OSError as e:
                failed.append(f"{rel}: {e}")
        if failed:
            print("\n*** NO SE PUDO RESTAURAR TODA LA CAPA:", file=sys.stderr)
            for f in failed:
                print(f"      {f}", file=sys.stderr)
            print(f"    Respaldo intacto en: {self.tmp}\n"
                  f"    O recuperala con: git -C {self.repo} checkout -- "
                  + " ".join(self.moved), file=sys.stderr)
            return False
        shutil.rmtree(self.tmp, ignore_errors=True)
        print(f"  · capa restaurada ({len(self.moved)} rutas)")
        return False


def install_plain_agents(repo: Path, src: Path) -> None:
    """Deja el AGENTS.md convencional del brazo de comparación (la capa ya está apartada)."""
    shutil.copyfile(src, repo / "AGENTS.md")


# ------------------------------------------------------------------------- agregación

def aggregate(rows: list[dict]) -> list[dict]:
    """Por pregunta: mediana y dispersión de turnos. Con n=1 la dispersión no existe y se
    dice explícitamente — un número sin dispersión no se puede comparar contra otro."""
    by_id: dict[str, list[dict]] = {}
    for r in rows:
        if not r["failed"]:
            by_id.setdefault(r["id"], []).append(r)
    aggs = []
    for qid, rs in by_id.items():
        t = sorted(r["num_turns"] for r in rs)
        grades = [r["grade"] for r in rs if r["grade"] not in ("-", "?")]
        aggs.append({
            "id": qid, "category": rs[0]["category"], "n": len(rs),
            "turns_mediana": statistics.median(t),
            "turns_min": t[0], "turns_max": t[-1],
            "turns_spread": t[-1] - t[0],
            "ctx_tok_mediana": statistics.median(sorted(r["cache_read"] for r in rs)),
            "seg_mediana": statistics.median(sorted(r["duration_ms"] for r in rs)) // 1000,
            # Un desacuerdo entre réplicas es la señal de que hay que verificar a mano.
            "acierto_estable": (len(set(grades)) <= 1) if grades else None,
            "grades": grades,
        })
    return sorted(aggs, key=lambda a: a["id"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo"); ap.add_argument("golden")
    ap.add_argument("--mode", choices=["kit", "nokit", "agentsmd"], default="kit")
    ap.add_argument("--repeat", type=int, default=1,
                    help="corridas por pregunta (n>=3 para poder comparar contra el ruido)")
    ap.add_argument("--out", default="scorecard.jsonl")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--layer", action="append", default=None,
                    help=f"ruta de la capa a apartar (repetible). Default: {DEFAULT_LAYERS}")
    ap.add_argument("--agentsmd-file",
                    help="el AGENTS.md convencional a usar en --mode agentsmd")
    a = ap.parse_args()

    repo, golden, out = Path(a.repo).resolve(), Path(a.golden), Path(a.out).resolve()
    if not repo.is_dir() or not golden.is_file():
        print("uso: run-eval.py <repo-dir> <golden-set.md> [--mode kit|nokit|agentsmd] "
              "[--repeat N] [--out FILE] [--grade]", file=sys.stderr)
        return 2
    if a.repeat < 1:
        print("--repeat tiene que ser >= 1", file=sys.stderr)
        return 2
    # shutil.which y no `which`: el binario no existe en todos los contenedores mínimos
    # (ni en Windows), y este harness tiene que poder correr en un runner de CI pelado.
    if shutil.which(CLI) is None:
        print(f"falta '{CLI}' en PATH", file=sys.stderr)
        return 2

    layers = a.layer or DEFAULT_LAYERS
    plain = None
    if a.mode in ("nokit", "agentsmd"):
        why = check_recoverable(repo, layers)
        if why:
            print(f"no se puede correr --mode {a.mode}: {why}", file=sys.stderr)
            return 2
    if a.mode == "agentsmd":
        # No se fabrica el brazo de comparación: el AGENTS.md "convencional" es una decisión
        # del que mide (qué pondría un dev normal en ESTE repo), no algo que el harness pueda
        # inventar sin sesgar el resultado a favor del kit.
        if not a.agentsmd_file:
            print("--mode agentsmd necesita --agentsmd-file FILE: el AGENTS.md convencional "
                  "contra el que se compara lo escribís vos (es la condición de control), no "
                  "lo genera el harness.", file=sys.stderr)
            return 2
        plain = Path(a.agentsmd_file).resolve()
        if not plain.is_file():
            print(f"no existe {plain}", file=sys.stderr)
            return 2

    questions = parse_golden(golden)
    rows: list[dict] = []
    judge_cost = judge_turns = 0.0
    out.write_text("", encoding="utf-8")

    def run_all() -> None:
        nonlocal judge_cost, judge_turns
        # `ctx_tok` = cache_read: el contexto que el agente REALMENTE leyó (85K-300K). El
        # `input_tokens` de la API son los tokens no-cacheados del último turno (6-12): ruido.
        print(f"{'id':<6}{'rep':<5}{'cat':<9}{'ctx_tok':>9}{'turns':>7}{'secs':>6}"
              f"{'cost':>8}  acierto")
        print("-" * 84)
        for q in questions:
            for rep in range(1, a.repeat + 1):
                before = repo_fingerprint(repo)
                j = claude_json(q["query"] + ASK_SUFFIX, cwd=repo)
                after = repo_fingerprint(repo)
                mutated = before != after
                if mutated:
                    print(f"  ! {q['id']} rep{rep}: LA CORRIDA MODIFICÓ EL REPO — la condición "
                          "cambió a mitad de la medición. Revisá `git status` y revertí antes "
                          "de comparar nada.", file=sys.stderr)
                failed = j is None
                j = j or {}
                u = j.get("usage", {}) or {}
                answer = j.get("result") or ""
                g = (grade_one(q["query"], answer, q["expect"], repo)
                     if (a.grade and answer) else
                     {"grade": "-", "premise": "-", "cost": 0.0, "turns": 0})
                judge_cost += g["cost"]; judge_turns += g["turns"]
                row = {
                    "id": q["id"], "category": q["category"], "mode": a.mode, "rep": rep,
                    "query": q["query"], "expect": q["expect"],
                    "grade": g["grade"], "premise": g["premise"],
                    "judge_cost_usd": g["cost"], "judge_turns": g["turns"],
                    "failed": failed, "mutated_repo": mutated,
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
                if failed:
                    print(f"{row['id']:<6}{rep:<5}{row['category']:<9}"
                          f"{'ERROR — la corrida falló':>29}")
                else:
                    flag = " ⚠premisa" if g["premise"] == "premisa-falsa-aceptada" else ""
                    print(f"{row['id']:<6}{rep:<5}{row['category']:<9}{row['cache_read']:>9}"
                          f"{row['num_turns']:>7}{row['duration_ms']//1000:>6}"
                          f"{round(row['cost_usd'], 3):>8}  {g['grade']}{flag}")

    if a.mode in ("nokit", "agentsmd"):
        with HiddenLayer(repo, layers):
            if plain:
                install_plain_agents(repo, plain)
            try:
                run_all()
            finally:
                if plain and (repo / "AGENTS.md").exists():
                    (repo / "AGENTS.md").unlink()
    else:
        run_all()

    # Los promedios se calculan SOLO sobre las corridas que de verdad corrieron: promediar
    # ceros de corridas fallidas produce un número más lindo y mentiroso.
    good = [r for r in rows if not r["failed"]]
    bad = len(rows) - len(good)
    n = max(len(good), 1)
    ok = sum(1 for r in good if r["grade"] in ("correcta", "trampa-ok", "no-hay-razon-ok"))
    invented = sum(1 for r in good if r["grade"] == "inventada")
    mutated_runs = sum(1 for r in rows if r.get("mutated_repo"))
    premise_bad = sum(1 for r in good if r["premise"] == "premisa-falsa-aceptada")
    aggs = aggregate(rows)

    if a.repeat > 1:
        print(f"\n== por pregunta (n={a.repeat}) ==")
        print(f"{'id':<6}{'cat':<9}{'mediana':>9}{'min':>6}{'max':>6}{'spread':>8}  acierto")
        print("-" * 66)
        for g in aggs:
            est = "" if g["acierto_estable"] in (True, None) else "  ⚠ INESTABLE " + \
                  "/".join(g["grades"])
            print(f"{g['id']:<6}{g['category']:<9}{g['turns_mediana']:>9}"
                  f"{g['turns_min']:>6}{g['turns_max']:>6}{g['turns_spread']:>8}{est}")
        spreads = [g["turns_spread"] for g in aggs]
        ruido = round(statistics.mean(spreads), 2) if spreads else 0
        print(f"\n  Ruido observado (spread medio de turnos): {ruido}. Un efecto menor a esto "
              f"NO es distinguible del ruido con este n.")

    print(f"\n== resumen ({a.mode}) ==")
    print(json.dumps({
        "preguntas": len(questions),
        "repeticiones": a.repeat,
        "corridas": len(rows),
        "corridas_ok": len(good),
        "corridas_fallidas": bad,
        "ctx_tokens_prom": sum(r["cache_read"] for r in good) // n,
        "ctx_tokens_total": sum(r["cache_read"] for r in good),
        # se conserva para poder auditar la diferencia, pero NO es la métrica a comparar
        "input_tokens_prom_no_cacheados": sum(r["input_tokens"] for r in good) // n,
        "turns_prom": round(sum(r["num_turns"] for r in good) / n, 1),
        "turns_mediana_por_pregunta": (
            round(statistics.mean(g["turns_mediana"] for g in aggs), 2) if aggs else 0),
        "spread_medio_turnos": (
            round(statistics.mean(g["turns_spread"] for g in aggs), 2) if aggs else 0),
        "segundos_total": sum(r["duration_ms"] for r in good) // 1000,
        "cost_usd_total": round(sum(r["cost_usd"] for r in good) + judge_cost, 3),
        "cost_usd_juez": round(judge_cost, 3),
        "turnos_juez": judge_turns,
        "aciertos": ok if a.grade else "(corré con --grade)",
        "premisas_falsas_aceptadas": premise_bad if a.grade else "(corré con --grade)",
        # En preguntas de POR QUÉ este es el número que importa: explicaciones convincentes
        # y falsas sobre decisiones que nadie tomó deliberadamente.
        "explicaciones_inventadas": invented if a.grade else "(corré con --grade)",
        "corridas_que_MODIFICARON_el_repo": mutated_runs,
    }, ensure_ascii=False, indent=2))
    print(f"scorecard → {out}")

    if a.repeat < 3:
        print("\n  Nota: con --repeat 1 no hay dispersión, así que este scorecard no puede "
              "sostener una comparación entre condiciones — solo describe una corrida. "
              "Para comparar, n>=3.", file=sys.stderr)
    if mutated_runs:
        print(f"\n*** {mutated_runs} corrida(s) MODIFICARON el repo bajo prueba. La condición "
              "cambió a mitad de la medición, así que este scorecard NO es comparable con "
              "otro. Revertí el repo y volvé a correr.", file=sys.stderr)
    if a.grade and invented:
        print(f"\n*** {invented} explicación(es) INVENTADAS: el agente dio una razón plausible "
              "para algo que nadie decidió deliberadamente. Es el peor resultado del set — una "
              "explicación convincente y falsa no la chequea nadie.", file=sys.stderr)
    if a.grade and premise_bad:
        print(f"\n*** {premise_bad} respuesta(s) aceptaron una premisa falsa de la pregunta. "
              "Un contexto que hace contestar rápido y MAL es una regresión, por más que "
              "baje el promedio de turnos: verificalas a mano antes de publicar nada.",
              file=sys.stderr)
    if bad:
        print(f"\n*** {bad}/{len(rows)} corridas FALLARON — este scorecard NO es una medición "
              f"válida. Revisá los errores de arriba (auth, red, timeout) y volvé a correr.",
              file=sys.stderr)
        return 1
    if not rows:
        print("*** el golden-set no tiene preguntas parseables", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
