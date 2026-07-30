# OKF eval — medir si el bundle realmente ahorra contexto

Este directorio es el **termómetro** del kit en un repo destino: prueba que la knowledge
base hace que un agente responda **más barato y mejor** que grepeando todo el repo. Es la
forma ejecutable del [cold-test](../../knowledge/runbooks/cold-test.md), pero **medida**:
no "¿entendió?" sino "¿cuántos tokens/turnos/segundos costó entender, y acertó?".

## Por qué existe

La promesa de OKF es: *el agente no recorre todo el código*. Eso solo se puede **afirmar**
si se **mide**. Este harness convierte esa promesa en un número por categoría de pregunta,
contra un baseline sin-kit, en contexto fresco.

## Las 4 columnas que importan

Por cada pregunta se registra:

| columna | de dónde sale | qué mide |
|---|---|---|
| `ctx_tok` = `cache_read` | `usage` del JSON headless | **la métrica de contexto**: cuánto tuvo que tragar de verdad (sube con cada grep/read). Órdenes de 85K–300K. El `input_tokens` de la API son los tokens **no cacheados** del último turno (6–12): es ruido, y compararlo entre corridas no mide nada. Se guarda en el scorecard como `input_tokens_prom_no_cacheados` solo para poder auditar la diferencia. |
| `num_turns` | `num_turns` | cuántas vueltas de tool-use (fan-out de búsqueda) |
| `duration_ms` | `duration_ms` | latencia real |
| **acierto** | juez (`--grade`) vs `expect` | **una respuesta rápida y equivocada es peor que una lenta y correcta** |
| **premisa** | juez (`--grade`) | ¿la respuesta le **siguió la corriente a una premisa falsa** de la pregunta? Es invisible para la columna de acierto —una respuesta con premisa falsa puede contener igual todos los hechos del `expect`— y es exactamente la forma del falso positivo que ya cazó este kit una vez. |

Sin la 4ª columna optimizás hacia respuestas vagas; sin la 5ª, hacia respuestas serviles.

## Cómo se corre

```bash
# 1) un scorecard CON el bundle (comportamiento natural; AGENTS.md se auto-carga)
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode kit --repeat 3 --out scorecard.kit.jsonl

# 2) el baseline SIN el bundle: aparta la capa del repo de verdad (ver más abajo)
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode nokit --repeat 3 --out scorecard.nokit.jsonl

# 3) el brazo que contesta la objeción "poné un AGENTS.md y listo": solo ese contrato,
#    sin bundle. El AGENTS.md convencional lo escribís vos — es la condición de control.
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode agentsmd \
    --agentsmd-file plain-AGENTS.md --repeat 3 --out scorecard.agentsmd.jsonl

# 4) con calificación de acierto y premisa (cuesta una llamada de juez por corrida)
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode kit --repeat 3 --grade
```

Stdlib pura (como `okf_lint.py`): solo necesita `claude` en PATH, no `jq`. Para el veredicto
cross-vendor, `OKF_EVAL_CLI=<otro-comando>`.

El runner imprime una tabla y deja un `.jsonl` (**una línea por corrida**, con su `rep`) +
un resumen. Con `--repeat N > 1` agrega por pregunta: mediana, min, max y spread.

## `--repeat`: por qué n=1 no alcanza

**El ruido intra-condición medido en este kit fue de ~3,3 turnos por pregunta** (dos corridas
de la misma condición sobre el mismo repo difirieron 13 turnos en una pregunta; otra midió 11
y 2). Con n=1, cualquier efecto menor a eso es indistinguible de haber corrido dos veces.

Corolario incómodo y verificado: el `−31%` que este kit publicó de su propio harness estaba
concentrado en **una sola pregunta**; sacándola, el efecto quedaba por debajo del ruido y con
signo mixto. **n≥3 para cualquier comparación**, y si el spread se come el efecto, el
resultado es "no se puede distinguir", no "no funcionó" ni "funcionó".

## El golden-set (no optimices contra UNA pregunta)

Ver [`golden-set.example.md`](golden-set.example.md). Reglas:

- **8–12 preguntas**, categorías mezcladas: `domain` (qué/por qué), `where` (dónde está
  implementado), `impact` (qué toco si cambio X), `ops` (cómo corro X), y **≥1 `trap`**
  (algo que el repo NO documenta — mide si admite "no está" o **alucina**).
- Cada pregunta lleva su **`expect`**: los hechos que una respuesta correcta debe contener
  + el archivo canónico que debería citar. Es la clave contra la que el juez califica.
- Mantené un puñado de preguntas **held-out** (en otro archivo) que NO mirás mientras
  iterás, para validar al final que no hubo overfitting.

## El loop de optimización (este harness es el paso 0)

1. Correr eval en ≥2 repos → scorecards.
2. Leer las **trazas** de las peores (no el score) → *failure mode*: routing / concepto
   esparcido / no-en-doc / chunk grande.
3. **Fork:** ¿el fix es general (→ cambio en el **kit**: contrato, formato, linter,
   template) o de contenido (→ autoría en el repo)? Solo el primero "optimiza el kit".
4. Aplicar al kit → re-estampar dogfood → `python3 scripts/okf_selfcheck.py`.
5. Re-aplicar a los repos → re-correr eval **con `--grade` y `--repeat 3`** → conservar
   **solo si baja turnos por encima del spread observado, SIN introducir ningún `incorrecta`
   ni ninguna `premisa-falsa-aceptada` nueva** (una respuesta rápida y equivocada es peor que
   una lenta y correcta; ver [`grade.md`](grade.md)) ni regresar otros repos.
6. ADR en `knowledge/decisions/` → volver a 1.

**Stop:** por categoría, cuando le gana claro al baseline sin-kit y dos vueltas seguidas
mejoran <10%.

**No publiques un número sin su dispersión.** Un `−31%` sin intervalo no es un resultado: es
una corrida. Si el efecto no supera el spread, lo que se reporta es "indistinguible con n=N".

## Notas

- **`--mode nokit` aparta los archivos, no le pide al agente que los ignore.** Pedírselo no
  medía "sin kit": Claude Code auto-carga el contrato en el prefijo antes de que el agente
  decida nada, así que el brazo quedaba contaminado a favor del kit. Ahora el harness mueve
  la capa (`knowledge/`, `AGENTS.md`, `CLAUDE.md`, `docs/wiki/`, `.agents/` — configurable con
  `--layer`) a un temporal y la restaura al terminar, incluso si la corrida se corta.
  **Solo corre si el repo es git y esas rutas están limpias**: el harness no mueve trabajo que
  git no pueda devolver. Si algo sale mal igual, imprime la ruta del respaldo y el
  `git checkout` exacto.
- Un subagente/headless es **el mismo modelo**; para probar portabilidad cross-vendor,
  corré el golden-set a mano en otra IA (igual que el cold-test).
