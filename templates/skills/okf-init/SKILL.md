---
name: okf-init
description: >
  Monta el sistema de contexto OKF en un repo desde cero (bootstrap): crea el
  bundle knowledge/ (markdown + frontmatter), el entrypoint AGENTS.md, e instala
  los skills/linter de mantenimiento y testeo. Usalo cuando el usuario pide
  "armá/inicializá/bootstrapeá este repo con OKF" o "creá el contexto OKF acá".
---

Montás un sistema de contexto OKF (Open Knowledge Format): conocimiento del
proyecto como carpeta `knowledge/` de markdown + frontmatter YAML, versionada en
git, legible por cualquier IA. Este skill es la versión ejecutable de la guía
completa.

**Si `okf-kit` está accesible, leé `GUIDE.md` y seguilo** (es la
fuente autoritativa, con `reference/profiles.md`, `reference/examples.md`,
`reference/special-cases.md`, `reference/verification.md` y los `templates/`). Si
no está accesible, seguí el procedimiento embebido de abajo.

**Sin instalaciones ni apps externas.** Markdown + git. Los únicos extras son scripts
Python opcionales (linter + coldtest, stdlib, sin `pip install`) y aceleradores externos
opcionales (Repomix) — ver `reference/optional-tools.md`. Nada obligatorio.

# Procedimiento

## 0. Antes de tocar nada — entendé el repo
**El destino es el repo del usuario, NO `okf-kit`.** Si llegaste acá por "cloná okf-kit y
aplicalo a mi repo X", todo lo que generes va en **repo X**; nunca escribas dentro de
`okf-kit` (tiene su propio `knowledge/` dogfood). Confirmá cuál es el destino y su ruta; si
dudás, preguntale al usuario.

Investigá: manifiestos (`package.json`/`pyproject.toml`/…) y stack, `README`/`/docs`,
contexto de IA ya presente (`AGENTS.md`/`CLAUDE.md`/`.cursorrules`), `git log --oneline -30`,
y cualquier memoria de la herramienta. **Lo que no puedas deducir de la fuente —el
*por qué*, una convención no escrita, el grano de una tabla— preguntáselo al usuario.
No lo inventes.** **Si ya existe un `knowledge/`, no lo pises.** Mirá el `kit_version` de su
`index.md`: si es anterior al `VERSION` del kit, el repo tiene el bundle al día pero el
**material instalado viejo** (contrato, skills, scripts) — seguí `reference/upgrading.md`, no
`okf-update` (ese mantiene el *contenido* y no puede tocar la maquinaria del kit). Si coincide,
el repo ya está al día y lo que haga falta es mantenimiento normal (`okf-update`). Si el repo ya tiene **contexto disperso abundante** (un
`AGENTS.md`/`CLAUDE.md` rico, `/docs`, ADRs), usá el skill `okf-migrate` en vez de
sembrar de cero. Para repos grandes, empaquetalos primero con Repomix y leé ese único
archivo en vez de caminar todo (opcional — ver `reference/optional-tools.md`, uso 1).

## 1. Elegí el perfil
Decidí el dominio → define carpetas y `type` (detalle en `reference/profiles.md`):
- **Código** — `architecture/ decisions/ domain/ schema/ runbooks/ references/`
- **Datos** — `datasets/ tables/ references/{metrics,joins}/ glossary/`
- **Wiki** — organizado por tema + `playbooks/ glossary`
- **Mixto** — combiná o inventá carpetas/tipos. Para monorepos/migración, ver
  `reference/special-cases.md`.

## 2. Creá la estructura
`knowledge/` con `index.md`, `log.md` y solo las carpetas del perfil que vayas a
llenar. No crees carpetas vacías.

## 3. Sembrá los conceptos (lo más importante)
Un archivo por concepto, con frontmatter `type`(req) + `title` + `description`
(una frase) + `timestamp`; `tags` y `resource` si aplican. Priorizá
el *por qué* que la fuente no dice; no copies lo que se deduce del código —linkealo.
**Cross-links relativos al archivo** (`../dir/x.md`), nunca con `/`. Usá los
`templates/knowledge/_*.md` como base: copialos a archivos **sin** el `_` y **borrá
el comentario HTML** (el archivo debe empezar con `---`).

