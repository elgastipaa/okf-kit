# Lente D — Estado del arte y posicionamiento de `okf-kit`

**Fecha del análisis:** 2026-07-30 · **Versión auditada:** `okf-kit` v0.7.3 (`VERSION`), 30 commits, primer commit 2026-06-17.
**Método:** lectura del repo (evidencia como `path:línea`) + búsqueda web con fuentes fechadas.
Marcas: **[V]** = verificado (leí la fuente / el repo / la API de GitHub) · **[H]** = hipótesis mía.

Todas las métricas de GitHub fueron consultadas vía `api.github.com` el **2026-07-30**, no
tomadas de artículos.

---

## 0. El hallazgo que reordena todo el informe

Existe, desde junio de 2026, un estudio revisado que mide exactamente lo que el kit promete —
y su conclusión de titular es **contraria** al consenso de la industria:

> **"Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"**
> Gloaguen, Mündler, Müller, Raychev, Vechev (SRI Lab, ETH Zürich), arXiv:2602.11988v2, junio 2026.
> https://arxiv.org/abs/2602.11988 · https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd

**[V]** Números:

| Medición | Resultado |
|---|---|
| Success rate, archivos **generados por LLM** | **−0.5%** en SWE-bench Lite, **−2%** en AGENTbench |
| Success rate, archivos **escritos por humanos** | **+4%** promedio en ambos benchmarks |
| Reasoning tokens (cualquier context file) | **+14–22%** |
| Pasos extra por tarea | **+2 a +4** |
| Costo de inferencia | **>+20%** |
| Uso de herramientas cuando el archivo lo pide | **×1.6** ("more activity isn't better activity") |

**[V]** Lo que el paper dice que **funciona**: "Tool choices that diverge from defaults.
Non-obvious test configurations. Constraints that aren't apparent from reading the code."
**[V]** Lo que **no** funciona: reproducir documentación que ya existe. Cuando los
investigadores **borraron los `.md` y `docs/` antes de generar**, los archivos autogenerados
**mejoraron 2.7% y superaron a los escritos por humanos**.
**[V]** Recomendación literal de los autores: *"human-written context files should describe
only minimal requirements"*.

### Por qué esto es simultáneamente la mejor y la peor noticia para OKF

**Valida la tesis central del kit, palabra por palabra.** Lo que el paper identifica como el
único contenido que paga es exactamente lo que `OKF-SPEC.md` §3.4 y `templates/AGENTS.md`
mandan escribir y lo que mandan **no** escribir:

- `templates/AGENTS.md` (§2, "Guardrails"): *"capturá el **por qué**, no el qué; **no
  dupliques** (una verdad, un archivo)"*.
- `templates/AGENTS.md` (§1): *"Lo que se deduce del código se **linkea**, no se copia (un
  número a mano = drift)"*.
- `knowledge/decisions/0009-entrypoint-is-a-map-not-an-answer.md:29-34`: el entrypoint es un
  mapa, no la respuesta.

**Y amenaza al kit en el mismo movimiento.** El paper mide *cualquier* archivo de contexto y
encuentra +20% de costo. `templates/AGENTS.md` son **148 líneas** de contrato genérico
*antes* de que el proyecto ponga una sola línea propia (`wc -l`), y el bundle instalado suma
índices, log, roadmap y templates. Si el kit no puede demostrar que su volumen paga, el paper
es la munición de cualquier escéptico.

**Lo notable: los propios datos del kit ya decían esto antes que el paper.**

- `eval/COMPARISON.md:11` — repos **sin ninguna capa de contexto** (idlerpg, 3.8 turnos) cuestan
  ~lo mismo que un wiki maduro sobre un repo grande (conclave, 4.7). *"Esperábamos que los
  repos sin capa de contexto fueran mucho más caros. **No lo son.**"*
- `eval/COMPARISON.md:111-129` — Loop 4 / Experimento 3: agregar hechos generados dio
  **resultado negativo**; *"Ninguna de las 4 preguntas de valor leyó el archivo generado"*.
- `eval/COMPARISON.md:84-89` — el kit **fabricó una respuesta confiada y equivocada** (q5) por
  tener una sección que *parecía* contestar.

Eso no es un problema de posicionamiento: **es el posicionamiento** (ver §3).

---

## 1. El campo hoy

### 1.1 Tabla maestra — qué cubre cada uno

Capas según el propio modelo del kit (`README.md:132-149`): **Pasado** (el porqué),
**Presente** (qué es y cómo funciona hoy), **Futuro** (rumbo + cambios en curso),
**Procedimientos** (cómo hago X), más tres ejes que el kit reclama como propios:
**normativo** (el doc obliga al código), **anti-drift** (detecta que el doc envejeció) y
**medición** (¿el contexto paga?).

