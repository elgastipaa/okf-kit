<!--
  TEMPLATE de glosario de dominio. Copialo a la raíz del bundle o a references/ como
  `glossary.md` (sin el `_`) y BORRÁ este comentario (el archivo debe empezar con `---`).

  PARA QUÉ: las preguntas a nivel TÉRMINO/stat ("¿qué es ATK?", "¿qué es el Vigor?") son
  las que más caro le salen a un agente — sin un mapa término→página, fanea al código a
  reconstruir el dato. Un glosario que rutea cada término a (a) su página canónica y (b) su
  *code-of-record* (el archivo donde vive el VALOR exacto) colapsa esas preguntas de muchos
  turnos a ~1. Medido: ~−60% de turnos en un repo de juego (ver okf-kit decisión 0007).

  REGLA: el glosario son PUNTEROS, no la fuente de verdad. Una línea por término; el detalle
  vive en el canónico y el valor en el code-of-record. No copies el valor — linkealo (un
  número a mano = drift). Si la fila y el código se contradicen, gana el código.

  Sumá una fila SOLO para términos que un recién llegado preguntaría y que hoy obligan a
  grepear. No conviertas esto en un diccionario exhaustivo.
-->
---
type: Reference
title: {{Glosario de dominio de <proyecto>}}
description: Términos/stats del dominio → respuesta en una línea + página canónica + code-of-record.
tags: [glossary, domain]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

> **Para preguntas a nivel término/stat, entrá por acá antes de grepear código.** Una línea
> de respuesta + la página canónica (el *por qué*) + el code-of-record (el *valor* exacto).
> Si una fila y el código se contradicen, **gana el código** (la fila es un bug a arreglar).

| Término | Qué es (1 línea) | Canónico (el porqué) | Code-of-record (el valor exacto) |
|---|---|---|---|
| **{{TÉRMINO}}** | {{definición en una línea}} | [{{página}}]({{../dir/x.md}}) | `{{ruta/al/archivo.ext}}` (o `:línea`) |
| **{{TÉRMINO}}** | {{…}} | [{{…}}]({{…}}) | {{— si no aplica}} |
