---
name: okf-init
description: >
  Monta el sistema de contexto OKF en un repo desde cero (bootstrap): crea el
  bundle knowledge/ (markdown + frontmatter), el entrypoint AGENTS.md, e instala
  los skills/linter de mantenimiento y testeo. Usalo cuando el usuario pide
  "armá/inicializá/bootstrapeá este repo con OKF" o "creá el contexto OKF acá",
  y también cuando describe el SÍNTOMA sin nombrar OKF: "cada sesión le tengo
  que explicar el proyecto de nuevo", "la IA no entiende mi repo", "quiero
  documentar esto para que la IA lo entienda", "que no se pierda el contexto
  entre sesiones", "armá un AGENTS.md/CLAUDE.md en serio para este repo".
  Para un repo que YA tiene docs/ADRs/AGENTS.md propios, usá okf-migrate.
  ALSO IN ENGLISH — trigger on the symptom, not the acronym: "I have to explain
  my project to the AI every session", "the AI keeps forgetting my project",
  "Claude/Cursor doesn't understand my repo", "set up context/memory for this repo",
  "write a proper AGENTS.md / CLAUDE.md for this project", "document this codebase
  so the AI gets it", "stop losing context between sessions".
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

## 1. Elegí el perfil y el nivel (las dos decisiones que el instalador necesita)

**El perfil** = el dominio → define carpetas y `type` (detalle en `reference/profiles.md`):
- **Código** (`codigo`) — `architecture/ decisions/ domain/ schema/ runbooks/ references/`
- **Concepto** (`concepto`) — por tema + `decisions/ playbooks/ glossary/ references/`
- **Mixto** (`mixto`) — combiná o inventá; **un repo de datos va acá** (`datasets/ tables/
  references/metrics/ glossary/`). Para monorepos/migración, ver
  `reference/special-cases.md`.

**El nivel** = ¿va la **capa de futuro** (rumbo + cambios en curso)? Es el default, y decide si
la instalación es completa o `--minimal`. Preguntale al usuario **en su idioma, no en el del
kit** — *"¿querés que además lleve el rumbo del proyecto —qué estás haciendo, qué sigue— para
retomar sin explicarme todo de nuevo? Suma un poco de ida y vuelta antes de codear."*
Sí (o duda) → completa. "Andá directo al código" → `--minimal`.

## 2. Instalá el esqueleto y la maquinaria (un comando, cero criterio)

Todo lo mecánico —esqueleto del bundle con las fechas y el `kit_version` sellados, contrato
`AGENTS.md` recortado según el nivel de instalación, skills, `okf_lint.py` / `okf_coldtest.py`
/ `okf_stale.py`, CI y git hook— lo hace el instalador del kit. **No lo hagas a mano: es
plomería, se ejecuta mal y se paga en tokens.**

```
python3 <ruta-al-kit>/scripts/okf_install.py <repo-destino> --profile <perfil> --name "<Proyecto>"
```

- Instalado como **plugin** de Claude Code, la ruta del kit es `${CLAUDE_PLUGIN_ROOT}`.
- Flags: `--minimal` (sin capa de futuro, ver §3) · `--no-claude` (procedimientos a `docs/okf/`
  en vez de `.claude/skills/`) · `--no-ci` · `--no-hook` · `--dry-run` (mostrar sin escribir).
- **No pisa un `knowledge/` existente**: aborta y te rutea (§0).
- Al terminar corre el linter sobre lo instalado y **lista lo que falta**, que es exactamente
  lo que sigue acá abajo. Si el linter no pasa, es un bug del kit — reportalo.

**¿La máquina no tiene Python?** Entonces el procedimiento mecánico es el `GUIDE.md` §4 del
kit (pasos 1, 5, 6 y 7), a mano. Es la única razón para hacerlo a mano.

## 3. Sembrá los conceptos (lo más importante)
Un archivo por concepto, con frontmatter `type`(req) + `title` + `description`
(una frase) + `timestamp`; `tags` y `resource` si aplican. Priorizá
el *por qué* que la fuente no dice; no copies lo que se deduce del código —linkealo.
**Cross-links relativos al archivo** (`../dir/x.md`), nunca con `/`. Usá los
`templates/knowledge/_*.md` como base: copialos a archivos **sin** el `_` y **borrá
el comentario HTML** (el archivo debe empezar con `---`).

**Las carpetas del perfil todavía no existen** — el instalador no crea carpetas vacías. Creá
cada una, con su `index.md`, recién cuando tenga un concepto real adentro, y **sumala al
`# Subdirectories`** del `knowledge/index.md`. Cada `index.md` de hoja agrupa sus conceptos
bajo un heading por `type`: `* [Título](archivo.md) - <description>`.

**Si va la capa de futuro** (§1): el instalador ya dejó `knowledge/roadmap.md` con la
estructura, pero su contenido **es tuyo**: preguntale al usuario la visión, lo próximo y los
no-goals — no se deducen de ninguna fuente. **Si no contesta o dice "hacelo vos": escribí lo
que sí puedas inferir del código/README y marcá cada hueco con un blockquote
`> Pendiente de confirmar: …`. No lo dejes con los `{{placeholders}}` puestos** — un roadmap
que no dice nada cuesta más que no tenerlo. El trabajo en curso va como docs en
`knowledge/_changes/` (template `_change.md`; el linter la ignora). Ciclo completo: `okf-plan`.

## 4. Completá lo que el instalador dejó marcado

Su reporte final lista los archivos con `{{placeholders}}`. Los que importan:

- **`AGENTS.md`**: el nombre y el stack en una o dos frases, las **reglas duras** del proyecto
  (linkeando al concepto que explica cada una) y las **capas NO autoritativas** (dirs scratch,
  legacy, planes viejos que NO son estado; si el repo no tiene ninguna, borrá esa sección).
- **`knowledge/checks.md`**: los comandos que prueban que el código anda, sacados del
  `package.json`/`Makefile`/CI — **no los inventes**. Si el repo no tiene ninguno,
  escribí eso tal cual: "este repo no tiene chequeos automáticos" es información y hoy
  es invisible. Es el único concepto que contesta *"¿cómo sé que esto anda?"*.
- **`knowledge/index.md`**: la `description` del roadmap y una línea por carpeta sembrada.
- **`knowledge/log.md`**: qué conceptos sembraste en este primer pase.

Si es un repo de **wiki o datos** que se navega a mano y no lo va a trabajar un agente de
código: borrá el `AGENTS.md` y el `CLAUDE.md`, y poné un puntero a `knowledge/` en el `README`.
Para herramientas que no sean Claude Code (Cursor/Copilot/Gemini…), `reference/install-per-tool.md`.

## 5. Verificá
Corré `python3 scripts/okf_lint.py knowledge` (o el skill `okf-verify`). Mostrale al
usuario el árbol final, el perfil elegido, qué sembraste, y **qué te faltó por no
tener la info**. Ver `reference/verification.md`.
