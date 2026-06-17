---
type: Decision
status: accepted
title: El bundle en git es la fuente de verdad, no la memoria de la herramienta
description: La memoria privada de la IA es un atajo personal; la verdad vive en knowledge/ versionado.
resource: ../../README.md
tags: [okf, source-of-truth, portability]
timestamp: 2026-06-17T00:00:00Z
---

# Contexto
Herramientas como Claude Code tienen una **memoria privada** (`~/.claude/.../MEMORY.md`).
Es cómoda, pero **no es portable ni vive en el repo**: otro agente, otra máquina u otra IA
no la ven. Apoyarse en ella para el conocimiento del proyecto reintroduce el problema que
OKF resuelve — el contexto atrapado fuera del repo.

# Decisión
La **fuente de verdad es el bundle OKF en git** (`knowledge/`). La memoria de la
herramienta queda como **atajo personal** con, a lo sumo, un puntero ("el contexto vive en
`knowledge/`"). Durante el bootstrap, el conocimiento tribal que esté en una memoria de
herramienta se **migra** al bundle para hacerlo portable, no se deja ahí.

# Consecuencias
- Cuando un agente aprende algo que "ya debería estar", lo escribe en `knowledge/`, no solo
  en el chat ni en la memoria privada. Es la regla #2 del contrato de `AGENTS.md`.
- El bundle es la cuarta capa "trampa" del [modelo de tres capas](../architecture/three-layer-model.md):
  útil pero no autoritativa.
- Beneficio: versionado, diffeable, con `log.md` de historial, y sobrevive a cambiar de
  herramienta o de máquina.
