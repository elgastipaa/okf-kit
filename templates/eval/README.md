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

Sin la 4ª columna optimizás hacia respuestas vagas. Las cuatro juntas, siempre.

## Cómo se corre

```bash
# 1) un scorecard CON el bundle (comportamiento natural; AGENTS.md se auto-carga)
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode kit  --out scorecard.kit.jsonl

# 2) el baseline SIN el bundle (el piso a batir)
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode nokit --out scorecard.nokit.jsonl

# 3) con calificación de acierto (cuesta llamadas extra de juez)
templates/eval/run-eval.py <repo-dir> <golden-set.md> --mode kit --out scorecard.kit.jsonl --grade
```

Stdlib pura (como `okf_lint.py`): solo necesita `claude` en PATH, no `jq`.

El runner imprime una tabla y deja un `.jsonl` (una línea por pregunta) + un resumen.

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
5. Re-aplicar a los repos → re-correr eval **con `--grade`** → conservar **solo si baja
   turnos SIN introducir ningún `incorrecta` nuevo** (una respuesta rápida y equivocada es
   peor que una lenta y correcta; ver [`grade.md`](grade.md)) ni regresar otros repos.
6. ADR en `knowledge/decisions/` → volver a 1.

**Stop:** por categoría, cuando le gana claro al baseline sin-kit y dos vueltas seguidas
mejoran <10%.

## Notas

- `--mode nokit` es un baseline **barato** (le pide al agente no leer el bundle); el
  baseline **fiel** es un clon del repo sin la capa de contexto. Documentá cuál usaste.
- Un subagente/headless es **el mismo modelo**; para probar portabilidad cross-vendor,
  corré el golden-set a mano en otra IA (igual que el cold-test).
