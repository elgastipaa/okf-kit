---
type: Change
title: La capa deja de invitar a contestar sin verificar
description: "El guardrail 'mapa, no respuesta' pasa a cubrir las páginas del bundle, que es de donde salieron los tres fallos de acierto medidos."
status: active
timestamp: 2026-08-02T00:00:00Z
---

# Por qué

La primera medición defendible del kit ([0005](0005-el-instrumento-antes-que-el-kit.md)) dio
**4 fallos de acierto contra 0** de los otros dos brazos. El diagnóstico posterior descartó
que fuera contenido: el bundle de idlerpg **no** contenía ninguno de los datos equivocados
—no dice "Guardian" en ningún lado, la línea del glosario sobre Forge Light es correcta, y
el triage de docs viejos está bien escrito—. Los tres fallos ocurrieron **con contenido
correcto**.

El patrón es único: **la capa ofrece una respuesta parcial más barata que la fuente, y el
agente se detiene ahí.** El glosario contesta "qué es Forge Light" y el agente da por
contestado "cuál es el último"; el triage contesta "qué docs son basura" y el agente lo cita
en vez de contar; en la q3 se sintió cubierto y no verificó el nombre de la especialización.

Y hay un agujero concreto de scope. La [0009](../decisions/0009-entrypoint-is-a-map-not-an-answer.md)
puso el guardrail *"es un MAPA, no la respuesta"* **en el contrato y solo sobre el contrato**
("no contestes citando las reglas o secciones de *este* contrato"). Los tres fallos vinieron
de **páginas del bundle**. La regla descriptivo-vs-código existe pero está redactada como
**resolución de conflicto** —si difieren, gana el código—, así que un agente que lee una
página y no percibe ninguna contradicción nunca la activa.

# Resultado esperado (la spec)

- **CUANDO** a un agente con el bundle instalado le preguntan por el estado actual del repo
  ("¿qué existe?", "¿cuántos hay?", "¿cuál es el vigente hoy?") → **ENTONCES** abre la fuente
  que el concepto señala y contesta desde ahí, **aunque el concepto ya parezca contestar y no
  haya contradicción visible**.
- **CUANDO** la pregunta admite más de una lectura → **ENTONCES** lo dice, en vez de elegir
  una y presentarla como la única (es el fallo de la q6).
- **CUANDO** se re-mide idlerpg con los tres brazos → **ENTONCES** el acierto del brazo kit
  vuelve a **0/18 no-aciertos y 0 premisas falsas**, sin que los turnos empeoren por encima
  del ruido. **Si no lo logra, este cambio se revierte** — no se relaja el gate.
- **CUANDO** se corre el gate del kit → **ENTONCES** el contrato instalado sigue entrando en
  el presupuesto de 7000 chars.

# Fuera de alcance

- El **mecanismo 5** (autoridad negativa) queda **congelado**, no sepultado: proponía
  licenciar que el agente deje de buscar, que es más permiso para lo que acaba de fallar.
  Se revisa recién cuando el acierto vuelva a 0/18.
- Medir `the-conclave` (la pregunta de valor: ¿paga donde el routing es difícil?). Va después,
  y arrastra su propio problema: su capa es un wiki propio, no un bundle OKF, así que medir
  el kit ahí exige aplicárselo a ciegas primero.
- La dieta del contrato y `runbooks/checks.md`: siguen en el roadmap.

# Plan / Tareas

- [x] [0022](../decisions/0022-el-bundle-tambien-es-un-mapa.md) supersede a la 0009; la 0009
      pasa a `status: "superseded by 0022"` con un aviso arriba, sin editar lo que decidió.
- [x] `templates/AGENTS.md` §1: la regla proactiva (~300 chars).
- [x] Tres recortes compensatorios, ninguno en §1: la explicación de por qué los
      procedimientos son vendor-neutral, y dos frases de §2/§3 que decían lo mismo más largo.
- [x] Índice de `decisions/` y roadmap al día (el mecanismo 5 queda marcado CONGELADO).
- [x] Gate + las tres suites en verde (111/111, 56/56, 20/20, 9/9).

## El presupuesto es ahora la restricción que bloquea todo lo demás

Lo encontró una suite de roturas, no yo: el caso *"uso corriente de la palabra 'rumbo' en el
contrato"* —que agrega **una frase de 53 chars** y debe pasar— **empezó a fallar**, y no por
el assert que prueba sino por el **presupuesto**. El contrato estaba al **99,3% del techo**.

Se recuperó margen recortando prosa redundante (headroom 48 → **62**), pero eso es un parche:
cualquier convención nueva que toque el contrato ya no entra. **La dieta de §2 pasa de "buena
idea del roadmap" a prerrequisito**, y arrastra superseder o acotar la
[0013](../decisions/0013-installed-material-is-self-sufficient.md), que es la que obliga a
esos 403 tokens por turno. El presupuesto además mide mal —un archivo de tres, sin el
`CLAUDE.md` ni las descripciones de los skills (lente B)—, así que el techo real está más
cerca de lo que el gate cree.
- [ ] Re-medir idlerpg (3 brazos, n=3) y comparar contra la línea de base de la 0005.

# Decisiones y descubrimientos en el camino

- La 0009 no estaba equivocada, estaba **incompleta**: por eso se supersede en vez de
  editarse. Editarla sería exactamente lo que el kit le prohíbe a sus usuarios.
- El fallo de la q7 es el más incómodo: el agente citó `documentacion-vieja-triage.md`, que es
  **un buen documento**. O sea que la falla no la causa la basura del bundle sino su calidad —
  cuanto mejor es la página, más barato es creerle sin verificar.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" **con la medición**, no asumido
- [ ] Decisiones/descubrimientos → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"
- [ ] Borrar este archivo (git conserva la historia)
