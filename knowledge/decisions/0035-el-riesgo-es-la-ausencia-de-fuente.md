---
type: Decision
status: accepted
origen: dictado
title: El riesgo no es que la fuente la haya escrito una IA, es que no haya fuente
description: "Cosechar de un documento escrito preservó decisiones reales aunque lo hubiera tecleado una IA, así que el kit no agrega gating por autoría de la fuente."
tags: [okf, confabulacion, eval, alcance]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

Al auditar un repo cuyo bundle había escrito una versión vieja del kit, el dueño confirmó que
el `DECISIONS.md` de 6699 líneas del que se cosechó **lo había escrito una IA**. La conclusión
inmediata fue que la autoridad se "lavaba" un paso más arriba: si `dictado` significa *"te lo
contó una persona"* y en la práctica se chequea como *"cita una fuente escrita"*, un documento
escrito por una IA produciría decisiones que citan fuente y siguen siendo fabricadas.

**Se midió antes de arreglar nada**, con una muestra de 12 sobre 51 y semilla registrada. El
dueño clasificó **12 de 12 como "la decidí yo"**. Cero fabricadas, cero "no sé".

La hipótesis del lavado **no se sostuvo**: *"lo escribió una IA"* y *"lo decidió una IA"* son
cosas distintas. Esa IA estaba **transcribiendo decisiones del dueño**.

# Decisión

**El factor de riesgo es la ausencia de fuente, no la autoría del intermediario.** El kit **no
agrega** gating por autoría de los documentos que cosecha —ni una pregunta obligatoria de
"¿quién escribió esto?" ni un `origen` degradado por venir de un doc de autor desconocido.

Lo que sigue vigente y es lo que la evidencia respalda: **reconstruir un porqué desde el código,
sin ninguna fuente escrita, es lo que fabrica** ([0027](0027-una-razon-reconstruida-no-manda.md)).
Cosechar de un documento —aunque lo haya tecleado un agente— preservó decisiones reales en el
único repo donde se midió.

# Consecuencias

- **Una regla que se iba a agregar por miedo, no se agrega.** El costo de equivocarse en esta
  dirección era alto: habría degradado a `proposed` decenas de decisiones legítimas en todo repo
  vibecodeado, que son justamente los repos que el kit apunta.
- **No está probado que el lavado sea imposible**, solo que no ocurrió acá. Un doc escrito por
  un agente **sin nadie revisando** produciría el efecto temido. Si aparece un caso, se
  supersede esta decisión con ese caso como evidencia — no con la intuición de vuelta.
- **Vale como precedente de método**: la alarma se levantó, se dejó por escrito, **no se
  arregló antes de medir**, y la medición la refutó. Arreglar primero habría convertido la
  medición en una confirmación de lo que ya se creía
  ([0028](0028-la-medicion-manda-y-el-gate-se-escribe-antes.md)).
