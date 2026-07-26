---
type: Runbook
title: Bootstrapear OKF en un repo (resumen del GUIDE)
description: La secuencia de init — perfil, estructura, siembra, índices, log, entrypoint, verificación.
resource: ../../GUIDE.md
tags: [ops, bootstrap, init]
timestamp: 2026-06-17T00:00:00Z
---

# Cuándo
Una sola vez por repo, para montar el contexto OKF desde cero. El procedimiento
autoritativo y completo es `GUIDE.md`; esto es el mapa. La versión skill es `okf-init`.

# Pasos
1. **Entendé el repo** (`GUIDE.md` §3): manifiestos/stack, docs existentes, contexto de IA
   ya presente, `git log`, memoria de la herramienta. Lo que no se deduce de la fuente
   —el *por qué*— **preguntáselo al usuario**, no lo inventes.
2. **Elegí el perfil** (Código / Datos / Wiki / Mixto) → define carpetas y `type`. Ver
   [perfiles](../concepts/profiles.md).
3. **Creá la estructura** `knowledge/` mínima: solo las carpetas que vas a llenar. No crees
   carpetas vacías.
4. **Sembrá los conceptos** (lo más importante): un archivo por concepto, capturando el
   *por qué* que la fuente no dice; lo deducible se **linkea**, no se copia. Partí de los
   templates `templates/knowledge/_*.md` (copialos sin el `_` y borrá el comentario HTML).
5. **Índices + log + versión:** `index.md` raíz (subdirectorios, y los conceptos que vivan en
   la raíz —`roadmap.md`, `glossary.md`— agrupados por `type`) y por hoja (conceptos
   agrupados por `type`); `log.md` con la fecha de hoy. Estampá `kit_version` desde
   `VERSION` y `okf_version: "0.1"` en el `index.md` raíz. Ver
   [kit_version vs okf_version](../decisions/0003-kit-version-vs-okf-version.md).
6. **Entrypoint:** `AGENTS.md` (+ `CLAUDE.md` shim) si lo trabaja un agente de código; o un
   puntero a `knowledge/` en el `README` si es wiki/datos. Recortá el template con sus
   marcadores según el nivel instalado — ver
   [material instalado autosuficiente](../decisions/0013-installed-material-is-self-sufficient.md).
7. **Mantenimiento + CI** (opcional): skills, scripts, `okf.yml`, git hook.
8. **Verificá:** corré [el linter](lint-the-bundle.md) y, periódicamente, el
   [cold test](cold-test.md).

# Notas / gotchas
- **Cross-links relativos al archivo**, nunca con `/` (rompe en GitHub). Ver
  [la decisión de links](../decisions/0001-relative-links-over-absolute.md).
- Los `templates/knowledge/` son **plantillas**, no el bundle: el bundle real se construye
  en `knowledge/` del repo destino.
