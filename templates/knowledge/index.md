<!--
  TEMPLATE de index.md. Los index.md NO llevan frontmatter, EXCEPTO el de la RAÍZ
  del bundle, que puede declarar okf_version (versión del FORMATO, de la spec) y
  kit_version (revisión del KIT con que se inicializó; okf-init lo completa desde
  VERSION). Links SIEMPRE relativos al archivo. Borrá este comentario al usar —
  y también el comentario `# okf-init lo reemplaza…` de la línea de kit_version.

  Hay dos formas según dónde esté el index:

  (A) RAÍZ del bundle (knowledge/index.md) → arranca con "# Por dónde empezar",
      la tabla que RUTEA POR NECESIDAD, y después lista los SUBDIRECTORIOS bajo
      "# Subdirectories". Si hay conceptos EN la raíz (p.ej. roadmap.md o un
      glossary.md), van entre medio, agrupados por type como en las hojas.

      La tabla es la parte que más rinde y la más fácil de hacer mal: va en las
      palabras del que PREGUNTA, no en las categorías del kit, y manda a 1-3
      archivos concretos. Mandar a una carpeta es volver a hacer navegar, que es
      exactamente lo que se paga en turnos.

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

# Por dónde empezar

| Si necesitás… | Leé | Fuente de verdad |
|---|---|---|
| {{la pregunta, en las palabras del que la hace}} | {{[`archivo.md`](archivo.md) — 1 a 3, nunca una carpeta}} | {{código / doc / el equipo}} |

# Roadmap

* [Rumbo de {{proyecto}}](roadmap.md) - {{description del frontmatter del roadmap}}

# Subdirectories

* [decisions](decisions/index.md) - {{descripción de qué hay en esta carpeta}}
* [references](references/index.md) - {{descripción}}
* [runbooks](runbooks/index.md) - {{descripción}}
