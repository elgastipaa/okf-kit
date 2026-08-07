---
type: Runbook
title: Cómo se comprueba que el kit anda
description: Los comandos que prueban que el kit funciona, y qué cubre cada uno.
tags: [checks, gate]
timestamp: 2026-08-07T00:00:00Z
---

# Los cuatro que corre el CI

Son los mismos que exige el gate de release. Si tocaste un assert o un criterio, se prueba acá.

| Comando | Qué cubre | Cuánto tarda |
|---|---|---|
| `python3 scripts/okf_selfcheck.py` | Consistencia interna del kit: linter limpio sobre el dogfood, `kit_version` sembrado, keep-alive y capa de futuro coincidentes, presupuesto del contrato, instalación mínima y completa sin huérfanos, referencias que resuelven. | ~20 s |
| `python3 scripts/okf_selfcheck_test.py` | **¿El gate falla cuando debe?** Inyecta cada rotura conocida sobre una copia del kit y verifica el veredicto. | ~2 min |
| `python3 scripts/okf_lint_test.py` | ¿El linter reporta cuando debe, y calla ante redacción legítima? | ~30 s |
| `python3 scripts/okf_stale_test.py` | ¿El ranker de drift ordena como corresponde? | ~5 s |

**Un assert sin su rotura probada es decoración.** Por eso las suites 2 a 4 no son opcionales:
miden que las herramientas *fallen*, no solo que pasen.

# Sobre el propio bundle

```bash
python3 templates/scripts/okf_lint.py knowledge --strict   # estructura
python3 templates/scripts/okf_refs.py  knowledge           # referencias vivas
python3 templates/scripts/okf_decisions.py knowledge/decisions  # ¿el kit cumple sus decisiones?
```

El tercero corre los `verify:` de las decisiones. Hoy: **26 con comando real, 8 sin chequeo
mecánico** (método de medición, límites del instrumento, lo que el kit promete — cosas que
ningún comando puede falsear).

El linter se consume **desde `templates/`**: copiarlo a la raíz crearía dos copias, que es la
deriva que el kit existe para evitar.

# Por qué el kit NO tiene capa generada

`okf_lint --modernize` la va a seguir ofreciendo, y la respuesta es **no**, evaluada: los
únicos números que cita este bundle son **registros históricos** (`v0.7.6 — 96 asserts`), que
están congelados a propósito y no driftean. No hay hechos volátiles que se pregunten seguido.
Es el caso que la [0031](decisions/0031-generar-compra-correctitud-no-velocidad.md) llama
*"no generes por generar"*: un generador es código a mantener.

# Lo que ninguno de estos cubre

Que el kit **sirva**. Eso no lo dice un chequeo determinista: lo dice la medición
(`templates/eval/run-eval.py`, resultados en `MEASUREMENT.md`), y su método está en la
[0028](decisions/0028-la-medicion-manda-y-el-gate-se-escribe-antes.md).
