---
type: Decision
title: "La capa de futuro se queda, con una condición medida: el roadmap solo paga si es correcto y auto-contenido"
description: Medido en dos repos con n=3 — un roadmap vigente y auto-contenido baja las preguntas de rumbo de 12 a 4 turnos; uno desactualizado o que solo rutea cuesta más que no tenerlo.
status: accepted
verify: none
verify_note: la condición se estableció midiendo; re-medirla cuesta plata y no la corre un check
tags: [future-work, measurement, roadmap, negative-result]
timestamp: 2026-07-26T00:00:00Z
---

# Contexto

La [capa de futuro](0011-future-work-layer.md) se diseñó y se auto-aplicó sin medirse. Por el
criterio [reactivo, no especulativo](0010-generated-volatile-facts.md), no podía complejizarse
ni darse por buena hasta tener números. Se midió con el harness de `templates/eval/` en dos
repos conejillo, n=3 por pregunta, leyendo todas las respuestas a mano y verificando sus
afirmaciones contra el código.

# Decisión

**La capa se queda**, y su valor queda condicionado a una propiedad que hay que sostener.

## Lo que paga

Con un roadmap **vigente y auto-contenido** (dice cuál es el trabajo activo y en qué punto
está), la pregunta *"¿qué sigue?"* cae de **12.3 a 4.0 turnos** y de **337K a 93K** de
contexto leído. Los rangos no se solapan (11/12/14 contra 4/4/4) y la variante con capa tiene
**dispersión cero**. La comparación es válida: la misma información estaba disponible en las
dos ramas — lo que cambia es tener un rumbo autoritativo en vez de rastrear capas declaradas
no-confiables.

El **harvest se corre solo**: ante "ya quedó andando, cerralo", un agente en frío hizo el
ciclo completo (decisión nueva + índices + log + roadmap + conceptos afectados + doc borrado)
y **verificó en vez de creerle al usuario** — corrió los smokes antes de dar nada por cerrado,
y renegoció explícitamente los puntos del spec que la realidad no cumplía.

## Lo que no paga, y es el resultado negativo que importa

**Un roadmap desactualizado cuesta más que no tener roadmap.** En el segundo conejillo el
rumbo afirmaba trabajo en curso que la fuente de verdad daba por terminado: los agentes
gastaron turnos **descubriendo y corrigiendo** esa mentira (hasta 22 turnos en una corrida),
y la rama **sin** roadmap encontró mejor información que la rama con roadmap. Un rumbo que
solo **rutea** a otra capa de planes tampoco compra el ahorro: la mejora viene de que el
roadmap sea **una respuesta**, no un índice.

**La capa puede fabricar contexto falso.** Ante una idea fuera de alcance, un agente aplicó el
disparador correctamente —no la implementó, la anotó en "Después"— pero **nunca chequeó el
código**: anotó como *feature nueva* algo que el repo ya tenía implementado, y esa premisa
falsa quedó **escrita en el roadmap**. El mismo agente sin la capa había contestado bien.

> **La lección central, y es estructural, no de los agentes.** Quien escribió el roadmap
> desactualizado del segundo conejillo fue el mismo autor de esta medición, cometiendo
> exactamente el error que la medición buscaba: infirió "en curso" de señales plausibles
> (specs presentes, commits recientes) sin abrir el archivo que decía *"STOP, esta es la
> fuente de verdad"* y declaraba el trabajo completado. **Cualquier capa que parezca
> autoritativa y sea más barata de leer que la fuente invita a saltearse la fuente.** La capa
> de futuro no reemplaza la verificación: la hace más barata de *saltear*.

# Consecuencias

- El disparador de scope creep exige **chequear si la idea ya existe en el código** antes de
  anotarla, en el contrato y en `okf-plan` (re-medido 3/3: detecta lo existente, no lo anota).
- **El roadmap entra en el ciclo de frescura como cualquier concepto.** Un rumbo que afirma
  trabajo terminado es un bug del documento con el costo medido arriba; el Nivel 4 de
  verificación y las señales anti-rot de `reference/maintaining.md` aplican.
- **Interop:** cuando el repo ya tiene su capa de planes, seguir ruteando desde el roadmap
  (no montar `_changes/`) sigue siendo lo correcto para no tener dos dueños — pero **no se
  obtiene el ahorro de retrieval**, y hay que decirlo en vez de venderlo.
- Queda abierto, sin medir lo suficiente: **el doc de `_changes/` se saltea** cuando el agente
  juzga que termina en una sola corrida. Es racional (crearlo y cosecharlo en el mismo turno
  es ceremonia) pero derrota el propósito cross-sesión, y el agente no puede saberlo de
  antemano. Candidato: que el umbral sea "¿podría no terminar en esta sesión?" en vez de
  "¿es no trivial?". No se cambia hasta medirlo.

# Verificación

```
python3 templates/eval/run-eval.py <repo> <golden-set> --grade
```
Con un golden-set que incluya preguntas de rumbo. **Leé las respuestas a mano**: el juez
automático puntuó `trampa-ok` una respuesta con premisa falsa y `incorrecta` tres respuestas
correctas. Ninguno de los defectos de esta medición lo detectó el propio instrumento.
