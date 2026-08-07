---
type: Decision
title: El plugin shippea solo el par de bootstrap, y no copia skills
description: "El plugin de Claude Code apunta a templates/skills/ con rutas custom y solo distribuye okf-init y okf-migrate; los procedimientos de mantenimiento se copian al repo destino."
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*plugin.json no ship"
tags: [distribucion, plugin, anti-drift]
timestamp: 2026-07-29T00:00:00Z
resource: ../../.claude-plugin/plugin.json
---

# Contexto

Instalar el kit era "cloná el repo y apuntá un agente al `GUIDE`", cuando el resto del
ecosistema instala con un comando. Claude Code distribuye plugins con skills, agentes y hooks
adentro — y el kit ya tenía exactamente esa forma (`templates/skills/`, `templates/hooks/`,
`templates/ci/`). Faltaban los manifiestos.

Dos trampas: un plugin que **copie** los skills crearía dos copias (la deriva que el kit
existe para evitar), y un plugin que **shippee todos** los procedimientos volvería el entorno
del usuario una dependencia oculta del repo.

# Decisión

**El plugin es el propio repo del kit** (`"source": "./"`) y su `plugin.json` apunta a
`./templates/skills/…` con rutas custom. **No copia nada**: una sola verdad en disco.

**Shippea solo `okf-init` y `okf-migrate`** — el par de **bootstrap**, que por definición corre
con el kit en disco. Los procedimientos de mantenimiento (`okf-update`, `okf-verify`,
`okf-plan`) se siguen **copiando al repo destino**.

La versión vive en `VERSION` (fuente única) y el `plugin.json` es su única segunda copia, con
un assert del gate que las compara. El `marketplace.json` **no** declara versión a propósito:
hosteado en git, cada commit cuenta como revisión nueva, y una tercera copia derivaría.

# Consecuencias

- **La [0013](0013-installed-material-is-self-sufficient.md) se mantiene**: quien clone un repo
  que recibió OKF, sin el plugin instalado, sigue teniendo sus procedimientos. Si vinieran del
  plugin, el repo dejaría de ser autosuficiente. Un assert del gate verifica que el
  `plugin.json` no los liste.
- El `CLAUDE.md` de la raíz hace que `claude plugin validate --strict` avise que no se carga
  como contexto del plugin. Es correcto y **esperado**: ese archivo existe porque el kit se
  auto-aplica OKF (es su shim de entrypoint), así que el plugin se valida sin `--strict`.
- El bootstrap deja de depender de que el usuario copie el skill a `~/.claude/skills/` a mano.
