<!--
  TEMPLATE genérico de concepto (prefijo "_" → el linter lo ignora; no es un concepto).
  Copialo a un archivo SIN el "_" (p.ej. <kebab-case>.md o 0001-x.md) en la subcarpeta
  que corresponda, completá frontmatter y body, y BORRÁ este comentario: el archivo
  debe EMPEZAR con `---`, o no es un concepto OKF válido.
  Elegí `type` del perfil correcto en reference/profiles.md. La `description` es UNA frase.
-->
---
type: {{del núcleo universal o del perfil: Decision | Reference | Table | Article | Component | ...}}
title: {{Nombre legible}}
description: {{Una sola frase que resume el concepto.}}
resource: {{URL o path al código/dashboard/ticket — opcional, borrá si no aplica}}
tags: [{{tag1}}, {{tag2}}]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

{{1-3 párrafos: qué es, qué representa, cómo se usa. Capturá el POR QUÉ y lo que el
código no dice. Lo que sí se deduce del código, linkealo con `resource` o un
cross-link en vez de copiarlo.}}

{{Usá headings convencionales cuando apliquen: `# Schema`, `# Examples`. Cross-linkeá
a conceptos relacionados, ej: ver [otro concepto](../decisions/0001-foo.md).}}

<!-- ¿Y SI NO SABÉS EL POR QUÉ?  Escribilo. No lo reconstruyas.

     El código te muestra QUÉ hace algo, y desde ahí es facilísimo redactar una razón
     convincente de por qué "se eligió" — cuando en realidad no lo eligió nadie: salió
     así, lo hizo otra IA, o es deriva de meses. Una razón inventada es peor que ninguna:
     suena bien, nadie la chequea, y el próximo agente la lee como un hecho.

     Cuando no puedas deducirlo de la fuente y no tengas a quién preguntarle, dejá:
         > Pendiente de confirmar: por qué {{X}} es así. No hay razón registrada.
     y contáselo al usuario cuando termines. Esa línea es información de verdad: le dice
     al próximo que ACÁ NO HAY RESPUESTA, en vez de darle una falsa. -->

# Citations
[1] {{[Título](URL) — si hiciste afirmaciones tomadas de algo externo; si no, borrá esta sección}}
