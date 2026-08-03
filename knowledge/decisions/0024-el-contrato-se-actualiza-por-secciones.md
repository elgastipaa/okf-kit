---
type: Decision
status: accepted
title: El contrato se actualiza por secciones, y por eso lo del kit y lo del usuario no se mezclan en un párrafo
description: El instalador reemplaza solo sus propias secciones del AGENTS.md y conserva las del usuario, así que el contrato deja de estar congelado en la versión que lo instaló.
tags: [okf, upgrade, instalador, contrato]
timestamp: 2026-08-03T00:00:00Z
---

# Contexto

`okf_install.py --upgrade` actualizaba scripts, skills, CI, hook y el sello de versión, pero
**no tocaba el `AGENTS.md`** — a propósito, porque tiene contenido del usuario y pisarlo es la
pérdida de datos que arregló la 0.7.4.

La consecuencia no la había mirado nadie: **ninguna mejora del contrato llegaba jamás a un
repo ya instalado.** Cada instalación quedaba congelada en el texto del día que nació. Se
descubrió al tener que portar a mano un cambio del contrato a un repo de prueba; el que lo
portó sabía qué había cambiado porque lo había escrito una hora antes. Un usuario con OKF
instalado hace meses no tiene cómo.

Al intentar automatizarlo apareció la causa real, y no era una función faltante del
instalador: **el contrato era inactualizable por su forma.** Las capas no autoritativas vivían
*dentro* de §1, con el texto del usuario y el del kit **entrelazados en el mismo párrafo** —en
un repo real el usuario había escrito antes de la frase fija del kit y también después. No hay
forma mecánica de reemplazar uno sin pisar el otro.

# Decisión

**El contrato se divide por dueño, a nivel de sección**, y el instalador actualiza solo las
suyas:

- **Del kit** (se reemplazan enteras en cada `--upgrade`): `## 1.`, `## 2.`, `## 3.` y
  `## Procedimientos`.
- **Del usuario** (se conservan palabra por palabra): el título y la descripción del stack,
  `## Reglas duras`, `## Capas NO autoritativas` —que **deja de estar embebida en §1 y pasa a
  ser su propia sección**— y **cualquier sección que el usuario haya agregado** y el kit no
  conozca.

El apareo entre versiones es por **prefijo** (`## 2.`), no por el título completo: los títulos
cambian entre revisiones y aparear por texto exacto abortaría sin motivo.

**Se planta y delega, en vez de adivinar**, en los tres casos donde no puede garantizar que no
destruye nada: `AGENTS.md` con cambios sin commitear o repo sin git (no hay red para
devolverlo), contrato en el formato viejo con las capas embebidas en §1, y una sección del kit
que ya no existe en la revisión nueva. En los tres avisa qué hacer; ninguno falla en silencio.

# Consecuencias

- **Mueve el merge del contrato de "criterio" a "plomería"**, que es el corte que define la
  [0017](0017-plomeria-determinista-vs-criterio.md). El principio de esa decisión no cambia
  —lo mecánico al script, lo que requiere inteligencia al agente—; lo que cambió es que este
  merge **dejó de requerir inteligencia** cuando se separaron las secciones. El resto de lo
  que la 0017 asigna al agente (sembrar conceptos, completar placeholders) sigue igual.
- **Obliga a una regla de forma para siempre:** ninguna sección del contrato puede mezclar
  prosa del kit con contenido del usuario en el mismo párrafo. Si una convención nueva
  necesita datos del repo, van en su propia sección y el kit apunta.
- **Hay una migración one-time** para todo repo instalado antes de la 0.7.5: mover las capas
  no autoritativas a su sección. El instalador la detecta y la pide; no la hace él, porque ahí
  es exactamente donde el texto está entrelazado.
- El gate lo cubre con **dos asserts y sus dos roturas**: que el upgrade conserve el contenido
  del usuario, y que efectivamente reemplace la prosa vieja del kit. Las dos mitades pueden
  fallar solas —no actualizar, o actualizar de más— y la segunda es destructiva.
