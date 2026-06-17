---
type: Decision
status: accepted
title: Consumo permisivo — solo `type` es requisito duro
description: Al leer, faltantes/type desconocidos/links rotos NO invalidan el bundle; solo type es obligatorio.
resource: ../../OKF-SPEC.md
tags: [okf, conformance, robustness]
timestamp: 2026-06-17T00:00:00Z
---

# Contexto
Un bundle OKF crece, se refactoriza y se genera **parcialmente con agentes**. Si cualquier
campo faltante o link roto lo invalidara, sería inusable en la práctica: un link a un
concepto todavía no escrito representa conocimiento pendiente, no un error.

# Decisión
**Al escribir, sé prolijo; al leer, sé tolerante.** El único requisito **duro** de
conformidad (OKF v0.1) es que todo concepto tenga un `type` no vacío y un frontmatter
parseable. Todo lo demás es guía blanda: campos opcionales faltantes, `type` desconocidos,
claves extra y links rotos **NO** invalidan el bundle. Los consumidores DEBEN tolerar
`type` que no conocen.

Esto se refleja en el linter: solo emite **ERROR** (exit 1) por frontmatter ausente/roto,
`type` faltante, YAML inválido, o link absoluto `/`. El resto (faltan `title`/`description`/
`timestamp`, índices desfasados, links rotos, descripción de varias frases) son **WARN** y
no rompen el build. Por eso CI corre **sin `--strict`**.

# Consecuencias
- Un bundle a medio escribir sigue siendo válido y útil — clave para el crecimiento
  incremental (ver [el ciclo de vida](../concepts/lifecycle.md)).
- Al *autorar* igual se completa el set por defecto (`type` + `title` + `description` +
  `timestamp` + `tags`) porque es lo que hace funcionar bien los `index.md` y el
  [progressive disclosure](../concepts/progressive-disclosure.md).
- No uses `--strict` en CI: convertiría WARNs legítimos (un link a algo aún no escrito) en
  fallos.
