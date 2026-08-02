---
type: Decision
status: accepted
supersedes: 0009-entrypoint-is-a-map-not-an-answer
title: El bundle también es un mapa — la obligación de verificar es previa, no reactiva
description: El guardrail contra respuestas rápidas y equivocadas se extiende del contrato a las páginas del bundle, y pasa de resolver conflictos a exigir la fuente antes de contestar.
tags: [okf, entrypoint, correctness, false-positive, eval]
timestamp: 2026-08-02T00:00:00Z
---

# Contexto

La [0009](0009-entrypoint-is-a-map-not-an-answer.md) puso el guardrail *"es un MAPA, no la
respuesta"* después de que un agente contestara mal citando una sección del **contrato**. La
decisión no estaba equivocada: estaba **incompleta**, y la primera medición defendible del kit
lo mostró.

Tres brazos sobre idlerpg (7 preguntas adversariales, n=3, capa aplicada por un agente ciego):
el brazo con el kit metió **4 fallos de acierto contra 0** de "sin capa" y de "solo un
`AGENTS.md` convencional", uno de ellos aceptando una premisa falsa. Verificados a mano.

**El diagnóstico descartó que fuera contenido.** El bundle no contenía ninguno de los datos
equivocados: no nombraba la especialización inventada, su línea de glosario sobre el design
system era correcta, y el documento de triage que el agente citó estaba bien escrito. Los tres
fallos ocurrieron **con contenido correcto en el bundle**.

El mecanismo es único: **la capa ofrece una respuesta parcial más barata que la fuente, y el
agente se detiene ahí.** El glosario contesta *"qué es X"* y el agente da por contestado *"cuál
es el X vigente"*; una página de triage contesta *"qué documentos son basura"* y el agente la
cita en vez de contar.

Dos agujeros de redacción lo permitían:

1. La 0009 quedó **scopeada al contrato** ("no contestes citando las reglas o secciones de
   *este* contrato"). Los tres fallos vinieron de **páginas del bundle**.
2. La regla descriptivo-vs-código estaba redactada como **resolución de conflicto** —si
   difieren, gana el código—, así que un agente que lee una página y **no percibe ninguna
   contradicción** nunca la activa. Justamente el caso: nadie ve un conflicto cuando la página
   es correcta pero contesta *otra* pregunta.

Es la predicción textual de la [0014](0014-future-layer-measured.md): *"cualquier capa que
parezca autoritativa y sea más barata de leer que la fuente invita a saltearse la fuente"*.

# Decisión

El contrato instalado extiende el guardrail al bundle y lo vuelve **previo, no reactivo**:
para preguntas de **estado actual** —"¿qué existe / cuántos hay / cuál es el vigente HOY?"— el
concepto es el **puntero** y la respuesta sale del **código**, y hay que abrir la fuente
**aunque el concepto parezca contestar y no se vea ninguna contradicción**. Se suma la
obligación de **declarar la ambigüedad** cuando la pregunta admite más de una lectura, en vez
de elegir una y presentarla como única.

Entra en el presupuesto del contrato con un recorte compensatorio en `## Procedimientos` (la
explicación de *por qué* son vendor-neutral era prosa para humano; el dato accionable es dónde
están).

Todo lo que la 0009 decidió sigue vigente y queda **subsumido acá**: no responder desde el
contrato, cubrir los términos-mecánica calientes en el glosario, y la regla dura del loop de
que una mejora de turnos con un `incorrecta` nuevo se rechaza.

# Consecuencias

- **Es una hipótesis con gate, no una mejora asumida.** Vale si la re-medición devuelve el
  acierto del brazo kit a **0/18 sin empeorar los turnos por encima del ruido**; si no, se
  revierte. El kit no puede darse por bueno un cambio de correctitud sin medirlo — es
  exactamente el error que esta decisión corrige.
- **Congela el "mecanismo 5"** (autoridad negativa: *"si el término no está en el
  code-of-record, no existe"*). Proponía licenciar que el agente **deje de buscar**, o sea más
  permiso para lo que acaba de fallar. Se revisa cuando el acierto vuelva a 0/18.
- **Cuanto mejor es una página del bundle, más barato es creerle sin verificar.** El fallo más
  incómodo lo produjo un documento bien escrito. La calidad del contenido no protege contra
  este modo de falla: por eso el guardrail es estructural y no una guía de estilo.
- Refuerza "[gana el código](0008-declare-non-authoritative-layers.md)" convirtiéndolo en una
  obligación previa: antes decía a quién creerle en un empate, ahora dice cuándo ir a mirar.
