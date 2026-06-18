---
type: Decision
status: accepted
title: Hechos volátiles se generan del código, no se copian a mano
description: El kit ofrece un template y una convención para generar los hechos volátiles desde el código (script + check de frescura en CI), como punto medio entre copiar (drift) y solo apuntar.
tags: [okf, generated, drift, efficiency, eval]
timestamp: 2026-06-18T00:00:00Z
---

# Contexto
El kit tenía dos formas de tratar un valor que el código posee: copiarlo a la prosa (rápido de
leer pero **drift garantizado** y, peor, invisible — un agente lo repite confiado y mal, ver
[mapa-no-respuesta](0009-entrypoint-is-a-map-not-an-answer.md)) o dejar un **puntero** al
code-of-record (no driftea, pero el agente igual abre y lee el código). Para hechos **volátiles
que se preguntan seguido** —conteos, niveles de desbloqueo, flags ON/OFF, listas— ninguna es
ideal: la primera miente, la segunda cuesta turnos.

Repos maduros ya resolvieron esto: un `_generated/state.md` generado por un script (`wiki:gen`)
y verificado en CI (`wiki:check`) — rápido de leer **y** fiel por construcción.

# Decisión
El kit ofrece la convención de **hechos generados** (template `templates/knowledge/_generated.md`):
un archivo de SOLO LECTURA que un **script del repo genera desde el código**, con un **check de
frescura en CI** que falla si quedó desincronizado, y un header que prohíbe editarlo a mano. El
glosario/index lo apunta como code-of-record. Es el punto medio: la velocidad de tener la
respuesta escrita, sin el drift de escribirla a mano.

Aplica **solo si conviene**: los hechos deben ser volátiles *y* preguntados seguido (un
generador es código a mantener). Si son estables, alcanza el puntero del
[glosario](0007-domain-glossary-and-code-of-record.md). Enforcement liviano: se ofrece, no se
exige.

# Consecuencias
- Resuelve la tensión "concepto con la respuesta (rápido) vs puntero (sin drift)" sin elegir:
  el valor está escrito *y* no puede mentir porque se regenera y el CI lo gatea.
- Es la versión **segura** de "cachear respuestas en la KB": la insegura es copiar a mano.
- Complementa los otros mecanismos: glosario rutea, capas no-autoritativas descartan ruido,
  hechos generados dan los valores volátiles sin abrir código. El *por qué* sigue siendo prosa
  curada a mano (eso no se genera).

# Refinamiento — aplicalo REACTIVO, no especulativo (evidencia 2026-06-18)
Aplicado **a ciegas/especulativo** a un repo, el mecanismo NO rindió: un agente generó conteos
razonables pero **ningún consulta los leyó** (prefirió el code-of-record del glosario), no bajó
turnos, y un hecho *cercano-pero-distinto* al preguntado hasta lo confundió. Tres causas:
1. A ciegas no se sabe qué hecho es "caliente" → la cobertura no matchea las preguntas.
2. Compite con el glosario: si ya hay un puntero al code-of-record, el agente usa ese.
3. **Tensión con [mapa-no-respuesta](0009-entrypoint-is-a-map-not-an-answer.md):** el guardrail
   "verificá en la fuente, lo que parece respuesta puede ser coincidencia" empuja al agente a
   **desconfiar del archivo generado** e ir al código.

Por eso: generá un hecho **solo cuando lo observás preguntado seguido Y cambia seguido Y lo
hacés la ÚNICA ruta/autoridad** para ese hecho (el caso de los flags en `_generated/state.md`
de un repo real, donde el índice rutea ahí y a ningún otro lado). Especulativo es overhead (un
generador + CI a mantener) sin payoff. No lo agregues "por las dudas".
