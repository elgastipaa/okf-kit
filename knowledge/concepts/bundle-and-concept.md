---
type: Concept
title: Bundle y Concepto — las unidades de OKF
description: Un bundle es la carpeta knowledge/; un concepto es un .md con frontmatter.
tags: [okf, format, fundamentals]
timestamp: 2026-07-26T00:00:00Z
---

OKF representa conocimiento como **un directorio de archivos markdown con frontmatter
YAML**. Dos términos son la base de todo lo demás:

- **Bundle** — la colección jerárquica y autocontenida de documentos. Es la unidad de
  distribución, normalmente la carpeta `knowledge/` del repo.
- **Concepto** — una unidad de conocimiento = un archivo markdown. Puede describir algo
  tangible (una tabla, un módulo) o abstracto (una decisión, una convención). Su
  **Concept ID** es el path dentro del bundle sin el `.md` (`decisions/0001-orm`).

Dos nombres están **reservados** y NO son conceptos: `index.md` (listado de directorio)
y `log.md` (historial). Tampoco lo es nada con **prefijo `_`** (archivo o carpeta): queda
fuera del bundle conforme y el linter lo ignora — así viven los derivados (`_generated/`) y
los docs de trabajo efímeros (`_changes/`). Cualquier otro `.md` es un concepto y **debe**
llevar frontmatter con `type`. Las reglas exactas están en
[el formato OKF](../references/okf-format.md).

# Por qué importa
La granularidad "un concepto por archivo" es lo que habilita el
[progressive disclosure](progressive-disclosure.md): el agente lista conceptos por su
`index.md` y carga solo los que necesita. Si un archivo cubre dos ideas, se parte.
