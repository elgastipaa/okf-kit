---
type: Decision
status: accepted
title: Sin apps externas; vendor-neutral; solo stdlib en el tooling
description: OKF es markdown + git; el único extra es un linter Python stdlib-only, sin pip ni apps.
resource: ../../README.md
tags: [okf, vendor-neutral, no-dependencies]
timestamp: 2026-06-17T00:00:00Z
---

# Contexto
El objetivo de OKF es que **cualquier IA, en cualquier momento, desde cualquier máquina**
entienda un proyecto. Atar el sistema a Obsidian, Notion, un visor de grafos, un SDK o un
vendor de IA rompería ese objetivo: el contexto dejaría de ser portable.

# Decisión
El núcleo es **markdown + git**, nada más. Concretamente:
- **Cero apps externas** para *usar* el bundle: se lee con `cat`, en GitHub, o como
  archivos por un agente.
- **Vendor-neutral**: `AGENTS.md` es el contrato cross-tool; los skills son una
  *conveniencia* de Claude Code cuyo contenido es markdown que cualquier agente sigue. La
  conexión por herramienta (Cursor/Copilot/Gemini…) son **punteros** a `AGENTS.md`, nunca
  copias. Ver [el modelo de tres capas](../architecture/three-layer-model.md).
- **Tooling solo stdlib**: el linter (`okf_lint.py`) y el coldtest no requieren
  `pip install`. Si la máquina no tiene Python, el skill `okf-verify` hace los mismos
  chequeos leyendo archivos. Aceleradores como Repomix son **opcionales**, nunca requeridos
  (ver [Repomix](../references/repomix.md)).

# Consecuencias
- No se debe introducir ninguna dependencia que haya que instalar para *usar* el bundle, ni
  ningún paso que ate a un vendor.
- El enforcement portable (git hook + CI) corre con cualquier herramienta porque es a nivel
  git/server, no de la IA.
- Esto es lo que sostiene la promesa "el contexto te sigue con `git clone`".
