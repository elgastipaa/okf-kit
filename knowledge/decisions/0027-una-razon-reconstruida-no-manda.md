---
type: Decision
status: accepted
verify: python3 scripts/okf_lint_test.py 2>&1 | grep -q "reconstruida del código declarada como normativa"
origen: dictado
title: Una razón reconstruida del código no manda, y si nadie la sabe se deja como pregunta
description: "El kit fabricaba porqués al escribir el bundle y les daba autoridad normativa; ahora una razón deducida se declara y no puede ser accepted."
tags: [okf, correctness, confabulacion, decisiones]
timestamp: 2026-08-04T00:00:00Z
---

# Contexto

Se midió el eje "por qué" con ground truth **dictado por el dueño del repo**, sobre seis
preguntas sacadas del código de un repo real. De las seis, **tres no las sabía nadie**: las
decidió una IA meses antes y no dejó registro.

El resultado de la medición fue que los dos brazos —con el kit y sin ninguna capa— inventaron
una explicación en **9 de 9 corridas**. Pero al buscar *dónde* nacía la invención apareció
algo peor:

**La invención no ocurría al responder. Ocurría al escribir el bundle.**

El agente que había aplicado el kit a ese repo —a ciegas, leyendo el código— escribió en un
runbook *"**no es cosmético**: el repo se trabaja en entornos donde npm no deja el bit de
ejecución…"*, y una **decisión entera con `status: accepted`** explicando muy bien por qué
"se eligió" el esquema de persistencia. El dueño, sobre las dos: *"no lo sé, lo hizo otra
IA"*.

Es peor que confabular al responder por tres razones: es **consistente** (siempre la misma
reconstrucción), es **citable** (viene con `resource:`), y **el contrato la trata como
normativa** — o sea que el kit le habría dicho a alguien que su código viola una decisión que
nunca se tomó.

**La causa no era el criterio del agente, era qué le pedía el template**, y hay evidencia
directa: en ese mismo repo, el mismo agente **dejó tres preguntas abiertas** — y todas están
en `roadmap.md`, el **único** template que las pedía. Donde le pedían un "Contexto", fabricó.

# Decisión

**Una razón que se dedujo del código no manda sobre el código.**

1. Las decisiones declaran `origen: dictado | reconstruido`. Ausente = `dictado` (no rompe
   bundles existentes).
2. **`origen: reconstruido` con `status: accepted` es ERROR del linter**, no warning: un
   warning se ignora y esto no se puede ignorar. Una reconstrucción vive en `proposed` hasta
   que alguien que sabe la confirme.
3. **Si nadie sabe por qué, no se escribe una decisión.** Se deja
   `> Pendiente de confirmar: …`, que ya era la convención del roadmap y ahora la ofrecen
   también los templates de concepto y de decisión.
4. `okf_lint.py --questions` lista esas preguntas, y **`okf-init`/`okf-migrate` terminan
   entregándoselas al usuario**. Si no hay usuario en sesión, hay que decirlo: un default
   silencioso es indistinguible de una respuesta informada.

# Consecuencias

- **El kit deja de convertir su punto ciego en autoridad.** No puede evitar que un modelo
  confabule —eso no lo controlamos—, pero sí puede dejar de **institucionalizar** la
  confabulación con frontmatter y numeración de ADR.
- **"No sé" pasa a ser un resultado entregable del init**, no un fracaso. Una pregunta abierta
  es información: le dice al próximo agente que ahí **no hay respuesta**, en vez de darle una
  falsa.
- **El valor del kit se reformula, y es más honesto:** no puede recuperar un porqué que nadie
  escribió. Puede evitar que el próximo se pierda, y puede **producir las preguntas** que solo
  una persona puede contestar. Eso último no lo hacía y es, probablemente, lo más valioso que
  hace un init.
- **MEDIDO (2026-08-05), y pasa el gate escrito antes de mirar.** En las dos preguntas donde
  se aplicó el fix, la invención pasó de **6/6 a 0/6**: las dos contestan ahora "no hay razón
  registrada". En las dos que se dejaron sin tocar sigue en 100%. Total del brazo: **11/18 →
  6/18 inventadas**, contra 14/18 sin capa. Los controles se movieron una celda cada uno, así
  que el efecto está muy por encima del ruido.
- **La lectura honesta es más chica que el número.** Esto no muestra que el kit haga al modelo
  más certero: muestra que **el bundle manda sobre lo que el agente contesta**, que es
  exactamente por qué la fabricación era tan dañina. El rework no cambia ese mecanismo — lo da
  vuelta, para que lo que se propague sea "no se sabe" en lugar de una explicación inventada.
- Sembrar la razón real que dictó una persona llevó esa pregunta de "no hay razón registrada"
  a **correcta 3/3**. Eso mide otra cosa —que el kit preserva lo que le contás— y es la única
  promesa del kit que quedó demostrada de punta a punta.
