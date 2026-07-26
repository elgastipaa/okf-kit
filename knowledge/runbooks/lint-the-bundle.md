---
type: Runbook
title: Validar conformidad de un bundle con el linter
description: Corré okf_lint.py para el chequeo determinista de Nivel 1 (PASS/FAIL).
resource: ../../templates/scripts/okf_lint.py
tags: [ops, verification, linter]
timestamp: 2026-07-26T00:00:00Z
---

# Cuándo
Antes de cerrar cualquier cambio al bundle, en el pre-commit hook, y en CI. Es el
**Nivel 1** (conformidad, objetivo) de la verificación.

# Pasos
1. Corré el linter apuntando a la carpeta del bundle:
   ```bash
   python3 templates/scripts/okf_lint.py knowledge
   ```
   Exit `0` = conforme (warnings permitidos). Exit `1` = hay errores. Exit `2` = error de uso
   (directorio inexistente o sin `.md`).
2. Para tratar warnings como errores (úsalo con cuidado, **no** en CI):
   ```bash
   python3 templates/scripts/okf_lint.py --strict knowledge
   ```

# Notas / gotchas
- **Solo stdlib, sin `pip install` — y sin PyYAML.** El frontmatter lo valida un parser
  determinista propio, así que el veredicto es el mismo en cualquier máquina (nada de
  chequeos que aparecen o desaparecen según lo que haya instalado).
- Hace fallar (ERROR) solo por: frontmatter ausente/roto/no-mapping, `type` faltante, YAML
  inválido, o link que **empieza con `/`**. Todo lo demás es WARN. Es la materialización de
  [consumo permisivo](../decisions/0002-permissive-consumption.md).
- **No uses `--strict` en CI:** un link a un concepto aún no escrito es WARN legítimo y no
  debe romper el build.
- Ignora los archivos `_*.md` (plantillas) por el prefijo `_`.
- Si no hay Python, el skill `okf-verify` corre estos mismos chequeos leyendo los archivos.
