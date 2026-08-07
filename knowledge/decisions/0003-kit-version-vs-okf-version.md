---
type: Decision
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*estampa kit_version == VERSION"
title: kit_version y okf_version son dos versiones distintas
description: okf_version versiona el formato; kit_version versiona esta guía+templates+tooling.
resource: ../../CHANGELOG.md
tags: [okf, versioning, kit]
timestamp: 2026-06-17T00:00:00Z
---

# Contexto
Hay dos cosas versionables que es fácil confundir: el **formato** OKF (las reglas de
`OKF-SPEC.md`) y **este kit** (la guía + templates + scripts). Mezclarlas haría imposible
saber con qué revisión del kit nació un repo, ni a qué versión del formato apunta su bundle.

# Decisión
Se mantienen **dos** identificadores separados:
- **`okf_version`** (p.ej. `"0.1"`) — la versión del **formato**, fijada por `OKF-SPEC.md`.
  Se declara en el frontmatter del `index.md` **raíz** del bundle (único `index.md` que
  lleva frontmatter).
- **`kit_version`** (p.ej. `0.3.0`) — la revisión de **este kit**, cuya fuente de verdad es
  el archivo `VERSION`. `okf-init` la estampa en el `index.md` raíz y en la línea
  `Initialization` de `log.md`, para que el repo sepa de qué revisión del kit nació.

# Consecuencias
- Al sembrar el `index.md` raíz hay que poner **ambos**: `okf_version: "0.1"` + el
  `kit_version` leído de `VERSION`.
- El placeholder `{{KIT_VERSION}}` de los templates se reemplaza con el contenido de
  `VERSION`, no con un número inventado.
- El `CHANGELOG.md` versiona el kit, no el formato. Ver
  [el runbook de bootstrap](../runbooks/bootstrap-a-repo.md) para dónde se estampa.
