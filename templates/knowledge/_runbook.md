<!--
  TEMPLATE de runbook. Va en runbooks/. Procedimiento operativo repetible: build,
  test, deploy, tareas de DB, levantar local. El COMO. Borrá este comentario.
-->
---
type: Runbook
title: {{Qué hace este procedimiento. Ej: "Correr el smoke test"}}
description: {{Una frase: qué logra y cuándo se corre.}}
resource: {{URI/path del script, ej: scripts/smoke.ts — opcional. Es el activo, NO un cross-link OKF}}
tags: [{{ops}}, {{subsistema}}]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Cuándo
{{En qué situación se corre esto.}}

# Pasos
1. {{Comando o acción concreta.}}
   ```bash
   {{comando exacto}}
   ```
2. {{...}}

# Notas / gotchas
{{Cosas que salen mal, prerequisitos no obvios, dónde corre (local vs cloud), etc.
Linkeá a la decisión que explica el porqué si aplica.}}