| Herramienta | Tracción **[V]** 2026-07-30 | Pasado | Presente | Futuro | Proced. | Normativo | Anti-drift | Medición | Instala |
|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **`okf-kit`** | 0 públicos (30 commits) | ✅ `decisions/` | ✅ bundle | ✅ roadmap+`_changes/` | ✅ 5 skills | ✅ §3.5 + audit N4 | ✅ `okf_stale.py` | ✅ `templates/eval/` | nada (md+git+py stdlib) |
| **AGENTS.md** (estándar) | 60k+ repos, AAIF/Linux Foundation | ❌ | ⚠️ 1 archivo | ❌ | ❌ | ❌ | ❌ | ❌ | nada |
| **Claude Code** (CLAUDE.md + auto-memory + skills + plugins) | plataforma | ⚠️ privado | ✅ | ⚠️ | ✅ nativo | ❌ | ❌ | ❌ | el harness |
| **Cursor rules + Memories** | plataforma | ⚠️ privado/per-user | ✅ `.mdc` c/globs | ❌ | ⚠️ | ❌ | ❌ | ❌ | el harness |
| **GitHub Spec Kit** | **124,499 ★**, push 2026-07-29 | ❌ | ⚠️ constitution | ✅✅ pesado | ✅ slash cmds | ✅ constitution | ❌ | ❌ | CLI (uvx/py) |
| **OpenSpec** | **63,087 ★**, push 2026-07-30 | ❌ (archive≠porqué) | ⚠️ specs vivas | ✅✅ deltas | ✅ | ✅ spec archivada | ❌ | ❌ | `npm i -g` |
| **Google Conductor** | **3,673 ★**, push 2026-07-29 | ❌ | ✅ `conductor/*.md` | ✅ tracks | ✅ | ⚠️ | ❌ | ❌ | plugin/extension |
| **cc-sdd** | **3,589 ★**, push 2026-05-20 | ❌ | ⚠️ | ✅ | ✅ skills 8 harnesses | ⚠️ | ❌ | ❌ | npx |
| **harness-sdd** | **230 ★**, push 2026-06-03 | ❌ | ⚠️ docs/ | ✅ `feature_list.json` | ✅ 4 roles | ✅ CHECKPOINTS | ❌ | ⚠️ `init.sh` (tests, no costo) | clonar |
| **Mneme** | **17 ★**, push 2026-07-28 | ✅ ADRs | ❌ | ❌ | ❌ | ✅✅ checks deterministas | ⚠️ | ⚠️ alignment score | SaaS + repo |
| **Codified Context** (arXiv) | **181 ★**, push 2026-04-01 | ⚠️ | ✅✅ 3 tiers | ⚠️ | ✅ 19 agentes | ❌ | ⚠️ gap detection | ❌ (4 casos observ.) | MCP server |
| **PROJECTMEM** (arXiv) | **281 ★**, push 2026-07-08 | ✅ event-sourced | ⚠️ | ❌ | ❌ | ⚠️ judgment layer | ❌ | ⚠️ | local CLI |
| **Aider** CONVENTIONS.md + repomap | plataforma | ❌ | ✅ repomap auto | ❌ | ❌ | ⚠️ | ❌ | ❌ | el harness |
| **mem0 / cognee / Letta / ByteRover** | plataforma | ⚠️ | ✅ vector/graph | ❌ | ❌ | ❌ | ❌ | ❌ | servicio + DB |
| **Superpowers** (obra) | **263,279 ★**, push 2026-07-28 | ❌ | ❌ | ✅ plan-spec-test | ✅✅ | ❌ | ❌ | ❌ | plugin CC |
| **adr-tools / Log4brains** | clásicos | ✅ ADRs | ❌ | ❌ | ❌ | ⚠️ humano | ❌ | ❌ | CLI |

✅ = lo hace y es su foco · ⚠️ = parcial o accidental · ❌ = no lo cubre

### 1.2 Ficha por competidor

