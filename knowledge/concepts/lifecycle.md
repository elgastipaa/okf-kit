---
type: Concept
title: El ciclo de vida del contexto (init y mantenimiento)
description: El bundle se monta una vez (init) y se mantiene vivo incremental para no pudrirse.
resource: ../../reference/maintaining.md
tags: [okf, lifecycle, maintenance]
timestamp: 2026-07-26T00:00:00Z
---

El kit cubre dos fases. **`GUIDE.md` = el init** (montar el bundle por primera vez).
**`reference/maintaining.md` = lo que viene después** (mantenerlo fresco). El bundle solo
vale si se mantiene vivo: una pieza de conocimiento por vez, como efecto colateral del
trabajo normal, no como un proyecto aparte.

# Cuándo actualizar el bundle
- Se toma/descubre una **decisión** no trivial → `decisions/NNNN-*.md`.
- Cambia la **arquitectura / schema** → editá el concepto + una línea en `log.md`.
- Aparece un **gotcha** (framework, API, setup) → `references/*.md`.
- Cambia un **procedimiento operativo** → `runbooks/*.md`.
- Te explican algo que el código no dice y vas a re-necesitar → la carpeta que toque.
- Se abre o se cierra un **cambio** planificado → `_changes/` + harvest al bundle
  (capa de futuro — ver la [decisión 0011](../decisions/0011-future-work-layer.md)).

# Las capas de enforcement (de blanda a dura)
El mantenimiento no depende de la buena voluntad; hay varias redes y ninguna es
obligatoria, pero juntas hacen difícil que el contexto se pudra:

1. **El contrato en `AGENTS.md`** — lo lee toda IA al arrancar (blando).
2. **`okf-update`** — skill de Claude *o* procedimiento que cualquier agente sigue.
3. **Pre-commit hook** — universal, a nivel git: bloquea commits no conformes.
4. **CI** (`okf.yml`) — corre el linter en cada push.
5. **`okf-verify` + cold test** — auditoría: ¿un agente en frío sigue entendiendo el
   proyecto solo con el bundle? Ver [el runbook de cold test](../runbooks/cold-test.md).

Estas capas son el verdadero diferencial frente a "escribir docs y olvidarlas". Cada
pregunta que el cold test falla = un concepto faltante.
