---
type: Architecture
title: El modelo de tres capas de contexto
description: El contexto se parte en entrypoint, conocimiento y procedimientos; el bundle es el corazón.
resource: ../../README.md
tags: [okf, architecture, layers]
timestamp: 2026-06-17T00:00:00Z
---

OKF separa el contexto de un proyecto en **tres capas**, cada una con una pregunta
distinta. Entender esta separación es entender por qué el bundle `knowledge/` es
obligatorio y las otras capas son opcionales.

# Las capas
| Capa | Vive en | Responde | La lee |
|---|---|---|---|
| **Entrypoint** | `AGENTS.md` (raíz del repo) | "¿Quién soy, qué reglas sigo, dónde está todo?" | Todo agente, al arrancar |
| **Conocimiento** | `knowledge/` (el bundle OKF) | "¿Qué es esto y **por qué**?" | El agente, bajo demanda, vía `index.md` |
| **Procedimientos** | `.claude/skills/` o markdown vendor-neutral | "¿**Cómo** hago la tarea X?" | El agente, cuando la tarea matchea |

La capa **Conocimiento** es el corazón y **siempre va**. Entrypoint y Procedimientos son
convenientes cuando un *agente de código* trabaja el repo; para una wiki o un bundle de
datos navegado a mano, se omiten y el entrypoint pasa a ser `knowledge/index.md`.

# La cuarta capa es una trampa
La **memoria privada de la herramienta** (p.ej. la memoria de Claude Code en
`~/.claude/...`) es útil pero **no es portable ni vive en el repo**. La fuente de verdad
debe ser el bundle en git. Ver
[conocimiento como source of truth](../decisions/0005-knowledge-as-source-of-truth.md).

# Por qué cross-vendor
Las tres capas funcionan con cualquier IA: `AGENTS.md` es lo más cercano a un estándar
que toda herramienta lee, el bundle es markdown plano, y los procedimientos son markdown
que corre como skill de Claude *o* se sigue directo. Ver
[la decisión de vendor-neutralidad](../decisions/0004-vendor-neutral-no-external-apps.md).
