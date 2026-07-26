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

- [ ] Definir las preguntas golden de rumbo ("¿qué sigue?", "¿en qué estábamos?", idea
      fuera de alcance) y agregarlas al golden-set de un conejillo
- [ ] Medir baseline (sin capa) en ese repo
- [ ] Instalar la capa (roadmap + un `_changes/` real) y re-medir
- [ ] Probar el ciclo completo de harvest con un agente en frío (¿lo corre sin que se lo pidan?)
- [ ] Registrar el resultado —positivo o negativo— como decisión

# Decisiones y descubrimientos en el camino

- (vacío — se llena mientras se trabaja)

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" de arriba (medido de verdad, no asumido)
- [ ] Decisiones/descubrimientos de arriba → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados (arquitectura / schema / runbooks…)
- [ ] Si el harvest creó una **carpeta** nueva, sumada al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado
- [ ] Borrar este archivo (git conserva la historia). **Ningún doc permanente puede quedar
      linkeando a `_changes/`** — cortá ese link primero (solo el roadmap linkea acá).
