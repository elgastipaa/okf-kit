---
type: Decision
status: accepted
origen: dictado
verify: none
verify_note: es el resultado de una medición revertida; su evidencia está en MEASUREMENT.md
supersedes: 0022-el-bundle-tambien-es-un-mapa
title: Obligar a verificar siempre no paga — se revierte la 0022 y vuelve el alcance de la 0009
description: Mandar abrir la fuente en toda pregunta de estado actual costó 28% más turnos sin alcanzar el acierto que su propio gate exigía; se revierte y sobrevive solo la cláusula de ambigüedad.
tags: [okf, entrypoint, correctness, eval, resultado-negativo]
timestamp: 2026-08-02T00:00:00Z
---

# Contexto

La [0022](0022-el-bundle-tambien-es-un-mapa.md) se aceptó **como hipótesis con gate escrito
antes de medir**: valía si devolvía el acierto del brazo kit a 0/18 sin empeorar los turnos
por encima del ruido, y si no, se revertía. Se midió sobre idlerpg con el bundle idéntico y
las mismas preguntas —única variable cambiada: el texto del contrato— con n=3.

| | acierto | premisas falsas | turnos (sin q2) |
|---|---|---|---|
| kit 0.7.4 | 4/18 | 1 | 137 |
| **kit + 0022** | **2–3/18** | **0** | **176** |
| sin capa | 0/18 | 0 | 123 |

**No pasa el gate.** El acierto mejoró pero no llegó a 0/18, y los turnos subieron **28%**
—muy por encima del ruido de 3,14— quedando 43% peor que no tener capa.

El diagnóstico que motivó la 0022 era **parcialmente incorrecto**, y la medición lo mostró:
no todos los fallos eran "la capa ofrece una respuesta parcial más barata que la fuente". El
fallo de la especialización inventada es un **hueco de cobertura más confabulación del
modelo** —el bundle nunca nombró las especializaciones— y ninguna regla sobre verificar podía
arreglarlo. De hecho no lo arregló: **el agente inventó los nombres mientras citaba el archivo
correcto**. Verificar en la fuente no impide alucinar *sobre* la fuente.

# Decisión

Se **revierte** la regla del contrato que introdujo la 0022, y el alcance de la
[0009](0009-entrypoint-is-a-map-not-an-answer.md) vuelve a estar vigente tal como estaba.

Queda registrado lo que sí sobrevive a la medición, para no volver a proponerlo a ciegas:

- **La mitad de ambigüedad funcionó**: las premisas falsas aceptadas bajaron de 1 a 0, y una
  corrida enumeró explícitamente las dos lecturas de una pregunta trampa antes de contestar
  (el juez se la marcó `parcial` por error; verificado a mano). Es la única parte con
  evidencia a favor, y es **barata**: no manda a abrir ninguna fuente.
- **La mitad de verificación obligatoria es la que costó los turnos** sin comprar acierto.

Cualquier reintento debe separar las dos mitades y medir solo la de ambigüedad, con su propio
gate escrito antes.

# Consecuencias

- **El kit no tiene todavía un fix para la regresión de acierto.** Sigue vigente lo medido: la
  capa cuesta correctitud en este repo y nadie sabe por qué del todo. No se declara resuelto
  lo que no se resolvió.
- **Más instrucción no es la palanca.** El intento fue agregar prosa al contrato, y el
  resultado fue más turnos con casi el mismo acierto. Refuerza por la vía dura lo que ya decía
  [arXiv:2602.11988](https://arxiv.org/abs/2602.11988): el volumen de contexto no compra
  correctitud.
- **El presupuesto del contrato se recupera** (headroom 405): los recortes compensatorios de
  la 0022 se conservan porque eran redundancias de prosa, no contenido accionable.
- El **mecanismo 5** sigue congelado: la razón que lo congeló —licenciar dejar de buscar— no
  cambió, y ahora hay menos motivo para creer que agregar reglas al contrato mueva el acierto.
- **Este es el primer cambio del kit revertido por su propia medición.** El gate escrito antes
  de mirar es lo que lo hizo posible; con el harness anterior (n=1, juez ciego, sin veredicto
  de premisa) la 0022 se habría quedado, y habría sumado 28% de turnos en silencio.
