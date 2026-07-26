---
name: okf-update
description: >
  Mantiene actualizado el bundle de contexto OKF del repo (la carpeta knowledge/).
  Usalo cuando se toma una decisión de diseño, cambia la arquitectura o el schema,
  aparece un gotcha, o cuando el usuario explica algo que "el agente ya debería
  saber". Convierte ese conocimiento en conceptos OKF versionados.
---

Este repo usa **OKF** (Open Knowledge Format) para su contexto: la carpeta
`knowledge/` es un bundle de markdown + frontmatter YAML que documenta el *qué* y
el *por qué* del proyecto. El entrypoint es `AGENTS.md` en la raíz. Tu trabajo con
este skill es mantener ese bundle fresco para que ningún contexto se pierda.

Es un **procedimiento vendor-neutral**: corre como skill de Claude Code *o* lo sigue
cualquier agente leyendo estas instrucciones. **Es autosuficiente**: no depende de que
`okf-kit` siga en disco.

# Cuándo disparar

Actualizá el bundle cuando pase cualquiera de estas:

- Se **toma o se descubre una decisión** no trivial → nuevo archivo en
  `knowledge/decisions/NNNN-<slug>.md` (numerado, una decisión por archivo).
- Cambia la **arquitectura, el schema o el modelo de datos** → editá el concepto
  afectado en `knowledge/architecture/` o `knowledge/schema/`.
- Aparece un **gotcha / quirk** (de un framework, una API, el setup local) →
  `knowledge/references/<slug>.md` con `# Citations`.
- El usuario te **explica algo que el código no dice** y que vas a necesitar de
  nuevo → es un concepto faltante; escribilo en la carpeta que corresponda.
- Cambia un **procedimiento operativo** (build/test/deploy/DB) → `knowledge/runbooks/`.
- **Si este repo lleva capa de futuro** (existe `knowledge/_changes/`): al cerrar un cambio,
  su harvest usa este mismo procedimiento para escribir cada pieza — el ciclo del cambio en
  sí es del procedimiento `okf-plan`. Si no existe esa carpeta, ignorá este punto.

Si lo que cambió ya se deduce leyendo el código, **no lo dupliques**: linkealo con
`resource` o con un cross-link. El bundle captura lo que el código no dice.

# Cómo hacerlo

1. **Identificá el concepto y su carpeta.** ¿Es una decisión, un concepto de
   dominio, un runbook, una reference, una tabla, un artículo? La carpeta y el
   `type` dependen del **perfil** del bundle (código / datos / wiki). Mirá cómo
   está organizado este bundle y seguí esa convención — **es la fuente**: los `type` y las
   carpetas que ya usa mandan sobre cualquier default.
2. **Escribí o editá el archivo** en la subcarpeta correcta, con frontmatter
   completo en este orden: `type` (requerido), `title`, `description` (una frase),
   `timestamp` (ahora, ISO 8601); `tags` y `resource` si aplican.
   (Si un valor lleva `:`, **entrecomillalo** o rompe el YAML.)
   **Si es una decisión, lleva además `status: accepted`.** No es decorativo: lo normativo
   se identifica por ese campo, así que una decisión sin `status` queda invisible para la
   auditoría de cumplimiento (`okf-verify`, Nivel 4) — existe, pero no obliga a nadie.
3. **Cross-linkeá** a conceptos relacionados con links markdown **relativos al archivo**.
4. **Actualizá el `index.md`** del directorio: la entrada va bajo un heading `# {type}` —
   en una carpeta **hoja** y también en la **raíz**, si el concepto vive ahí (`roadmap.md`,
   `glossary.md`). `# Subdirectories` del index raíz es para las **carpetas**: si creaste
   una, sumala ahí también. Cada entrada es
   `* [Título](archivo.md) - <description del frontmatter>`.
5. **Si mantenés `log.md`**, agregá una línea bajo la fecha de hoy
   (`## YYYY-MM-DD`), ej: `* **Update**: <qué cambió> ([link](decisions/0007-x.md)).`
   (link **relativo al archivo**, nunca con `/`). Si tu log es git + `decisions/`, saltá esto.
6. **Si una regla dura cambió**, reflejala también en `AGENTS.md` (mantenelo chico).

# Deprecar o reemplazar algo

El conocimiento viejo no se borra a las apuradas ni se edita "para darlo de baja":

- **Reemplazar una decisión:** creá una decisión **nueva** (`status: accepted`) con
  `supersedes: NNNN`, y poné en la vieja `status: "superseded by MMMM"`. Así queda el
  camino de migración, no un agujero.
- **Deprecar un concepto:** movélo a `knowledge/archive/` o marcá arriba
  `SUPERSEDED → ver <link>`. **Nombrá explícito el concepto viejo** (el término, la
  flag, la clase) para que un `grep` futuro lo encuentre.

# Reglas

- **No dupliques.** Una verdad, un archivo. Si está en el código, linkealo (un número
  a mano = drift garantizado).
- **Gana el código (conceptos descriptivos).** Si un concepto que *describe* algo
  (arquitectura, schema, dominio, runbook, reference, glosario) contradice la fuente,
  el concepto es el bug — corregilo o deprecalo, no al revés.
- **Salvo que el concepto sea normativo — ahí el bug es el código.** Una **decisión
  aceptada** y una **convención** prescriben lo que debe cumplirse (y, si el repo lleva capa
  de futuro, también el rumbo y el *resultado esperado* de un cambio activo). Si el código los viola: **no los edites para
  emparejarlos** ni sigas de largo — avisale al usuario y ofrecé arreglar el código **o**
  superseder la decisión explícitamente (ver "Deprecar o reemplazar"). Editarlos en
  silencio borra la razón por la que alguien decidió eso.
- **Capturá el por qué**, no el qué.
- **Una `description` de una sola frase** — se usa verbatim en los `index.md`.
- **No inventes.** Si no sabés el porqué de algo, preguntale al usuario antes de
  escribirlo.
- **Conformidad OKF:** todo `.md` no reservado (`index.md`, `log.md`) lleva
  frontmatter con `type` no vacío.
