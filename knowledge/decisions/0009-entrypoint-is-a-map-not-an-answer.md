---
type: Decision
status: accepted
verify: grep -q "MAPA, no la respuesta" templates/AGENTS.md
title: El entrypoint es un mapa, no una respuesta — guardrail contra falsos positivos
description: El template AGENTS.md instruye explícitamente no responder preguntas de dominio citando el propio contrato, porque una capa de contexto puede fabricar respuestas rápidas y equivocadas.
tags: [okf, entrypoint, correctness, false-positive, eval]
timestamp: 2026-06-18T00:00:00Z
---

# Contexto

> **Vigente.** La [0022](0022-el-bundle-tambien-es-un-mapa.md) intentó extender su alcance al
> bundle; se midió, no pasó el gate y **se revirtió** ([0023](0023-verificar-siempre-no-paga.md)).
> Esta decisión sigue en pie tal como está.
En una validación **blind** (un agente aplicó el kit a un repo sin conocer las preguntas, y
después se midió con `templates/eval/`), aparecieron −31% de turnos reales — pero **una
pregunta se volvió rápida y MAL**: "¿cuál es la regla anti-waste?" (una mecánica de combate)
cayó de 5 a 1 turno porque el agente matcheó "anti-waste" con la sección *"Capas NO
autoritativas — no reconcilies basura"* del `AGENTS.md` y respondió **citando el contrato, sin
mirar el código** (`FINISHER_ANTI_WASTE_RULES`). Midiendo solo turnos/tokens, eso contaba como
mejora; era una regresión de correctitud. Lo cazó la calificación de acierto.

Causa general (no del repo): el agente trató al **contrato como fuente de respuestas**. Un
hueco de cobertura en el glosario + una sección de autoridad cuyo *nombre* parece contestar =
atajo a una respuesta falsa.

# Decisión
El template `templates/AGENTS.md` declara explícitamente que **el entrypoint es un mapa, no la
respuesta**: para preguntas de dominio ("¿cómo funciona X?", "¿cuál es la regla de Y?") el
agente sigue el mapa hasta el concepto o el código y **no responde citando las reglas/secciones
del propio contrato**; si el nombre de una sección parece contestar, es coincidencia y hay que
verificar en la fuente. Complementariamente, la `GUIDE.md` pide que el glosario **cubra los
términos-mecánica calientes** (un hueco es peligroso), y `templates/eval/grade.md` eleva el
**falso positivo (rápido y mal)** a regla dura del loop: una mejora de turnos que mete un
`incorrecta` nuevo se rechaza.

# Consecuencias
- Ataca el mecanismo del falso positivo de forma **general** (sirve para cualquier repo), sin
  soplarle la respuesta al repo destino (eso sería point-fix tramposo).
- Refuerza la regla de oro existente "[gana el código](0008-declare-non-authoritative-layers.md)":
  el contrato apunta, la fuente manda — y el agente *debe ir a la fuente*.
- Hace explícito en el kit lo que el eval ya predicaba: **medir acierto, no solo tokens**; una
  capa de contexto puede fabricar confianza equivocada si se la trata como contenido.
