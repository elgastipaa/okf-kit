---
type: Reference
title: Repomix — acelerador externo opcional
description: Empaqueta un repo en un archivo para entender el codebase y mide tokens del bundle; nunca requerido.
resource: https://github.com/yamadashy/repomix
tags: [repomix, optional, tooling]
timestamp: 2026-06-17T00:00:00Z
---

[Repomix](https://github.com/yamadashy/repomix) es un acelerador **opcional** (Node, vía
`npx repomix@latest`) que OKF **nunca requiere** — el kit funciona 100% sin él. Dos usos:

1. **Entender el repo al bootstrapear/migrar**: empaqueta el codebase en un único archivo
   AI-friendly comprimido (`--compress`, ~70% menos tokens) para leer en vez de caminar
   archivos a mano. Gasto único al estructurar; después el contexto se mantiene incremental.
2. **Token-sizer del bundle**: el linter valida estructura, no tamaño. Repomix imprime
   tokens totales y los archivos más pesados, para detectar un `index.md`/concepto demasiado
   grande (smell de Nivel 2) y decidir cuándo partir.

Punto clave: **no consume tokens de LLM** — es un tokenizador local (Tiktoken). El costo en
tokens es solo el agente al *leer* su output. Encaja con la regla de
[no apps externas requeridas](../decisions/0004-vendor-neutral-no-external-apps.md): es un
acelerador, no una dependencia.

# Citations
[1] [Repomix](https://github.com/yamadashy/repomix)
[2] [optional-tools.md (en este kit)](../../reference/optional-tools.md)
