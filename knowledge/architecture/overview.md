---
type: Architecture
title: Qué es el kit OKF y cómo está armado
description: El kit es una guía self-contained + templates para montar contexto OKF en cualquier repo.
resource: ../../README.md
tags: [okf, overview, methodology]
timestamp: 2026-06-17T00:00:00Z
---

El kit OKF (carpeta `okf-kit`) **no es una app**: es una **guía ejecutable + una
librería de templates** que un agente sigue para montar un sistema de "ingeniería de
contexto" duradero sobre *cualquier* repo. El producto entregado al repo destino es un
bundle `knowledge/` (markdown + frontmatter) más, opcionalmente, un entrypoint y unos
procedimientos. El kit en sí casi no tiene código: lo único ejecutable son dos scripts
Python opcionales (linter + coldtest), un workflow de CI y un git hook.

La distinción clave: este bundle (el que estás leyendo) documenta **el kit como
proyecto** — qué es OKF, su modelo mental, sus decisiones de diseño y su ciclo de vida.
El kit aplicado a sí mismo es un acto de dogfooding.

# Anatomía del kit
- **`GUIDE.md`** — el procedimiento que un agente sigue para bootstrapear OKF en un repo.
- **`OKF-SPEC.md`** — el formato (reglas normativas). Ver [el formato](../references/okf-format.md).
- **`reference/`** — perfiles, ejemplos, verificación, mantenimiento, casos especiales,
  install-per-tool, herramientas opcionales.
- **`templates/`** — entrypoint (`AGENTS.md`/`CLAUDE.md`), `knowledge/` (index, log,
  tipos de concepto), skills, scripts, CI, hook.
- **`VERSION` / `CHANGELOG.md`** — la revisión del kit. Ver
  [kit_version vs okf_version](../decisions/0003-kit-version-vs-okf-version.md).

# Las tres capas
El contexto de un proyecto se parte en capas; OKF (el bundle) es solo una. Ver
[el modelo de tres capas](three-layer-model.md) para el detalle de cada una y por qué el
bundle es el corazón.

# Cómo se entrega
El recorrido de bootstrap (perfil → estructura → siembra → índices → log → entrypoint →
mantenimiento → verificación) está en el [runbook de bootstrap](../runbooks/bootstrap-a-repo.md),
que resume `GUIDE.md`. El ciclo posterior al init está en
[el ciclo de vida](../concepts/lifecycle.md).
