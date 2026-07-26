---
name: okf-migrate
description: >
  Migra el contexto disperso de un repo que YA existe (AGENTS.md, CLAUDE.md,
  .cursorrules, /docs, ADRs, notas tribales del README) a un bundle OKF en
  knowledge/, sin duplicar. Usalo cuando el usuario pide "migrá/consolidá el
  contexto existente a OKF" o "pasá estas docs/ADRs a OKF".
---

Sos el camino **brownfield** de OKF: el repo ya tiene contexto, pero disperso. Tu
objetivo es **consolidarlo** en un bundle `knowledge/` versionado y navegable, **sin
agregar una capa más ni duplicar**. (Para un repo sin contexto previo, usá `okf-init`.)

**Si `okf-kit` está accesible**, leé `reference/special-cases.md`
(§"Migrar desde…") y `GUIDE.md`; usá los `templates/`. Si no, seguí esto.

# Procedimiento

## 1. Inventariá el contexto disperso
Buscá y listá todo lo que ya documenta el proyecto:
- `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`.
- `/docs`, wikis, READMEs largos, ADRs (`docs/adr/`, `decisions/`…).
- Comentarios "tribales" en el README o en el código (decisiones, gotchas).
- Planes y pendientes: `TODO.md`, `ROADMAP.md`, listas de "próximos pasos", features a medias.
Mostrale el inventario al usuario antes de mover nada. (Para repos grandes, empaquetá
con Repomix y leé ese archivo — opcional, ver `reference/optional-tools.md`.)

## 2. Triage de frescura — verificá contra el código (NO migres ni pointees basura)
**Antes** de clasificar por destino, clasificá cada pieza por **frescura**, chequeándola
contra el código (gana el código). Migrar NO es "mover todo": es separar lo vivo de lo legacy.

- **Vigente** (coincide con el código) → sigue al Paso 3 (se harvestea/migra/pointea).
- **Stale / contradice el código / legacy** → **NO se migra como verdad ni se pointea.** Se
  **declara no-autoritativa** en la sección "Capas NO autoritativas" de `AGENTS.md` (ver el
  template). Opcionalmente proponé actualizarla o borrarla.
- **Dudosa** (no podés determinar si está viva sin conocimiento de dominio) → **pará y
  preguntale al usuario.**

Mostrale al usuario tu triage y, para lo stale/dudoso, pedí la disposición — p. ej.: *"Encontré
N docs. Estos coinciden con el código (los migro); estos contradicen/parecen viejos (los marco
no-autoritativos); estos no puedo determinar — ¿los mantengo, actualizo o descarto?"*. **Nunca
pointees el bundle hacia un doc sin verificar que está vivo** — eso consagra el drift (la KB
terminaría ruteando a los agentes hacia la basura).

## 3. Clasificá lo VIGENTE por destino
- **Reglas duras / "siempre-nunca"** → se quedan en `AGENTS.md` (el índice).
- **Decisiones y su *por qué*** → `knowledge/decisions/NNNN-<slug>.md` (los ADRs
  existentes se mueven casi tal cual, renombrados y con frontmatter OKF).
- **Dominio / schema / procesos** → la carpeta del perfil que toque (ver `profiles.md`).
- **Procedimientos operativos** → `knowledge/runbooks/`.
- **Material externo** → `knowledge/references/` (resumido, con `# Citations`).
- **Planes / TODOs / roadmaps**: **preguntale al usuario si quiere la capa de futuro**
  (misma pregunta que en `okf-init` §3 — en su idioma, no en el del kit). Si va: la
  intención que sigue viva → `knowledge/roadmap.md` (visión, qué sigue, no-goals —
  confirmala con él) y, si hay trabajo a medio hacer, un doc por cambio en
  `knowledge/_changes/` (ver `okf-plan`). Si no va, es la instalación **mínima**: aplicá el
  borrado por marcadores del `AGENTS.md` que describe `okf-init` §5. Los planes muertos
  → no-autoritativos o borrar (preguntá la disposición, como con cualquier doc stale).

## 4. Mové, no copies
Por cada pieza: creá el concepto OKF en `knowledge/` (frontmatter `type`+`title`+
`description`+`timestamp`, `tags` si aplica; cross-links **relativos al archivo**, nunca `/`) y
**borrá el contenido del original**, dejando un puntero ("esto ahora vive en
`knowledge/<...>`"). En `AGENTS.md` dejá solo el índice + "el contexto vive en
`knowledge/`, empezá por `knowledge/index.md`". `CLAUDE.md` queda como shim `@AGENTS.md`.

## 5. Anti-duplicación + verificá
**Una verdad, un lugar.** Si algo quedó en dos lados, borralo de uno y linkeá. Generá
los `index.md` (raíz —subdirectorios **y** los conceptos que vivan en la raíz, como
`roadmap.md`, agrupados por `# {type}`— y hojas) y una entrada en `log.md` (`## YYYY-MM-DD`, "Migración
de contexto existente a OKF"). Corré `python3 scripts/okf_lint.py knowledge` (o
`okf-verify`) para detectar links rotos tras mover.

# Reglas
- **Verificá frescura antes de migrar o pointear.** Un doc stale NO es fuente de verdad: se
  declara no-autoritativo, nunca se pointea como tal. Pointear sin verificar = consagrar drift.
- **No dupliques.** El éxito de la migración se mide en que el contexto quedó en UN
  lugar, no en que hay más markdown.
- **No pises** un `knowledge/` que ya exista: en ese caso actualizá con `okf-update`.
- **Preguntá** lo que no se deduzca, y la **disposición de lo stale/dudoso** (mantener /
  actualizar / descartar); no inventes el *por qué* de una decisión vieja ni asumas que un doc
  viejo sigue vigente.
- **No borres el original hasta haber movido** su contenido al bundle.
