#!/usr/bin/env python3
"""okf_lint_test.py — ¿el linter REPORTA cuando tiene que reportar?

El `okf_lint.py` es la herramienta más usada del kit (corre en CI, en el pre-commit hook y
dentro de `okf-verify`) y era la única sin test de roturas: el `selfcheck` y el `okf_stale`
ya tenían el suyo. Un criterio de FAIL que nunca se probó rompiendo lo que dice cuidar es
decoración — la misma regla que `okf_selfcheck_test.py` aplica al gate.

Cada caso inyecta UNA rotura sobre una copia del bundle dogfood y verifica el veredicto y
que el mensaje sea el que corresponde (no alcanza con que falle: tiene que fallar *por eso*).
Los casos `expect=None` son **redacción legítima** que NO debe reportar nada.

Es kit-only (vive en `scripts/`, no en `templates/`) y no toca el repo real.

Uso:  python3 scripts/okf_lint_test.py
Exit: 0 si todos los casos se comportan como corresponde, 1 si alguno no.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
LINT = KIT / "templates" / "scripts" / "okf_lint.py"
CASES: list[tuple[str, str | None, object, tuple[str, ...], bool, int | None, bool]] = []


def case(name: str, expect: str | None, extra: list[str] | None = None,
         pack_unique: bool = False, questions_expect: int | None = None,
         budget_expect: bool = False):
    """expect = substring que el reporte DEBE contener; None = no debe reportar nada.

    `extra` = flags adicionales del linter para ese caso (p.ej. `--skip`)."""
    def deco(fn):
        CASES.append((name, expect, fn, tuple(extra or ()), pack_unique, questions_expect, budget_expect))
        return fn
    return deco


def edit(d: Path, rel: str, old: str, new: str) -> None:
    p = d / rel
    t = p.read_text(encoding="utf-8")
    if old not in t:
        raise AssertionError(f"el caso no aplica: no encontré en {rel}: {old[:50]!r}")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


def a_concept(d: Path) -> Path:
    return d / "decisions" / "0001-relative-links-over-absolute.md"


# ---- ERRORES (hacen fallar el linter incluso sin --strict)
@case("concepto sin `type`", "falta `type`")
def _(d): edit(d, "decisions/0001-relative-links-over-absolute.md", "type: Decision", "kind: Decision")


@case("cross-link absoluto (rompe en GitHub)", "link absoluto")
def _(d): edit(d, "index.md", "](decisions/index.md)", "](/decisions/index.md)")


@case("valor de frontmatter con `:` sin comillas", "sin comillas")
def _(d): edit(d, "roadmap.md", 'description: "Hacia', "description: Hacia")


@case("frontmatter sin cerrar", "sin cerrar")
def _(d):
    # Se borra SOLO el delimitador de cierre: borrar los dos daría "falta frontmatter",
    # que es otro criterio (y el caso pasaría por el motivo equivocado).
    p = a_concept(d)
    t = p.read_text(encoding="utf-8")
    close = t.index("\n---", 3)
    p.write_text(t[:close] + t[close + 4:], encoding="utf-8")


# ---- los tres chequeos que hasta 0.7.1 solo validaba el criterio humano
@case("`authority` con un valor fuera del vocabulario", "no está en el vocabulario")
def _(d): edit(d, "decisions/0012-descriptive-vs-normative.md",
               "type: Decision", "type: Decision\nauthority: banana")


@case("subcarpeta que el index del padre no lista (subárbol invisible)", "no está listada")
def _(d):
    # La PUERTA del index también linkea `decisions/index.md`, así que sacar la entrada del
    # listado ya no alcanza: hay que sacar las dos para que el subárbol quede invisible.
    p = d / "index.md"
    t = p.read_text(encoding="utf-8")
    p.write_text(t.replace("decisions/index.md", "decisions/index.md-x"), encoding="utf-8")


@case("entrada del index que divergió de la `description` del concepto", "no coincide")
def _(d): edit(d, "decisions/index.md", "Se usan links relativos", "Se usan links raros")


# ---- WARNs de siempre (se prueban porque --strict los vuelve bloqueantes)
@case("concepto no linkeado en el index de su carpeta", "no está linkeado")
def _(d): shutil.copy(a_concept(d), a_concept(d).with_name("9999-huerfano.md"))


@case("link relativo roto", "link roto")
def _(d): edit(d, "index.md", "](decisions/index.md)", "](decisiones/index.md)")


@case("heading de fecha no ISO en log.md", "no ISO")
def _(d): edit(d, "log.md", "## 2026-07-29", "## 29 de julio")


@case("carpeta vacía", "carpeta vacía")
def _(d): (d / "vacia").mkdir()


# ---- lo que la pasada adversarial de 0.7.3 encontró (falsos negativos del linter)
@case("`type:` sin espacio (escalar YAML, no mapping: no hay ninguna clave)", "no es 'clave: valor'")
def _(d): edit(d, "decisions/0001-relative-links-over-absolute.md", "type: Decision", "type:Decision")


@case("marcador de conflicto de merge sin resolver", "conflicto de merge")
def _(d): edit(d, "roadmap.md", "# Visión", "# Visión\n<<<<<<< HEAD\nuna cosa\n=======\notra cosa\n>>>>>>> rama")


@case("link absoluto escondido en un ítem de lista anidado", "link absoluto")
def _(d): edit(d, "index.md", "# Subdirectories",
               "# Subdirectories\n\n* nivel 1\n    * [absoluto](/knowledge/x.md) escondido")


# ---- REDACCIÓN LEGÍTIMA: no debe reportar nada
@case("bundle dogfood intacto", None)
def _(d): pass


@case("`authority` con un valor válido", None)
def _(d): edit(d, "decisions/0012-descriptive-vs-normative.md",
               "type: Decision", "type: Decision\nauthority: normative")


@case("entrada del index con énfasis markdown y em-dash", None)
def _(d): edit(d, "decisions/index.md",
               "- Se usan links relativos (../x.md) porque los absolutos (/x.md) rompen en GitHub.",
               "— Se usan links **relativos** (`../x.md`) porque los absolutos (/x.md) rompen en GitHub")


@case("entrada de index con la `description` envuelta en dos líneas", None)
def _(d):
    # Envolver prosa a 90 columnas es la norma (los docs del kit lo hacen). Cortar en el
    # primer \n daba un falso positivo que mostraba los dos textos IDÉNTICOS.
    edit(d, "decisions/index.md",
         "- Se usan links relativos (../x.md) porque los absolutos (/x.md) rompen en GitHub.",
         "- Se usan links relativos (../x.md) porque los absolutos\n  (/x.md) rompen en GitHub.")


@case("`authority` válido con un comentario YAML al lado", None)
def _(d): edit(d, "decisions/0012-descriptive-vs-normative.md", "type: Decision",
               "type: Decision\nauthority: normative   # la clase la da el type")


@case("carpeta que solo tiene index.md (sembrada, todavía sin conceptos)", None)
def _(d):
    (d / "domain").mkdir()
    (d / "domain" / "index.md").write_text("# Concept\n", encoding="utf-8")
    edit(d, "index.md", "# Subdirectories\n", "# Subdirectories\n\n* [domain](domain/index.md) - vacía aún.\n")


# ---- alcanzabilidad desde la raíz (subárboles invisibles)
@case("un concepto al que no se llega navegando desde la raíz", "subárbol invisible")
def _(d):
    # El índice de la carpeta lo lista bien, pero el índice RAÍZ deja de listar la carpeta:
    # los chequeos locales siguen contentos y el subárbol entero queda inalcanzable.
    # Se rompen TODAS las apariciones: desde la 0.9.0 la puerta del index también la linkea,
    # y romper solo la primera dejaba el subárbol alcanzable por la otra.
    p = d / "index.md"
    t = p.read_text(encoding="utf-8")
    p.write_text(t.replace("](decisions/index.md)", "](decisions/index.md-roto)"), encoding="utf-8")


@case("un concepto linkeado desde otro concepto, no desde un índice", None)
def _(d):
    # Redacción legítima: se llega igual, por un cross-link. El chequeo es de
    # ALCANZABILIDAD, no de "todo tiene que colgar de un índice".
    p = d / "decisions" / "0099-alcanzable-por-cross-link.md"
    p.write_text(
        # Lleva `verify:` porque el dogfood adoptó la convención: en un bundle adoptado, una
        # decisión `accepted` sin declararlo es WARN, y este caso mide OTRA cosa.
        "---\ntype: Decision\nstatus: accepted\nverify: none\n"
        "verify_note: fixture del test de alcanzabilidad\ntitle: Alcanzable por cross-link\n"
        "description: Concepto al que se llega desde otro concepto y no desde un índice.\n"
        "timestamp: 2026-08-03T00:00:00Z\n---\n\n# Contexto\n\ncuerpo\n",
        encoding="utf-8")
    # Se lista en su índice (chequeo local, ya existente) y además se cross-linkea: el
    # chequeo nuevo no tiene que agregar ruido sobre contenido perfectamente normal.
    edit(d, "decisions/index.md", "\n* [", 
         "\n* [Alcanzable por cross-link](0099-alcanzable-por-cross-link.md) - Concepto al que se llega desde otro concepto y no desde un índice.\n* [")
    edit(d, "decisions/0001-relative-links-over-absolute.md", "# Contexto",
         "# Contexto\n\nVer [alcanzable](0099-alcanzable-por-cross-link.md).")


# ---- ids estables de regla y --skip
@case("cada hallazgo trae su id de regla entre corchetes", "[link-absolute]")
def _(d):
    edit(d, "index.md", "](decisions/index.md)", "](/decisions/index.md)")


@case("--skip calla la regla por id", None, extra=["--skip", "dir-empty"])
def _(d):
    # Rotura de efecto AISLADO: una carpeta vacía dispara `dir-empty` y nada más. Un link
    # absoluto habría servido igual de mal: además de `link-absolute`, deja el subárbol
    # entero inalcanzable, así que el caso no probaría el skip sino la suma de reglas.
    (d / "carpeta-vacia").mkdir()


@case("--skip de otra regla NO tapa la que importa", "[link-absolute]",
      extra=["--skip", "dir-empty,log-date-iso"])
def _(d):
    edit(d, "index.md", "](decisions/index.md)", "](/decisions/index.md)")


# ---- --pack: empaquetar el bundle sin duplicar
@case("--pack no repite un archivo aunque lo linkeen dos veces", None, pack_unique=True)
def _(d):
    # El cross-link extra hace que el concepto sea alcanzable por dos caminos. Un pack que
    # inline por link lo copiaria dos veces — la deriva adentro del propio pack.
    edit(d, "index.md", "# Subdirectories",
         "Ver tambien [una decision](decisions/0001-relative-links-over-absolute.md).\n\n# Subdirectories")


# ---- origen: una razón reconstruida no puede ser normativa
@case("una decisión reconstruida del código declarada como normativa", "origen-reconstruido-normativo")
def _(d):
    # El estado exacto que produjo la peor falla que midió este kit: un agente redactó un
    # Contexto convincente para algo que NADIE decidió, y quedó `accepted` = normativo.
    edit(d, "decisions/0001-relative-links-over-absolute.md",
         "origen: dictado", "origen: reconstruido")


@case("una decisión reconstruida que NO se declara normativa", None)
def _(d):
    # Redacción legítima: reconstruir está bien mientras no se disfrace de mandato.
    edit(d, "decisions/0001-relative-links-over-absolute.md",
         "origen: dictado", "origen: reconstruido")
    edit(d, "decisions/0001-relative-links-over-absolute.md", "status: accepted", "status: proposed")


@case("una decisión dictada por una persona, normativa", None)
def _(d):
    edit(d, "decisions/0001-relative-links-over-absolute.md",
         "origen: dictado", 'origen: "dictado"')


@case("una decisión confirmada que no declara el hueco del porqué",
      "origen-confirmado-sin-pregunta")
def _(d):
    edit(d, "decisions/0001-relative-links-over-absolute.md",
         "origen: dictado", "origen: confirmado")


@case("una decisión confirmada que SÍ declara el hueco, normativa", None)
def _(d):
    # El caso legítimo: la decisión obliga (alguien confirma que se tomó) y el porqué queda
    # como deuda visible, que además entra sola en `--questions`.
    edit(d, "decisions/0001-relative-links-over-absolute.md",
         "origen: dictado", "origen: confirmado")
    edit(d, "decisions/0001-relative-links-over-absolute.md", "# Contexto",
         "# Contexto\n\n> Pendiente de confirmar: por que se decidio esto. La decision esta\n"
         "> confirmada; el razonamiento no quedo registrado.")


# ---- verify: la convención se exige sola cuando el bundle la adopta
@case("una decisión `accepted` sin `verify` en un bundle que ya lo usa",
      "decision-sin-verify")
def _(d):
    # El dogfood ya adoptó la convención, así que alcanza con sacársela a una.
    edit(d, "decisions/0001-relative-links-over-absolute.md", "\nverify:", "\nverify_x:")


@case("`verify: none` sin decir por qué", "verify-none-sin-nota")
def _(d):
    p = d / "decisions" / "0019-licencia-apache-2.md"
    txt = p.read_text(encoding="utf-8")
    import re as _re
    txt = _re.sub(r"^verify:.*$", "verify: none", txt, count=1, flags=_re.M)
    p.write_text(txt, encoding="utf-8")


@case("`verify: none` CON su motivo declarado", None)
def _(d):
    p = d / "decisions" / "0019-licencia-apache-2.md"
    txt = p.read_text(encoding="utf-8")
    import re as _re
    txt = _re.sub(r"^verify:.*$", "verify: none\nverify_note: es una decisión legal",
                  txt, count=1, flags=_re.M)
    p.write_text(txt, encoding="utf-8")


@case("--questions saca a la superficie una pregunta abierta", None, questions_expect=1)
def _(d):
    edit(d, "decisions/0001-relative-links-over-absolute.md", "# Contexto",
         "# Contexto\n\n> Pendiente de confirmar: por que se eligio esto. No hay razon registrada.")


@case("--budget separa la prosa del kit de la del usuario", None, budget_expect=True)
def _(d):
    pass


def main() -> int:
    if not LINT.is_file():
        print(f"okf_lint_test: no encontré {LINT}", file=sys.stderr)
        return 1
    root = Path(tempfile.mkdtemp(prefix="okf-lint-test-"))
    print(f"{'caso':<62} {'espera':<8} {'real':<8} veredicto")
    bad = 0
    try:
        for name, expect, fn, extra, pack_unique, q_exp, b_exp in CASES:
            # Se copia el KIT entero, no solo `knowledge/`: el dogfood linkea archivos de
            # afuera del bundle (`../../OKF-SPEC.md`) y en una copia aislada serían links
            # rotos — un falso positivo del harness que enmascararía los casos limpios.
            kit = root / re.sub(r"\W+", "_", name)[:40]
            shutil.copytree(KIT, kit, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            d = kit / "knowledge"
            try:
                fn(d)
            except AssertionError as e:
                print(f"{name:<62} {'—':<8} {'—':<8} SETUP ROTO: {e}")
                bad += 1
                continue
            if b_exp:
                rb = subprocess.run([sys.executable, str(LINT), str(d), "--budget"],
                                    capture_output=True, text=True)
                ok = "del kit" in rb.stdout and "tuyo" in rb.stdout and "TOTAL" in rb.stdout
                print(f"{name:<62}{'desglosa':<8} {'ok' if ok else 'no':<8} "
                      f"{'ok' if ok else '<<< MAL'}")
                bad += not ok
                continue
            if q_exp is not None:
                # Se mide el DELTA contra el dogfood, no el total. Exigir "1 pregunta" daba
                # por sentado que el bundle del kit tiene cero preguntas abiertas — y tener
                # preguntas abiertas es exactamente la práctica que el kit predica, así que
                # el propio kit rompía este test al usarla. Un test de la herramienta no
                # puede depender del contenido del dogfood.
                rq = subprocess.run([sys.executable, str(LINT), str(d), "--questions"],
                                    capture_output=True, text=True)
                base = subprocess.run([sys.executable, str(LINT), str(KIT / "knowledge"),
                                       "--questions"], capture_output=True, text=True)
                def _n(out: str) -> int:
                    # Con cero preguntas el linter no imprime ningún número, dice "no hay
                    # preguntas abiertas". Sin este caso, el dogfood limpio daba -1 y el
                    # delta nunca cerraba.
                    if "no hay preguntas abiertas" in out:
                        return 0
                    m = re.search(r"(\d+) pregunta", out)
                    return int(m.group(1)) if m else -1
                ok = _n(rq.stdout) == _n(base.stdout) + q_exp
                print(f"{name:<62} {'lista '+str(q_exp):<8} "
                      f"{'ok' if ok else 'no las vio':<8} {'ok' if ok else '<<< MAL'}")
                bad += not ok
                continue
            if pack_unique:
                rp = subprocess.run([sys.executable, str(LINT), str(d), "--pack"],
                                    capture_output=True, text=True)
                heads = [l for l in rp.stdout.splitlines() if l.startswith("## `")]
                ok = len(heads) == len(set(heads))
                print(f"{name:<62} {'limpio':<8} {'limpio' if ok else 'duplica':<8} "
                      f"{'ok' if ok else '<<< MAL'}")
                bad += not ok
                continue
            r = subprocess.run([sys.executable, str(LINT), str(d), "--strict", *extra],
                               capture_output=True, text=True)
            out = r.stdout + r.stderr
            if expect is None:
                ok = r.returncode == 0
                real = "limpio" if ok else "reporta"
            else:
                # No alcanza con que falle: tiene que fallar POR ESTO.
                ok = r.returncode != 0 and expect in out
                real = ("reporta" if r.returncode != 0 else "limpio") + ("" if ok else " (otro)")
            bad += not ok
            print(f"{name:<62} {'limpio' if expect is None else 'reporta':<8} {real:<8} "
                  f"{'ok' if ok else '<<< MAL'}")
            if not ok and expect:
                print(f"{'':<62} → esperaba {expect!r} en el reporte; salió:\n{out.strip()[:400]}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"\nokf_lint_test: {len(CASES) - bad}/{len(CASES)} casos se comportan como corresponde")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
