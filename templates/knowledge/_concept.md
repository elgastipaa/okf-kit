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

# Citations
[1] {{[Título](URL) — si hiciste afirmaciones tomadas de algo externo; si no, borrá esta sección}}
