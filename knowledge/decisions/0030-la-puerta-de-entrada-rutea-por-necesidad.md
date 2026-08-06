---
type: Decision
status: accepted
origen: dictado
title: La puerta de entrada del bundle rutea por necesidad, no lista por tipo
description: "El index.md raíz arranca con una tabla necesidad → 1-3 archivos → fuente de verdad, y el listado por type queda abajo."
tags: [okf, index, economia-de-contexto]
timestamp: 2026-08-06T00:00:00Z
---

# Contexto

Un índice organizado por `type` —`# Decision`, `# Reference`, `# Subdirectories`— está
organizado por **la taxonomía del kit**, no por **las preguntas del que llega**. Obliga a
navegar: índice raíz → índice de carpeta → concepto. Midiendo cinco condiciones sobre el mismo
repo apareció que navegar sale aproximadamente **igual de caro que grepear el código**, que es
por qué un bundle bien escrito pero listado por tipo quedó indistinguible de no tener capa.

La capa que ganaba esa comparación —escrita a mano por el dueño del repo— tenía en cambio una
tabla *"Si necesitás… | Leé | Fuente de verdad"* que manda directo a 1-3 archivos.

# Decisión

**El `index.md` de la raíz arranca con `# Por dónde empezar`**: una tabla con una fila por
pregunta que el repo recibe de verdad, **en las palabras del que pregunta**, apuntando a
**1-3 archivos concretos** y declarando su fuente de verdad.

- **Mandar a una carpeta no cuenta**: es volver a hacer navegar.
- El listado por `type` **se conserva abajo**, intacto. `OKF-SPEC.md` §5 lo llama "convención
  de la implementación de referencia", así que la tabla se suma y **ningún bundle instalado
  deja de ser válido**.
- El instalador siembra las filas que puede saber solo (los chequeos siempre, el rumbo si va la
  capa de futuro); las del repo las escribe el agente en `okf-init`.

# Consecuencias

- **El kit no reclama un número por esto.** El brazo medido no separó del anterior por encima
  del ruido del instrumento ([0032](0032-el-instrumento-tiene-un-piso-de-resolucion.md)). Se
  sostiene como práctica —no cuesta nada, no degradó nada, y es la única configuración que
  aterrizó sobre los números de la capa humana en las tres métricas a la vez— **no como
  resultado**. La prosa del kit lo dice sin cifra atrás.
- **Es la parte más fácil de hacer mal.** Un agente apurado reproduce la taxonomía del kit
  porque es lo que tiene a mano. Por eso está afirmado en los dos lados —lo que siembra el
  instalador y lo que completa `okf-init`— y los dos tienen su assert con rotura probada.