**AGENTS.md (el estándar).** **[V]** Formalizado en agosto 2025 (OpenAI + Google + Cursor +
Factory + Sourcegraph), hoy bajo gobernanza de la **Agentic AI Foundation (Linux Foundation)**
junto con MCP; leído nativamente por Codex, Cursor, Copilot, Gemini CLI, Aider, Windsurf, Zed,
Factory, Jules y 20+ herramientas; **60,000+ repos**.
Fuentes: https://blog.buildbetter.ai/agents-md-complete-guide-for-engineering-teams-in-2026/ ·
https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/
**[V]** Distribución real de archivos de configuración medida en 2026: AGENTS.md 42.7%,
CLAUDE.md 30.3%, copilot-instructions.md 13.7%
(https://arxiv.org/html/2606.09090).
- **Resuelve:** dónde poner las instrucciones, sin discusión de formato. Es *el* consenso.
- **NO resuelve:** nada más. Es un archivo sin schema, sin ciclo de vida, sin verificación, sin
  capa de porqué, sin detección de que envejeció. El paper de ETH mide justamente eso y le da
  cero de ganancia neta.
- **¿Se pisa con OKF?** **No — OKF lo usa.** `templates/AGENTS.md` ES un AGENTS.md, y
  `templates/CLAUDE.md` es un shim de una línea (`@AGENTS.md`). Esta es la decisión de
  posicionamiento más correcta del kit y hay que subrayarla en el pitch, no defenderla.

**Claude Code (CLAUDE.md + auto-memory + skills + plugins).** **[V]** El harness tiene hoy
cuatro scopes de CLAUDE.md, un subsistema **Auto Memory** que captura aprendizajes de sesión,
un pipeline de consolidación sobre la primitiva **Dreams**, un `MEMORY.md` que ancla el
directorio de auto-memoria y los comandos `/memory` y `/context`.
Fuente: https://vectorize.io/articles/claude-code-memory
**[V]** A nivel API/plataforma, Anthropic tiene un **memory tool** que persiste archivos entre
conversaciones (https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool), y
memoria persistente en **Managed Agents** desde 2026-04-23; benchmarks internos con context
editing: **84% de ahorro de tokens y +39% de performance** en una tarea de 100 turnos
(https://www.edtechinnovationhub.com/news/anthropic-brings-persistent-memory-to-claude-managed-agents-in-public-beta).
- **Resuelve:** continuidad de sesión, procedimientos (skills), compresión de contexto. Gratis
  y sin que el usuario haga nada.
- **NO resuelve:** portabilidad (vive en `~/.claude`), revisabilidad (no pasa por PR),
  autoridad (nada obliga al código), ni la pregunta "¿esto sirve?".
- **¿Se pisa con OKF?** **Sí, en dos capas de tres.** Ver §2.

**Cursor rules + Memories.** **[V]** `.cursor/rules/*.mdc` con frontmatter YAML y **cuatro
tipos de activación**: `Always` (siempre en contexto), `Auto Attached` (por glob), `Agent
Requested` (el modelo decide) y `Manual` (`@mención`). Las **Memories** son autogeneradas,
**per-project y per-user**: un compañero no las hereda salvo que alguien las promueva a mano a
un rules file.
Fuentes: https://skillwright.app/blog/cursor-rules-guide ·
https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/
- **Resuelve:** progressive disclosure **resuelto por el harness**, a costo cero de turnos.
- **NO resuelve:** el porqué, la portabilidad cross-vendor, el drift. Y las Memories son
  explícitamente no-compartidas: el conocimiento no se acumula en el equipo.
- **¿Se pisa con OKF?** **Sí, y en el punto más incómodo:** el `index.md` de OKF hace a mano y
  gastando turnos lo que el `.mdc` hace declarativamente. Ver §2 y robo #3.

**GitHub Spec Kit.** **[V]** 124,499 ★, actividad hoy mismo. `constitution.md` +
`/speckit.specify` → `.clarify` → `.plan` → `.tasks` → `.implement`, 30+ integraciones de agentes.
Fuente: https://github.com/github/spec-kit
**[V]** Crítica recurrente y fechada: *"the process is heavy, and the documents it produces
govern the code by convention rather than by enforcement"*; en brownfield multi-módulo
*"produces volume rather than fidelity"*; y el v0.10.0 rompió los tutoriales previos a junio 2026.
Fuentes: https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html ·
https://vibecoding.app/blog/spec-kit-review
- **Resuelve:** el futuro con ceremonia completa y auditoría para equipos.
- **NO resuelve:** el pasado (por qué el código es así), el drift, y —irónicamente— produce
  exactamente el volumen que el paper de ETH penaliza.
- **¿Se pisa con OKF?** Solo con la capa de futuro (`_changes/`). `reference/spec-driven-interop.md`
  ya documenta la convivencia. **Correcto no competir.**

**OpenSpec.** **[V]** 63,087 ★, push hoy. Ciclo `propose → apply → archive` con delta specs,
25+ herramientas, v1.4.1 en junio 2026, sin phase gates, orientado a brownfield.
Fuentes: https://github.com/Fission-AI/OpenSpec · https://rywalker.com/research/openspec
- **¿Se pisa con OKF?** Igual que Spec Kit: futuro sí, pasado no. `reference/spec-driven-interop.md:74-88`
  ya define la regla ("un solo dueño del trabajo en curso"). **Bien resuelto.**

**Google Conductor — el competidor más peligroso, y el que el kit no menciona.** **[V]**
3,673 ★, push 2026-07-29. Preview 2025-12-17 como extensión de Gemini CLI; **en 2026 se
convirtió en plugin portable** que corre en Antigravity y **Claude Code**. Guarda el contexto
del proyecto como **markdown versionado en git** bajo `conductor/`: `product.md`,
`tech-stack.md`, `workflow.md`, guías de estilo — más `tracks/` con `spec.md`, `plan.md` y
`metadata.json`.
Fuentes: https://github.com/gemini-cli-extensions/conductor ·
https://developers.googleblog.com/evolving-spec-driven-development-conductor-now-supports-antigravity/ ·
https://developers.googleblog.com/conductor-introducing-context-driven-development-for-gemini-cli/
- **Por qué es el más peligroso:** es la **única** herramienta del set que comparte las tres
  propiedades que el kit vende como diferenciales — markdown, git, sin servicio externo — y
  además tiene distribución de Google y multi-harness. No es un CLI de npm que un vibecoder
  evita: es un plugin.
- **Lo que NO tiene [V]:** capa de pasado (no hay `decisions/`, no hay concepto de documento
  normativo), detección de drift, y ninguna medición.
- **Gap concreto del kit:** `reference/spec-driven-interop.md` nombra OpenSpec, Spec Kit y Kiro
  — **no nombra Conductor**, que es con el que más se pisa. Es la omisión más costosa del repo.

**cc-sdd.** **[V]** 3,589 ★, push 2026-05-20. "Minimal, adaptable SDD harness with Agent Skills
for Claude Code, Codex, Cursor, Copilot, Windsurf, OpenCode, Gemini CLI, Antigravity."
Fuente: https://github.com/gotalab/cc-sdd
- Relevante porque demuestra que **"un skill por harness, desde una sola fuente"** ya es un
  patrón establecido — lo mismo que el kit hace con `templates/skills/`.

**harness-sdd.** **[V]** 230 ★, push 2026-06-03. Roles `leader` / `spec_author` / `implementer`
/ `reviewer` en `.claude/agents/`; `specs/<feature>/{requirements,design,tasks}.md`; `progress/`
con `current.md` e `history.md`; `feature_list.json` con estados `pending → spec_ready →
in_progress → done`; `CHECKPOINTS.md`; `init.sh` que corre los tests, valida que los features
marcados SDD tengan spec y **enforcea un único feature activo**. Lema: *"state in disk, not in chat"*.
Fuente: https://github.com/betta-tech/harness-sdd
- **Sobre el no-goal del kit:** los 230 ★ frente a 124k de Spec Kit son evidencia de mercado a
  favor de **sostener** el no-goal de los roles. Ver §4.

**Mneme.** **[V]** 17 ★ en GitHub (`MnemeHQ/mneme`, push 2026-07-28) + producto en mnemehq.com.
Convierte ADRs en **checks deterministas pre-generación** para Claude Code, Cursor y Copilot;
un evaluador chequea cada respuesta contra las decisiones inyectadas y devuelve un
**alignment score** determinista.
Fuentes: https://github.com/MnemeHQ/mneme · https://mnemehq.com/insights/how-ai-coding-agents-use-adrs/
- **Es el único competidor directo de la capa normativa de OKF.** Su tesis — *"An ADR that only
  informs is a suggestion. An ADR that also verifies is a guardrail"* — es literalmente la
  ADR 0021 del kit llevada a producto.
- **Tracción real: mínima (17 ★).** El kit tiene tiempo, pero la idea ya está nombrada por otro.

**Codified Context (arXiv 2602.20478, Vasilopoulos, 2026-02-24).** **[V]** Tres tiers: *hot
memory* (constitución de ~660 líneas cargada siempre), 19 agentes de dominio (9,300 líneas), y
*cold memory* (34 specs on-demand, ~16,250 líneas) indexada por un servicio MCP. Sobre un
sistema C# de 108,000 líneas, 283 sesiones, 70 días: **26,200 líneas de infraestructura de
contexto = 24.2% del codebase**. Repo: https://github.com/arisvas4/codified-context-infrastructure
(181 ★, push 2026-04-01).
- **Es OKF llevado al extremo** y confirma que la arquitectura de tres capas del kit no es
  idiosincrática. **Pero su evidencia son 4 case studies observacionales, sin baseline.** No
  puede responder si las 26,200 líneas pagaron.

**PROJECTMEM (arXiv 2606.12329, Malo & Qiu, junio 2026).** **[V]** Memoria local-first,
event-sourced, integrada con git, con una *judgment layer*. Repo:
https://github.com/riponcm/projectmem (281 ★, push 2026-07-08).
- Captura **intentos fallidos** — algo que OKF hoy no modela y que un vibecoder sufre a diario
  ("la IA re-rompe lo que ya arreglé").

**Lore (arXiv 2603.15566, Stetsenko, 2026-03-17).** **[V]** Propone usar los mensajes de commit
como protocolo estructurado de conocimiento. **Sin implementación ni métricas** — es una
propuesta. Relevante como señal: el "pasado" es problema reconocido en la literatura.

**Context rot / DOCER (arXiv 2606.09090, Treude & Baltes, 2026-06-08).** **[V]** Aplicaron
DOCER (un checker de consistencia de README, sin modificar) a **612 archivos de configuración
de IA en 356 repos**: **23.0% de los repos (82/356) tienen referencias a código muertas** en su
AGENTS.md/CLAUDE.md; 230 referencias stale sobre 18,048 elementos verificados; inspección manual
de 50 casos → **64% son stale reales**, 36% falsos positivos por regex ancha. Tool open source,
resultados en Zenodo. https://arxiv.org/html/2606.09090
- **Es la validación externa de `okf_stale.py`** y el número duro que le faltaba al pitch.

**Aider.** **[V]** `CONVENTIONS.md` como read-only file + **repo map** generado con tree-sitter.
Fuentes: https://aider.chat/docs/config/aider_conf.html ·
https://github.com/Aider-AI/aider/blob/main/aider/website/docs/repomap.md
- Su repo map es el argumento más fuerte contra la mitad "descriptiva" de un bundle: **la
  estructura del código se deriva automáticamente**. Refuerza `OKF-SPEC.md` §3.4.

**Memory layers (mem0, cognee, Letta, Zep, ByteRover).** **[V]** ByteRover lidera LoCoMo
(multi-hop 92.2%, temporal 94.4%) y es *purpose-built for coding agents*, tratando la memoria
como un **versioned context tree**. cognee 1.0 corre grafo+vectores+sesiones sobre un Postgres.
Fuentes: https://www.cognee.ai/blog/guides/best-ai-memory-layers-for-ai-agents-in-2026-comparison ·
https://get-hermes.ai/memory/
- **No compiten con OKF en el mismo eje:** requieren servicio y/o DB, violando la premisa de
  `decisions/0004-vendor-neutral-no-external-apps.md`. Compiten por el **presupuesto de
  atención** del usuario ("ya tengo memoria, ¿para qué markdown?").

**Superpowers (obra).** **[V]** 263,279 ★, push 2026-07-28 — el plugin de Claude Code más
grande del ecosistema, "agentic skills framework & software development methodology".
Fuente: https://github.com/obra/superpowers
- **Es la referencia de distribución.** No se pisa en contenido (es metodología de desarrollo,
  no de conocimiento), pero define qué "se ve como una herramienta que la gente instala".

**El upstream: OKF de Google Cloud.** **[V]** Anunciado **2026-06-16**, v0.1, alcance declarado
= *knowledge catalogs* y contexto de datos organizacional ("table schemas, metric definitions,
runbooks, join paths"), **explícitamente no pensado como estándar general de repos de software**.
Fuentes: https://www.marktechpost.com/2026/06/16/google-cloud-introduces-open-knowledge-format-okf-a-vendor-neutral-markdown-spec-for-giving-ai-agents-curated-context/ ·
https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
**[V]** `GoogleCloudPlatform/knowledge-catalog`: 8,036 ★, push 2026-07-29 — **y la SPEC ya está
en v0.2** (dos breaking changes desde v0.1, más familias de frontmatter: `sources`, `generated`,
`verified`, `status`, `stale_after`, `runtime`, `parameters`, `executor`, `attester`).
https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

> **Dos consecuencias operativas [V]:**
> 1. **`okf-kit` es first-mover.** El primer commit del kit es **2026-06-17**, un día después
>    del anuncio, y generaliza OKF a un dominio que Google explícitamente **no** cubrió (repos
>    de código). Eso es una ventaja real y hoy no se comunica en ningún lado.
> 2. **Deriva de versión detectada.** `OKF-SPEC.md:3` dice "Versión 0.1" y `knowledge/index.md:2`
>    estampa `okf_version: "0.1"`, pero el upstream ya publicó **v0.2**. Los campos nuevos
>    `stale_after`, `verified` y `generated` son **exactamente** los que el kit reinventó por su
>    cuenta (`_generated/`, ADR 0010, `okf_stale.py`). Alinear con v0.2 es gratis y convierte
>    tres invenciones locales en conformidad con el estándar.

---

## 2. Qué le come el almuerzo a OKF

### 2.1 En riesgo de volverse redundante (ordenado por urgencia)

**A. La capa "Procedimientos" — ya está absorbida. [V]**
`README.md:140` la vende como una de las tres capas. Pero los skills son una primitiva nativa de
Claude Code, cc-sdd ya publica skills para 8 harnesses, y Superpowers tiene 263k ★. Los cinco
`templates/skills/*/SKILL.md` (690 líneas totales) **no son un diferencial** — son plomería
necesaria. **Acción:** dejar de listarlos como capa vendible; presentarlos como "el kit se
instala como plugin, igual que todo lo demás".

**B. El `index.md` como mecanismo de progressive disclosure — el pedazo del *formato* con más
riesgo. [V]** Cursor resuelve lo mismo declarativamente con `.mdc` (globs, agent-requested) y
Claude Code con la `description` del frontmatter de skill: **el harness decide qué cargar, a
costo cero de turnos**. El `index.md` requiere que el agente lo *lea* — y el paper de ETH mide
exactamente eso como +2–4 pasos. **Esto no mata a OKF** (el `index.md` es la fuente única y
portable), **pero sí mata el argumento "OKF te da progressive disclosure"**: eso ya lo da la
plataforma, mejor. **Acción:** ver robo #3 — pasar de "el index es el mecanismo" a "el index es
la fuente, y el kit la proyecta al mecanismo nativo de cada harness".

**C. El ítem de roadmap "Estado de sesión en vivo" — nace muerto. [V]**
`knowledge/roadmap.md:38-39` propone capturar "dónde quedó la sesión si el contexto se corta".
Claude Code ya tiene Auto Memory + `MEMORY.md` + consolidación con Dreams + `/memory`; Cursor
tiene Memories autogeneradas; Anthropic tiene un memory tool a nivel API con **84% de ahorro de
tokens** medido. Reimplementarlo en markdown es llegar tarde y peor.
**Acción concreta:** reformular ese ítem. Lo que la plataforma **no** da y sí falta es que ese
estado sea **portable y revisable en un PR**. Si se hace, que sea "exportar la memoria privada
al bundle", no "inventar un archivo de sesión".

**D. La promesa "sin reventar la ventana de contexto" (`README.md:165`) — cada vez menos
diferencial. [V]** Con context editing + compaction nativos, el harness recorta solo. La
promesa que sí queda en pie es *"el agente no recorre todo el código"* — y esa es medible
(§3), que es donde hay que llevarla.

**E. El volumen del propio kit — la amenaza que el kit se hace a sí mismo. [V]**
`templates/AGENTS.md` = 148 líneas *antes* del contenido del proyecto. El paper de ETH dice
"minimal requirements only", y el propio `eval/COMPARISON.md:111-129` ya registró un resultado
negativo por agregar material. **Nadie ha medido cuánto cuesta cargar el contrato del kit
contra cuánto ahorra.** Es la pregunta más peligrosa que le pueden hacer al kit, y hoy
`run-eval.py` no la puede responder porque no tiene un brazo intermedio (ver robo #1).

### 2.2 Lo que la plataforma NO puede absorber nunca

**1. El porqué, en git, revisable.**
Un harness puede recordar *lo que pasó en la sesión*. No puede inventar la razón de una
decisión que nadie escribió. Y lo que sí captura es **privado y per-user** — está verificado
para Cursor ("a teammate doesn't inherit yours unless you promote it into a rules file by
hand") y es estructuralmente cierto para `~/.claude`. `README.md:151-155` lo llama "la cuarta
capa que es una trampa" y tiene razón. **Este es el foso.**

**2. El registro normativo: el documento que obliga al código.**
`OKF-SPEC.md` §3.5 y `templates/AGENTS.md` §1 definen que una `decision` con `status: accepted`
convierte una discrepancia en **violación del código**, con dos salidas legítimas (arreglar o
superseder) y prohibición explícita de editar el doc en silencio. Ninguna memoria de plataforma
hace esto — las memorias son **descriptivas por construcción**. El único que compite es Mneme
(17 ★). Un harness nunca va a decirte "tu código viola tu propia decisión": no tiene forma de
saber cuál era normativa.

**3. Detección de drift sin gastar un token.**
`templates/scripts/okf_stale.py:11-20`: `resource:` que ya no existe (drift **confirmado**),
`timestamp` podrido, y churn desde el timestamp. Cero tokens, solo git + frontmatter. La
plataforma no sabe que tu doc envejeció — y el paper de Treude & Baltes mide que **pasa en el
23% de los repos**. Ningún competidor del set tiene esto.

**4. La medición.** Ver §3. Es el único eje donde el kit está solo.

**5. Auditoría por un tercero sin sesgo de autor.**
`templates/agents/okf-reviewer.md:1-30`: *"quien escribió algo no puede auditarlo"*, sin permisos
de escritura (`disallowedTools: Write, Edit, NotebookEdit`), consigna *"buscá la contradicción,
no la confirmación"*. Un harness auto-evalúa; nunca se va a poner un revisor encima por default.

---

## 3. El diferencial defendible: la medición

### 3.1 Verificación: ¿alguien más mide lo que `templates/eval/` mide?

Busqué específicamente herramientas que midan **turnos / tokens / acierto de un agente contra
TU repo, con y sin capa de contexto**. Resultado:

| Categoría | Qué miden | ¿Equivalente a `templates/eval/`? |
|---|---|---|
| SWE-bench, Terminal-Bench, AgentBench, TAU-bench | el **agente/modelo** | ❌ — no miden tu contexto |
| `linny006/agent-eval-harness`, `harness/harness-evals` | comparar **agentes** en issues de GitHub | ❌ — el eje es el agente |
| DeepEval, RAGAS | métricas de LLM/RAG genéricas | ❌ — no atadas a un repo |
| Spec Kit, OpenSpec, Conductor, cc-sdd | nada | ❌ **[V]** |
| harness-sdd `init.sh` **[V]** | corre tests, valida presencia de specs, enforcea 1 feature activo | ❌ — es un **gate de conformidad**, no una medición de costo/acierto |
| Mneme **[V]** | alignment score contra ADRs inyectadas | ⚠️ — mide **cumplimiento**, no **costo de retrieval** |
| Codified Context **[V]** | 4 case studies observacionales, sin baseline | ❌ |
| arXiv 2602.11988 (ETH) **[V]** | exactamente esto — A/B con y sin context file | ⚠️ **es un paper, no una herramienta que puedas correr en tu repo** |

**Conclusión [V]: nadie tiene el equivalente.** El único trabajo que hace la medición correcta
es académico, se corre sobre benchmarks públicos y **su veredicto es negativo para el estado
del arte**. No existe la herramienta que le diga a *un desarrollador concreto* si *su* capa de
contexto paga.

### 3.2 Qué tiene el kit, verificado

- `templates/eval/run-eval.py` — corre cada pregunta en un proceso headless fresco (`claude -p`),
  registra `cache_read` como métrica de contexto real, `num_turns`, `duration_ms`, `cost_usd`,
  y opcionalmente el acierto vía juez (`run-eval.py:122-133`).
- **La cuarta columna es el diseño clave** (`templates/eval/README.md:23`): *"una respuesta
  rápida y equivocada es peor que una lenta y correcta"*. Sin ella se optimiza hacia respuestas
  vagas.
- **Honestidad instrumental verificable:** `run-eval.py:46-53` documenta por qué una corrida
  fallida devuelve `None` y no `{}` (*"el peor bug posible en un harness de medición"*), y
  `run-eval.py:144-149` promedia solo sobre corridas que corrieron.
- **Track record público de auto-refutación** — esto es lo más difícil de fingir:
  - `eval/COMPARISON.md:13-16` — hipótesis ingenua **refutada** por los propios datos.
  - `eval/COMPARISON.md:66-70` — experimento **invalidado por contaminación del
    experimentador**, admitido y re-hecho blind.
  - `eval/COMPARISON.md:84-89` — el kit **fabricó una respuesta confiada y mala**; lo cazó el
    acierto, y salió la ADR 0009.
  - `eval/COMPARISON.md:111-129` — Experimento 3: **resultado negativo**, feature descartada.
  - `knowledge/roadmap.md:53-54` — el kit **admite que su propio juez está roto** para preguntas
    de comportamiento.

### 3.3 Cómo se convierte en punta de lanza

El paper de ETH le regala al kit el mejor *hook* de posicionamiento posible, porque ataca
directamente a lo que hace el 90%:

> **"El estudio más grande sobre AGENTS.md (ETH Zürich, junio 2026) encontró que no mejoran
> nada y cuestan >20% más. Tienen razón — para los AGENTS.md que nadie midió. Este kit es el
> único que trae la balanza."**

Tres movimientos concretos, en orden:

1. **Desgitignorar `/eval/` y publicar los scorecards.** `.gitignore:11` excluye `/eval/`
   entero — **el diferencial está literalmente oculto en el repo**. El único artefacto visible
   es `eval/COMPARISON.md`, que sobrevive por estar trackeado desde antes. `roadmap.md:30-32`
   ya lo reconoce (*"Es el diferencial que ningún competidor tiene"*) pero lo pone **tercero**
   en la lista de adopción. Debe ser **primero**: es más barato que el repo de ejemplo y es lo
   único que un desconocido no puede replicar leyendo el README.
2. **Publicar el número contra el baseline correcto** (ver robo #1): no "el kit mejora X%" sino
   "el bundle cuesta N tokens de carga y ahorra M — acá está el jsonl".
3. **Empaquetar el harness como producto separable.** `templates/eval/` sirve para medir
   *cualquier* capa de contexto, no solo OKF. Un vibecoder que usa Spec Kit puede correrlo. Es
   la única pieza del kit con valor autónomo para usuarios de la competencia — y por lo tanto
   la mejor puerta de entrada.

---

## 4. Robos legítimos (rankeados)

Antes: **los no-goals del roadmap [V]**.

- **`roadmap.md:63-64` — los otros tres roles de harness-sdd (leader/spec_author/implementer):
  SOSTENER.** Evidencia nueva a favor del no-goal, no en contra: harness-sdd tiene **230 ★**
  frente a 124k de Spec Kit y 63k de OpenSpec; el mercado no está pidiendo roles. Además el
  paper de ETH penaliza el volumen de instrucciones, y los roles son volumen puro.
- **`roadmap.md:69-70` — no reimplementar SDD completo estilo OpenSpec: SOSTENER y REFORZAR.**
  OpenSpec tiene 63,087 ★ y commits de hoy; competir es suicida. **Pero el doc de interop tiene
  un agujero:** `reference/spec-driven-interop.md` nombra OpenSpec, Spec Kit y Kiro y **no
  nombra Conductor** (3,673 ★, plugin portable, markdown+git, respaldo Google) — el único que
  ocupa exactamente el mismo nicho técnico. Agregarlo es una hora de trabajo.
- **`roadmap.md:65-66` — no harvester con contexto fresco: SOSTENER.** El razonamiento
  ("contexto fresco sirve para auditar, no para recordar") sigue siendo correcto y ningún
  competidor lo contradice.

Ninguno de los cinco robos viola un no-goal.

---

### Robo #1 — Baseline de tres brazos: medir el **costo del contexto**, no solo la mejora
**Fuente [V]:** https://arxiv.org/abs/2602.11988 (Gloaguen et al., ETH Zürich, junio 2026) —
+14–22% reasoning tokens, +2–4 pasos, >+20% costo con cualquier context file.

**Qué se roba:** el diseño experimental. El paper compara *sin contexto* vs *con contexto*; el
kit compara `--mode nokit` vs `--mode kit` (`run-eval.py:93`). **Falta el brazo del medio**, que
es exactamente la objeción del 90%: *"¿y contra un AGENTS.md pelado?"*.

**Concreto:** agregar `--mode agentsmd` (solo el entrypoint, sin bundle) a
`templates/eval/run-eval.py`, y agregar al resumen un veredicto explícito de balance — el
runner ya captura `cache_read` y `cost_usd` (`run-eval.py:126-132`), solo falta el criterio.
Complementariamente, endurecer el loop de `templates/eval/README.md:65-66`: hoy dice "conservar
solo si baja turnos sin introducir incorrecta"; debería decir **"y sin subir el costo total"**.

**Por qué encaja con markdown+git:** es una flag y ~20 líneas de stdlib en un script que ya
existe. Cero dependencias nuevas.

**Impacto:** es el único robo que produce **la frase del pitch**.

---

### Robo #2 — Estado del trabajo machine-readable (sin roles)
**Fuente [V]:** https://github.com/betta-tech/harness-sdd — `feature_list.json` con estados
`pending → spec_ready → in_progress → done` e `init.sh` que **enforcea un único feature activo**.

**Qué se roba:** *solo* el estado verificable. **No** los roles (no-goal respetado).

**El kit ya lo pidió y le faltaba evidencia:**
- `roadmap.md:40-41` — *"el roadmap es prosa, así que '≤1 cosa en curso' no lo puede enforcear
  ni el linter ni el hook"*.
- `roadmap.md:57-58` — higiene de `_changes/` (cambios zombie) *"solo si la medición muestra que
  pasa seguido"*.

**La evidencia externa llegó [V]:** Treude & Baltes miden **23% de repos con referencias
muertas** en sus archivos de configuración de IA (https://arxiv.org/html/2606.09090). Los
cambios zombie son la misma patología. Y **el upstream OKF v0.2 ya trae los campos**: `status` y
`stale_after` en el frontmatter estándar
(https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

**Concreto:** frontmatter `status:` en los docs de `_changes/` (usando el vocabulario de OKF
v0.2, no uno propio) + dos asserts en `templates/scripts/okf_lint.py`: (a) ≤1 cambio con estado
activo, (b) cambio activo cuyo `timestamp` quedó atrás de N commits → warning de zombie.

**Por qué encaja:** el linter ya lee frontmatter y ya es stdlib. Cero ceremonia nueva: es un
campo, no un archivo.

---

### Robo #3 — Activación declarada por glob (defender el `index.md` de la absorción)
**Fuente [V]:** Cursor `.cursor/rules/*.mdc` con cuatro tipos de activación (`Always`,
`Auto Attached` por glob, `Agent Requested`, `Manual`) —
https://skillwright.app/blog/cursor-rules-guide ·
https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/

**El problema que resuelve:** hoy la progressive disclosure de OKF cuesta turnos (leer
`index.md` → decidir → leer concepto). Cursor y Claude Code la resuelven a costo cero desde el
frontmatter. Es el riesgo **B** de §2.1.

**Concreto — y compatible con la decisión 0004:** un campo **opcional** en el frontmatter del
concepto, tipo `applies_to: ["src/combat/**"]`. En OKF puro es metadata inerte (el spec permite
claves adicionales, `OKF-SPEC.md:263`). Pero `scripts/okf_install.py` puede **proyectarlo**:
generar `.cursor/rules/okf-<concepto>.mdc` con el glob y un puntero de una línea al concepto.

**Una verdad (`knowledge/`), N proyecciones (shims generados).** Es exactamente el patrón que el
kit ya usa con `templates/CLAUDE.md` (`@AGENTS.md`), escalado. No duplica contenido: duplica
*punteros*, que es lo que el kit sí permite.

**Por qué encaja:** el instalador ya genera archivos y ya verifica su salida con el linter
(`README.md:55-58`). Y ataca el flanco más expuesto del formato.

---

### Robo #4 — Referencias de código muertas en el cuerpo del concepto (extender `okf_stale.py`)
**Fuente [V]:** https://arxiv.org/html/2606.09090 — Treude & Baltes aplicaron **DOCER sin
modificar** a 612 archivos de config de IA en 356 repos: extrajeron referencias a elementos de
código y verificaron su presencia entre el commit inicial y HEAD. **23.0% de repos con
referencias stale**; 230 stale sobre 18,048 elementos; **64% de precisión** en inspección manual
de 50 casos (36% falsos positivos por regex ancha).

**El gap [V]:** `templates/scripts/okf_stale.py:11-20` usa tres señales — `resource:` inexistente,
`timestamp` podrido, churn. **Ninguna mira dentro del cuerpo del documento.** Un concepto que
menciona `` `FINISHER_ANTI_WASTE_RULES` `` o `` `src/game/talentNodes.js` `` en prosa y esos
símbolos ya no existen es drift confirmado, gratis de detectar, y hoy el kit no lo ve.

**Concreto:** un cuarto bloque en `okf_stale.py` que extraiga tokens en backticks con forma de
path o de símbolo y chequee existencia con `git ls-files` / grep. **Reportar la precisión
esperada** (el paper mide 64%) para no vender certeza donde hay heurística — coherente con que
el script declara explícitamente "no es un gate".

**Por qué encaja:** sigue siendo git + stdlib + cero tokens, la propiedad que hace que el
script se corra de verdad.

**Bonus de posicionamiento:** es la primera métrica dura que el kit podría publicar **sobre
repos ajenos** ("corrimos esto sobre N repos populares con AGENTS.md, el X% tiene referencias
muertas"). Eso es contenido de adopción que hoy no existe (`roadmap.md:28-29`).

---

### Robo #5 — Portabilidad como artefacto generado, no como promesa
**Fuente [V]:** https://developers.googleblog.com/evolving-spec-driven-development-conductor-now-supports-antigravity/
— Conductor dejó de ser extensión de Gemini CLI y pasó a plugin portable: *"By becoming a
plugin, Conductor is now a portable, ecosystem-wide capability."* Refuerzo:
https://github.com/gotalab/cc-sdd (3,589 ★) shippea skills para 8 harnesses desde una fuente.

**El gap [V]:** el kit dice "vendor-neutral" (`README.md:142-144`) y lo cumple *conceptualmente*
—`reference/install-per-tool.md` explica cómo apuntar cada IA— pero lo único que **genera** es
`.claude-plugin/` y, con `--no-claude`, procedimientos en `docs/okf/`. Para Cursor y Copilot el
usuario tiene que hacer algo a mano. **Neutralidad que requiere trabajo manual pierde contra
un plugin que se instala.**

**Concreto:** que `okf_install.py` genere shims de una línea —`.cursor/rules/okf.mdc`,
`.github/copilot-instructions.md`, `GEMINI.md`— todos apuntando a `AGENTS.md`. Es literalmente
lo que `templates/CLAUDE.md` ya hace (`@AGENTS.md`), replicado. Sin contenido duplicado: solo
punteros, así que no hay deriva posible y no viola la regla dura de "una fuente de verdad".

**Por qué encaja:** el instalador ya escribe archivos y todo se revierte con `git checkout`
(`README.md:61`). Son ~4 archivos de una línea.

---

### Robo #6 (menor, opcional) — "Un ADR que solo informa es una sugerencia"
**Fuente [V]:** https://mnemehq.com/insights/how-ai-coding-agents-use-adrs/ — *"Enforcement
requires a deterministic check that verifies the code against the decision, not a model that is
merely reminded of it."*

El kit ya tiene la mitad correcta: el Nivel 4 de `reference/verification.md` + `okf-reviewer`.
Lo que Mneme agrega es que **algunas** decisiones son grep-ables ("no importar X desde Y", "no
usar la lib Z"). Robo: un campo opcional `check:` en el frontmatter de una `decision` con un
comando shell que la verifica, que `okf_lint.py` corre si existe. Sube el porcentaje de
decisiones enforceadas sin gastar un token de agente.

**Cautela [H]:** Mneme tiene 17 ★. Bajo en el ranking porque no hay evidencia de demanda, y
porque el frontmatter con comandos ejecutables es una superficie de riesgo. Solo si la medición
muestra que las violaciones normativas son frecuentes.

---

## 5. El pitch de una línea

### El obstáculo real

El 90% va a decir *"poné un AGENTS.md y listo"*. **Ahora hay un número para responder eso**, y
no es del kit: es de ETH Zürich.

### Pitch primario

> **"Un AGENTS.md le dice a la IA cómo correr los tests. OKF le dice por qué tu código es así
> — y te da el número que prueba que sirve."**

### Variantes según audiencia

- **Vibecoder puro (5 segundos):**
  *"Tu IA no se olvida de los comandos. Se olvida de por qué decidiste algo hace tres semanas.
  Eso es lo que OKF guarda — en tu repo, en git, en markdown."*
- **Escéptico técnico (con la munición del paper):**
  *"El estudio más grande sobre AGENTS.md (ETH Zürich, jun 2026) midió: cero mejora, +20% de
  costo. Lo único que dio +4% fue el contenido humano que el código no puede decir. OKF es el
  formato para escribir ese contenido — y el único kit que trae la balanza para verificar que
  el tuyo lo esté haciendo."*
- **El que ya usa Spec Kit / OpenSpec / Conductor:**
  *"Ellos gestionan lo que vas a construir. OKF guarda por qué lo que ya construiste es así.
  Conviven —está documentado— y el harness de medición te sirve igual."*

### La estructura de la diferenciación, en tres golpes

| Objeción | Respuesta | Respaldo |
|---|---|---|
| "Con AGENTS.md alcanza" | AGENTS.md **es** la puerta; OKF es lo que hay detrás. El kit *genera* tu AGENTS.md | `templates/AGENTS.md`; arXiv 2602.11988 (+4% solo con contenido no-derivable) |
| "Claude ya tiene memoria" | Sí — privada, per-user, no revisable en PR, no portable. Tu socio no la hereda | Cursor Memories per-user **[V]**; `README.md:151-155` |
| "¿Y cómo sé que sirve?" | Corré el harness. Es la pregunta que nadie más te deja hacer | `templates/eval/`; §3.1 (nadie tiene equivalente) |

### Lo que hay que dejar de decir **[H, pero fundado en el paper]**

- ~~"progressive disclosure"~~ → lo da la plataforma, mejor. Decir "una fuente, proyectada a
  cada harness".
- ~~"tres capas"~~ → dos son commodity. La capa que importa es **el porqué + su verificación**.
- ~~"nunca perder contexto"~~ → es lo que promete literalmente todo el mercado de memory layers.
  El diferencial no es *guardar*, es **probar que lo guardado paga**.

---

## Anexo — Fuentes

**Papers (todas verificadas leyendo el PDF/HTML):**
- arXiv:2602.11988 — Evaluating AGENTS.md (Gloaguen, Mündler, Müller, Raychev, Vechev; ETH Zürich SRI Lab; jun 2026) — https://arxiv.org/abs/2602.11988 · https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd
- arXiv:2606.09090 — Context Rot in AI-Assisted Software Development (Treude, Baltes; 2026-06-08) — https://arxiv.org/html/2606.09090
- arXiv:2602.20478 — Codified Context (Vasilopoulos; 2026-02-24) — https://arxiv.org/html/2602.20478v1
- arXiv:2606.12329 — PROJECTMEM (Malo, Qiu; jun 2026) — https://arxiv.org/pdf/2606.12329
- arXiv:2603.15566 — Lore (Stetsenko; 2026-03-17) — https://arxiv.org/pdf/2603.15566
- arXiv:2602.14690 — Harness Engineering (Galster et al.; AIware '26; 2026-07-02) — https://arxiv.org/pdf/2602.14690

**Repos (★ y `pushed_at` vía api.github.com, 2026-07-30):**
- https://github.com/github/spec-kit · https://github.com/Fission-AI/OpenSpec · https://github.com/gemini-cli-extensions/conductor · https://github.com/gotalab/cc-sdd · https://github.com/betta-tech/harness-sdd · https://github.com/MnemeHQ/mneme · https://github.com/riponcm/projectmem · https://github.com/arisvas4/codified-context-infrastructure · https://github.com/obra/superpowers · https://github.com/GoogleCloudPlatform/knowledge-catalog

**Docs y artículos fechados:**
- https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md (v0.2)
- https://www.marktechpost.com/2026/06/16/google-cloud-introduces-open-knowledge-format-okf-a-vendor-neutral-markdown-spec-for-giving-ai-agents-curated-context/
- https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- https://developers.googleblog.com/evolving-spec-driven-development-conductor-now-supports-antigravity/
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
- https://vectorize.io/articles/claude-code-memory
- https://www.edtechinnovationhub.com/news/anthropic-brings-persistent-memory-to-claude-managed-agents-in-public-beta
- https://skillwright.app/blog/cursor-rules-guide
- https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/
- https://blog.buildbetter.ai/agents-md-complete-guide-for-engineering-teams-in-2026/
- https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html
- https://rywalker.com/research/openspec
- https://mnemehq.com/insights/how-ai-coding-agents-use-adrs/
- https://academy.dair.ai/blog/agents-md-evaluation
- https://aider.chat/docs/config/aider_conf.html · https://github.com/Aider-AI/aider/blob/main/aider/website/docs/repomap.md
- https://www.cognee.ai/blog/guides/best-ai-memory-layers-for-ai-agents-in-2026-comparison · https://get-hermes.ai/memory/
