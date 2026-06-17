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
Investigá: manifiestos (`package.json`/`pyproject.toml`/…) y stack, `README`/`/docs`,
contexto de IA ya presente (`AGENTS.md`/`CLAUDE.md`/`.cursorrules`), `git log --oneline -30`,
y cualquier memoria de la herramienta. **Lo que no puedas deducir de la fuente —el
*por qué*, una convención no escrita, el grano de una tabla— preguntáselo al usuario.
No lo inventes.** Si ya existe un `knowledge/`, no lo pises: actualizalo (ver el
skill `okf-update`). Si el repo ya tiene **contexto disperso abundante** (un
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
(una frase) + `timestamp` + `tags`; `resource` si apunta a un activo real. Priorizá
el *por qué* que la fuente no dice; no copies lo que se deduce del código —linkealo.
**Cross-links relativos al archivo** (`../dir/x.md`), nunca con `/`. Usá los
`templates/knowledge/_*.md` como base: copialos a archivos **sin** el `_` y **borrá
el comentario HTML** (el archivo debe empezar con `---`).

## 4. Índices, log y sello de versión
`index.md` en la raíz (subdirectorios bajo `# Subdirectories`) y en cada hoja
(conceptos agrupados por `# {type}`), links relativos. `log.md` con una entrada de
hoy (`## YYYY-MM-DD`). Reemplazá el placeholder `{{KIT_VERSION}}` (en el `index.md`
raíz y en la línea de `Initialization` del `log.md`) con el contenido de
`VERSION` — la fuente única de la versión; si no está accesible, usá la
versión que conozcas. El `index.md` raíz lleva además `okf_version: "0.1"`.

## 5. Entrypoint
Si un agente de código va a trabajar el repo: copiá `templates/AGENTS.md` a la raíz
(+ `CLAUDE.md` shim). Si es wiki/datos navegado a mano: omití `AGENTS.md` y poné un
puntero a `knowledge/` en el `README`.

## 6. Instalá mantenimiento, testeo y CI
- `templates/skills/okf-update/` y `templates/skills/okf-verify/` → `.claude/skills/`.
- `templates/scripts/okf_lint.py` y `templates/scripts/okf_coldtest.py` → `scripts/`.
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
