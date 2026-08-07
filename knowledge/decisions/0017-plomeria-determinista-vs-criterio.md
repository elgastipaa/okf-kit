---
type: Decision
title: La plomería del init la ejecuta un script; el criterio se queda en el agente
description: "Todo lo mecánico del init/upgrade vive en okf_install.py como fuente única, y el skill delega en vez de re-statearlo; sembrar conceptos y mergear el contrato siguen siendo del agente."
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*delega la plomería al instalador"
tags: [instalacion, tooling, anti-drift]
timestamp: 2026-07-29T00:00:00Z
resource: ../../scripts/okf_install.py
---

# Contexto

> **Actualizada por la [0024](0024-el-contrato-se-actualiza-por-secciones.md)** (2026-08-03):
> el merge del `AGENTS.md`, que acá figura como criterio del agente, pasó a ser plomería —
> se separaron las secciones por dueño y el instalador ya puede hacerlo solo. El corte que
> define esta decisión no cambia; se movió un ejemplo de un lado al otro.

El kit resolvía bien el problema difícil (qué contexto capturar y por qué) y mal el fácil
(copiar archivos). `okf-init` le pedía a una IA ~40 operaciones de archivo y **una sola de
ellas requiere inteligencia**: sembrar los conceptos. El resto eran `mkdir`, `cp`, `chmod`,
sellar `{{KIT_VERSION}}` y borrar los bloques entre marcadores.

Peor: las trampas de esa plomería estaban **explicadas en prosa** porque no había código que
las garantizara — copiar los `_concept.md` sin el `_` y sin su comentario HTML, borrar las 8
líneas de marcadores siempre y lo de entre medio solo en la instalación mínima, renombrar los
tres `SKILL.md` (se llaman igual y se pisan), dejarlos fuera de `knowledge/` o el linter los
rechaza, `chmod +x` en el hook. Cada línea de esa prosa se pagaba en tokens en cada init y se
podía ejecutar mal. Y todos los asserts del gate medían el **template**, nunca la salida real.

# Decisión

**El corte es mecánico vs criterio, y cae entre los pasos 2 y 3 de `okf-init`.**

- Lo **mecánico** vive en `scripts/okf_install.py` (stdlib, kit-only) como **fuente única del
  procedimiento**: esqueleto del bundle sellado, contrato recortado según el nivel, skills con
  su renombre, scripts, CI, hook con su `chmod`, y `--upgrade` para reemplazar la maquinaria.
- Lo que requiere **criterio** se queda en el agente: entender el repo, elegir perfil y nivel,
  **sembrar los conceptos**, completar los `{{placeholders}}`, y mergear el `AGENTS.md` al
  actualizar (es el único archivo con contenido del proyecto mezclado con el del kit).
- **`okf-init` y `reference/upgrading.md` DELEGAN**: nombran el comando y describen lo que
  falta, sin re-statear los pasos mecánicos. Un assert del gate lo verifica.
- **El instalador verifica su propia salida** con el linter en `--strict`, y el gate
  **instala de verdad** en un repo temporal para chequear el resultado, no el template.

No viola la [0004](0004-vendor-neutral-no-external-apps.md): es stdlib, sin `pip`, no es
obligatorio, y el camino manual del `GUIDE` §4 sigue existiendo para máquinas sin Python.

# Consecuencias

- **El riesgo real de esta decisión es la doble fuente** (prosa del skill + código del script),
  que es la causa raíz de los bugs históricos del kit. Se mitiga con el assert de delegación:
  si `okf-init` vuelve a describir la plomería, el gate falla.
- `--upgrade` **es** el camino mecánico de la [0016](0016-material-instalado-vs-contenido.md):
  `reference/upgrading.md` se queda solo con sus pasos de criterio (leer el CHANGELOG, detectar
  el nivel, mergear el contrato).
- Verificar la **salida** destapó dos bugs latentes que la verificación del template no podía
  ver: el `description` del `_roadmap.md` con `:` sin comillas (ERROR de YAML en un roadmap
  recién sembrado) y su ejemplo de "Ahora" linkeando un `_changes/` inexistente.
- El instalador **no crea carpetas vacías**: una carpeta con solo un `index.md` es un lugar que
  nadie llenó, y la [0014](0014-future-layer-measured.md) ya midió que un documento vacío
  cuesta más que no tenerlo. Las reporta para que el agente las cree al sembrar.
