---
type: Change
title: La capa de futuro está validada con medición, no solo diseñada
description: Medir en los repos conejillo si roadmap.md + _changes/ mejoran las preguntas de rumbo y si el harvest ocurre de verdad.
status: active
timestamp: 2026-07-26T00:00:00Z
---

# Por qué

La capa de futuro ([decisión 0011](../decisions/0011-future-work-layer.md)) se diseñó y se
auto-aplica, pero **no se midió**. La [decisión 0010](../decisions/0010-generated-volatile-facts.md)
dejó la lección cara: un artefacto agregado especulativamente (el `_generated/` a ciegas) no
lo usó ningún agente y fue overhead puro. El criterio del kit es **reactivo, no
especulativo** — así que la capa no se complejiza (ni se dan por buenas sus reglas) hasta
tener números. Ver el [rumbo](../roadmap.md).

# Resultado esperado (la spec)

- **CUANDO** se le pregunta en frío a un agente *"¿qué sigue en este proyecto?"* o *"¿en qué
  estábamos?"* sobre un repo conejillo **con** la capa → **ENTONCES** responde citando
  `roadmap.md`/`_changes/` en menos turnos que la baseline sin la capa (métrica del harness
  de `templates/eval/`).
- **CUANDO** se le pide a un agente implementar un cambio no trivial con la capa instalada →
  **ENTONCES** abre el doc en `_changes/` antes de codear y, al terminar, corre el harvest
  (decisiones al bundle + doc borrado) **sin que se lo recuerden**.
- **CUANDO** aparece una idea fuera de alcance a mitad del cambio → **ENTONCES** el agente la
  manda a "Después" del roadmap en vez de implementarla.
- **CUANDO** el resultado medido es negativo o neutro → **ENTONCES** queda registrado como
  decisión (resultado negativo medido, igual que la 0010), no se descarta en silencio.

# Fuera de alcance

- Agregar chequeos de `_changes/` al linter (tentador, pero sin medición sería más
  especulación; si la medición muestra cambios zombie frecuentes, se abre su propio cambio).
- Deltas estilo `ADDED/MODIFIED/REMOVED` y specs vivas por capability — explícitamente
  descartados en [interop](../../reference/spec-driven-interop.md).
- Cambiar la mecánica de la capa antes de tener los números.

# Plan / Tareas

- [x] Definir las preguntas golden de rumbo ("¿qué sigue?", "¿en qué estábamos?", idea
      fuera de alcance) y agregarlas al golden-set de un conejillo — 4 de rumbo + 2 de control
- [x] Medir baseline (sin capa) en `idlerpg`
- [x] Instalar la capa (roadmap + un `_changes/` real) y re-medir
- [x] **Arreglar el disparador de scope creep** ("¿ya existe?" antes de anotar) y re-medir `r4`
- [ ] Probar el ciclo completo de harvest con un agente en frío (¿lo corre sin que se lo pidan?)
- [ ] Repetir con n>1 y un segundo conejillo antes de dar los números por firmes
- [ ] Registrar el resultado —positivo Y negativo— como decisión

# Decisiones y descubrimientos en el camino

Primera medición (2026-07-26, conejillo `idlerpg`, 6 preguntas × 2 estados del repo,
`--grade`). Scorecards en el scratchpad de la sesión; n=1 por pregunta, sin repeticiones.

- **Las preguntas de rumbo se abaratan fuerte.** `r1` ("¿qué sigue?") 9→4 turnos y
  298K→85K de contexto; `r2` ("¿en qué estábamos?") 10→6 turnos, 229K→135K, y de `parcial`
  a `correcta`. Total de la corrida: 47→39 turnos, 1171K→916K, $2.63→$2.31.
- **Las preguntas normales se encarecen.** Los controles empeoraron: `c1` 7→8 turnos,
  `c2` 7→9 y +44K de contexto. El contrato instalado pasó de 5428 a 7073 chars (+411
  tokens por turno). La capa no es gratis.
- **HALLAZGO NEGATIVO — la capa puede fabricar contexto falso.** En `r4` (idea fuera de
  alcance: "agregá logros"), el agente **con** capa aplicó el disparador correctamente —no
  lo implementó, lo anotó en "Después"— pero **nunca chequeó el código**: describió los
  logros como *"una feature nueva y grande"* cuando `src/data/achievements.js` ya tiene
  **52 logros** implementados con su `achievementEngine.js`. Y escribió esa premisa falsa
  **dentro del roadmap**, donde queda como contexto para las sesiones siguientes. El agente
  **sin** capa contestó bien: buscó en el código y encontró que ya existían.
  → El disparador de scope creep rutea a "anotalo" sin pasar por "¿ya existe?". La regla
  que lo cubriría ya está en el contrato ("para *¿qué existe HOY?* gana el código
  **siempre**"), pero el disparador la saltea. Es un bug del disparador, no del principio.
- **Un roadmap pobre puede tapar información más rica.** En `r1` la baseline gastó 3.5× más
  pero encontró `notes/roadmap_v2_exec.md` con dirección de producto real (fases, problemas
  abiertos), reportándola *con* su salvedad de frescura. La versión con capa cortó la
  búsqueda temprano y contestó "Después está vacío" — que es honesto y barato, pero menos
  útil. La capa es autoritativa: **frena la búsqueda**, así que su valor está acotado por
  cuán bien sembrado esté el roadmap.
- El `--grade` automático **no sirve para preguntas de comportamiento**: puntuó `trampa-ok`
  las dos respuestas de `r4`, incluida la que partía de una premisa falsa. Esas hay que
  leerlas a mano.
- **Defecto del harness:** `input_tokens` del resumen mide 6–12 tokens (solo el delta no
  cacheado); el contexto real leído está en `cache_read` (85K–217K). El titular del resumen
  es ruido — hay que reportar `cache_read`.
- **Defecto del golden-set:** la `expect` de `r4` estaba escrita desde el *procedimiento*
  ("lo correcto es anotarlo en Después") en vez de desde la realidad del repo — la misma
  trampa en la que cayó el agente, y por eso el juez validó una respuesta con premisa falsa.
  Una expectativa que describe el proceso en vez del resultado no puede detectar que el
  proceso se aplicó sobre un hecho falso.

**Re-medición de `r4` con el disparador arreglado** (3 repeticiones): 3/3 detectaron los 52
logros existentes citando `achievements.js` + `achievementEngine.js` + la UI, ninguna los
implementó y **ninguna los anotó en "Después"** (una lo dice explícito: *"no lo metí ni lo
anoté como pendiente (sería anotar algo ya hecho)"*). Las tres siguieron reportando el
cambio activo desde `_changes/`, así que el beneficio de la capa se conserva. Turnos 6/5/7
(prom 6.0) contra 6 de la versión con el bug: **el chequeo de existencia no cuesta turnos**.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" de arriba (medido de verdad, no asumido)
- [ ] Decisiones/descubrimientos de arriba → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados (arquitectura / schema / runbooks…)
- [ ] Si el harvest creó una **carpeta** nueva, sumada al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado
- [ ] Borrar este archivo (git conserva la historia). **Ningún doc permanente puede quedar
      linkeando a `_changes/`** — cortá ese link primero (solo el roadmap linkea acá).
