---
type: Decision
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*link absoluto\|PASS.*linter pasa limpio"
title: Los cross-links son relativos al archivo, no absolutos al bundle
description: Se usan links relativos (../x.md) porque los absolutos (/x.md) rompen en GitHub.
resource: ../../OKF-SPEC.md
tags: [okf, links, github, gotcha]
timestamp: 2026-06-17T00:00:00Z
---

# Contexto
La spec OKF define dos formas de cross-link: **relativa al archivo** (`../dir/x.md`) y
**absoluta al bundle** (`/dir/x.md`, desde la raíz del bundle). La spec *original* de
Google "recomienda" la forma absoluta. Pero los absolutos solo funcionan si un consumidor
reescribe los links; **GitHub interpreta `/` como la raíz del repo, no del bundle**, así
que rompen en el visor más común y en cualquier preview de markdown plano.

# Decisión
Este kit usa **siempre links relativos al archivo** como default, incluso contra la
recomendación nominal de la spec original — porque es lo que hace la propia
implementación de referencia de OKF (su generador de índices emite relativos), y es lo
que de verdad funciona sin tooling. El linter trata un link que **empieza con `/`** como
**ERROR** (no warning): es el único chequeo de links que hace fallar el build.

# Consecuencias
- Todo cross-link y toda entrada de `index.md` debe ser relativa: `./y.md`, `../dir/z.md`.
  Nunca empezar con `/`.
- Los links sobreviven a clones y se renderizan vivos en GitHub sin herramientas, alineado
  con el principio "sin apps externas" (ver
  [vendor-neutralidad](0004-vendor-neutral-no-external-apps.md)).
- Costo: mover un archivo rompe los links relativos que lo apuntan. Se acepta porque el
  linter los detecta (como WARN) y porque el progressive disclosure mantiene los movimientos
  acotados. Ver [el formato](../references/okf-format.md) §4.
