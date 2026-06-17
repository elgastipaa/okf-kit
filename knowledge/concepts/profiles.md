---
type: Concept
title: Perfiles — cómo OKF se adapta a cualquier dominio
description: Un perfil es un layout de carpetas + un vocabulario de type, según el dominio.
resource: ../../reference/profiles.md
tags: [okf, profiles, universality]
timestamp: 2026-06-17T00:00:00Z
---

OKF es **agnóstico al dominio**: la mecánica (markdown + frontmatter, `index.md`,
`log.md`, cross-links, progressive disclosure) es siempre la misma. Lo único que cambia
entre un proyecto de datos, uno de código y una wiki es **qué carpetas usás y qué ponés
en `type:`**. Esa elección es un **perfil**: un punto de partida, no una camisa de fuerza.

# Los perfiles
- **Código / Software** — `architecture/ decisions/ domain/ schema/ runbooks/ references/`.
  Tipos: `Architecture`, `Component`, `Decision`, `Domain Concept`, `Data Model`, `Runbook`…
- **Datos / Analytics** — `datasets/ tables/ references/{metrics,joins}/ glossary/`. Es el
  caso original de OKF. Tipos: `Dataset`, `Table`, `Metric`, `Join`…
- **Wiki** — organizado **por tema**, no por tipo, + `playbooks/` y `glossary`. Tipos:
  `Article`, `Note`, `Concept`, `Playbook`…
- **Mixto / Genérico** — combiná perfiles o inventá carpetas/tipos. OKF lo permite porque
  `type` es libre y la jerarquía es independiente del dominio.

Hay un **núcleo universal** de tipos que sirve en cualquier perfil: `Concept`, `Decision`,
`Reference`, `Playbook`, `Glossary`. El detalle completo de cada perfil está en
`reference/profiles.md`.

# Este bundle es un caso Mixto
El kit OKF se documenta a sí mismo con un perfil **Mixto**: es metodología (wiki-like)
pero ships tooling (linter, CI, hook) y tiene decisiones de diseño reales. Por eso usa
`architecture/`, `concepts/`, `decisions/`, `runbooks/` y `references/` a la vez. Ver
[la decisión de perfil de este bundle](../decisions/0006-dogfood-profile-choice.md).
