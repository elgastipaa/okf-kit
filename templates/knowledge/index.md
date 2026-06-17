<!--
  TEMPLATE de index.md. Los index.md NO llevan frontmatter, EXCEPTO el de la RAÍZ
  del bundle, que puede declarar okf_version (versión del FORMATO, de la spec) y
  kit_version (revisión del KIT con que se inicializó; okf-init lo completa desde
  VERSION). Links SIEMPRE relativos al archivo. Borrá este comentario al usar.

  Hay dos formas según dónde esté el index:

  (A) RAÍZ del bundle (knowledge/index.md) → lista los SUBDIRECTORIOS bajo
      "# Subdirectories". Es el bloque de abajo.

  (B) HOJAS (knowledge/<carpeta>/index.md) → agrupa los CONCEPTOS bajo un heading
      por su `type`, así (sin frontmatter):

          # Decision

          * [Usamos cola para emails](0007-email-queue.md) - Los emails salen async.
          * [DB solo local](0002-db-local.md) - Migraciones y seeds por CLI local.

          # Reference

          * [useActionState encoding](useactionstate.md) - Los forms mandan FormData.

  En ambos casos: cada entrada es `* [Título](link-relativo) - <description del
  frontmatter del concepto>`. Mantené las descripciones en una frase.
-->
---
okf_version: "0.1"
kit_version: "{{KIT_VERSION}}"   # okf-init lo reemplaza con el contenido de VERSION
---

# Subdirectories

* [decisions](decisions/index.md) - {{descripción de qué hay en esta carpeta}}
* [references](references/index.md) - {{descripción}}
* [runbooks](runbooks/index.md) - {{descripción}}
