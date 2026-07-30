---
type: Decision
status: accepted
title: Declarar capas no-autoritativas en el entrypoint para no reconciliar basura
description: El AGENTS.md template lista los dirs scratch/legacy que NO son estado, porque las preguntas adversariales (código vs notas viejas) explotan en turnos.
tags: [okf, authority, staleness, efficiency, eval]
timestamp: 2026-07-29T00:00:00Z
---

# Contexto
Midiendo con `templates/eval/` sobre un repo real con docs dispersos y `notes/` legacy,
las preguntas **adversariales** — donde el código dice una cosa y notas/docs viejas dicen
otra — resultaron las más caras. Caso testigo (baseline, sin capa): "¿cuántos `.md` quedaron
viejos/legacy?" costó **27 turnos** porque el agente cruzó ~106 archivos contra el código sin
nada que le dijera cuál fuente manda. Es un failure mode de **autoridad/staleness**, distinto
del routing que cura el [glosario](0007-domain-glossary-and-code-of-record.md).

Repos maduros ya lo resuelven: el wiki de un repo real tiene una tabla *"Capas que NO son
fuente de estado (no leas el estado actual de acá)"* que marca planes/logs/mockups como
no-autoritativos. El kit no lo prescribía.

# Decisión
El template `templates/AGENTS.md` gana una sección **"Capas NO autoritativas"**: el repo
lista ahí los dirs/archivos scratch, legacy, planes viejos o exploración que **no reflejan el
estado actual**, con la regla de que para preguntas "¿qué existe / cuántos / a qué nivel HOY?"
**gana el código** y esas capas se ignoran (no se reconcilian). La `GUIDE.md` lo recomienda
para repos ruidosos/legacy. Enforcement **liviano** (coherente con
[consumo permisivo](0002-permissive-consumption.md)): se propone, no se exige.

# Consecuencias
- Indicio fuerte: declarar `notes/` no-autoritativo bajó esa pregunta de auditoría de **27 a
  2 turnos**. (El scorecard *completo* de ese spike quedó **contaminado** — el experimentador
  escribió la capa conociendo las preguntas; ver `eval/COMPARISON.md` — por eso una validación
  **blind** está en curso: un agente aplica el kit sin conocer las preguntas, recién después
  corren. El número 27→2 es indicativo, no definitivo.)
- Complementa el glosario: glosario = *dónde está la verdad* (routing); capas no-autoritativas
  = *qué ignorar* (autoridad). Juntos atacan los dos costos de un repo ruidoso.
- **Cautela aprendida (vale para ambos mecanismos):** no hornear *valores* en la capa — un
  agente los repite sin verificar el código y propaga drift. La capa apunta; el código manda.