**Capa de futuro (default; es lo que decide si la instalación es "completa" o "mínima"):**
preguntale al usuario **en su idioma, no en el del kit** — *"¿querés que además lleve el
rumbo del proyecto —qué estás haciendo, qué sigue— para retomar sin explicarme todo de nuevo?
Suma un poco de ida y vuelta antes de codear."* Sí (o duda) → completa; "andá directo al
código" → mínima (saltá esta capa y seguí las instrucciones de borrado en §5 y §6).

Si va: sembrá `knowledge/roadmap.md` (template `_roadmap.md`) **preguntándole** la visión, lo
próximo y los no-goals — no se deducen de ninguna fuente. **Si no contesta o dice "hacelo
vos": escribí lo que sí puedas inferir del código/README y marcá cada hueco con un
blockquote `> Pendiente de confirmar: …`. No omitas el archivo** — el contrato instalado lo
linkea. El trabajo en curso va como docs en `knowledge/_changes/` (template `_change.md`; el
linter la ignora). Ciclo completo: skill `okf-plan`.

## 4. Índices, log y sello de versión
`index.md` en la raíz (subdirectorios bajo `# Subdirectories`, y los conceptos que vivan en
la raíz —`roadmap.md`, `glossary.md`— antes, agrupados por `# {type}`) y en cada hoja
(conceptos agrupados por `# {type}`), links relativos. `log.md` con una entrada de
hoy (`## YYYY-MM-DD`). Reemplazá el placeholder `{{KIT_VERSION}}` (en el `index.md`
raíz y en la línea de `Initialization` del `log.md`) con el contenido de
`VERSION` — la fuente única de la versión; si no está accesible, usá la
versión que conozcas. El `index.md` raíz lleva además `okf_version: "0.1"`.

## 5. Entrypoint
Si un agente de código va a trabajar el repo: copiá `templates/AGENTS.md` a la raíz
(+ `CLAUDE.md` shim). Si es wiki/datos navegado a mano: omití `AGENTS.md` y poné un
puntero a `knowledge/` en el `README`.

**Borrá el andamiaje, mecánicamente** (si no, el contrato manda al agente a archivos que no
existen): siempre, las 8 líneas de marcadores `<!-- OKF:future-layer:… -->`; y **si no
instalaste la capa de futuro** (§3), además todo lo que quede **entre** cada par de
marcadores `:start`/`:end` (4 bloques) y el bloque `# Roadmap` del `knowledge/index.md`.

## 6. Instalá mantenimiento, testeo y CI
- `templates/skills/okf-update/` y `templates/skills/okf-verify/` → `.claude/skills/`; sumá
  `templates/skills/okf-plan/` **solo si instalaste la capa de futuro** (§3). Si no se usa
  Claude Code, copiá cada `SKILL.md` a `docs/okf/okf-<nombre>.md` — **renombrando** (los tres
  se llaman igual y si no se pisan entre sí) y **fuera de `knowledge/`**, o el linter los
  rechaza (traen frontmatter sin `type`).
- `templates/scripts/okf_lint.py`, `okf_coldtest.py` y `okf_stale.py` → `scripts/`.
- `templates/ci/okf.yml` → `.github/workflows/okf.yml` (linter en cada push, cero tokens).
- `templates/hooks/pre-commit` → git hook **universal** (corre con cualquier IA): `cp` a
  `.git/hooks/pre-commit` + `chmod +x`, o `git config core.hooksPath`. Bloquea si el bundle
  no es conforme y avisa si cambió código sin tocar `knowledge/`.
- **Para herramientas que no sean Claude Code** (Cursor/Copilot/Gemini…), seguí
  `reference/install-per-tool.md` para apuntarlas al contrato `AGENTS.md`.

## 7. Verificá
Corré `python3 scripts/okf_lint.py knowledge` (o el skill `okf-verify`). Mostrale al
usuario el árbol final, el perfil elegido, qué sembraste, y **qué te faltó por no
tener la info**. Ver `reference/verification.md`.
