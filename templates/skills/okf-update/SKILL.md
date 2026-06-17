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
cualquier agente leyendo estas instrucciones (ver `reference/install-per-tool.md`).

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

Si lo que cambió ya se deduce leyendo el código, **no lo dupliques**: linkealo con
`resource` o con un cross-link. El bundle captura lo que el código no dice.

# Cómo hacerlo

1. **Identificá el concepto y su carpeta.** ¿Es una decisión, un concepto de
   dominio, un runbook, una reference, una tabla, un artículo? La carpeta y el
   `type` dependen del **perfil** del bundle (código / datos / wiki). Mirá cómo
   está organizado este bundle y seguí esa convención; si está disponible,
   consultá `reference/profiles.md`.
2. **Escribí o editá el archivo** en la subcarpeta correcta, con frontmatter
   completo en este orden: `type` (requerido), `title`, `description` (una frase),
   `timestamp` (ahora, ISO 8601), `tags`, y `resource` si apunta a código/dashboard.
   (Si un valor lleva `:`, **entrecomillalo** o rompe el YAML.)
3. **Cross-linkeá** a conceptos relacionados con links markdown **relativos al archivo**.
4. **Actualizá el `index.md`** del directorio: en una carpeta **hoja**, la entrada va
   bajo un heading `# {type}`; en la **raíz**, bajo `# Subdirectories`. Cada entrada es
   `* [Título](archivo.md) - <description del frontmatter>`.
5. **Agregá una línea a `knowledge/log.md`** bajo la fecha de hoy
   (`## YYYY-MM-DD`), ej: `* **Update**: <qué cambió> ([link](decisions/0007-x.md)).`
   (link **relativo al archivo** desde la raíz del bundle, nunca con `/`).
6. **Si una regla dura cambió**, reflejala también en `AGENTS.md` (mantenelo chico).

# Reglas

- **No dupliques.** Una verdad, un archivo. Si está en el código, linkealo.
- **Capturá el por qué**, no el qué.
- **Una `description` de una sola frase** — se usa verbatim en los `index.md`.
- **No inventes.** Si no sabés el porqué de algo, preguntale al usuario antes de
  escribirlo.
- **Conformidad OKF:** todo `.md` no reservado (`index.md`, `log.md`) lleva
  frontmatter con `type` no vacío.
