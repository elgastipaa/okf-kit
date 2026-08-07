---
type: Decision
status: accepted
origen: dictado
verify: test -d knowledge/decisions -a -d knowledge/references -a -d knowledge/architecture
title: Este bundle usa un perfil Mixto para documentar el propio kit
description: El kit se documenta a sí mismo combinando carpetas de Código y Wiki (perfil Mixto).
tags: [okf, dogfood, profiles, meta]
timestamp: 2026-06-17T00:00:00Z
---

# Contexto
Al aplicar OKF al **propio kit** (dogfooding) hay que elegir un perfil, y el kit no encaja
limpio en ninguno: es **metodología** (la prosa *es* el producto → suena a Wiki) pero
también **ships tooling** (linter, coldtest, CI, git hook → suena a Código) y tiene
**decisiones de diseño** reales que conviene capturar como ADRs.

# Decisión
Se usa el perfil **Mixto** (ver [perfiles](../concepts/profiles.md)), combinando carpetas
de Código y de Wiki:
- `architecture/` — el modelo mental (anatomía del kit, tres capas).
- `concepts/` — los conceptos centrales de OKF (bundle, progressive disclosure, perfiles,
  ciclo de vida).
- `decisions/` — las decisiones de diseño del kit (este archivo incluido), numeradas.
- `runbooks/` — procedimientos operativos del kit (lint, cold test, bootstrap).
- `references/` — el formato y aceleradores externos.

# Consecuencias
- Es un ejemplo vivo de la regla "combiná o inventá carpetas" de los perfiles: no hay que
  forzar el proyecto dentro de un perfil puro.
- Los `type` salen del núcleo universal (`Concept`, `Decision`, `Reference`, `Runbook`) más
  `Architecture` del perfil Código. Todos toleran ser desconocidos por
  [consumo permisivo](0002-permissive-consumption.md).
