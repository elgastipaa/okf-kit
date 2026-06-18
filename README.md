# OKF — Guía para implementar ingeniería de contexto en cualquier repo

Esta carpeta es una **guía self-contained + librería de templates** para montar
un sistema de contexto duradero en cualquier proyecto, usando el **Open Knowledge
Format (OKF)**.

El objetivo: que **cualquier IA, en cualquier momento, desde cualquier máquina**
entienda un proyecto sin que se lo expliques de nuevo. El contexto vive en el
repo, en git, en markdown plano — no en la memoria privada de una herramienta.

> Esta guía no depende de ningún servicio, SDK ni de la nube. Es markdown.
> Si podés `cat` un archivo, podés leerla; si podés `git clone`, la podés llevar.

**Aplicable a cualquier proyecto.** OKF es agnóstico al dominio. La misma mecánica
sirve para repos de **código**, proyectos de **datos/analytics** y **wikis / bases
de conocimiento**. Lo único que cambia entre ellos es el layout de carpetas y el
vocabulario de `type:` — eso se elige con un *perfil* (ver `reference/profiles.md`).

**Sin apps externas ni instalaciones.** No hace falta Obsidian, Notion, MkDocs, un
visor de grafos ni ningún servicio: es markdown + git. Un humano lo lee en GitHub o
con `cat`; un agente lo lee como archivos. El kit incluye un linter de Python
opcional (`okf_lint.py`) para validar conformidad y correr en CI — **solo stdlib,
sin `pip install`**. No hay nada que adoptar para *usar* el bundle.

> **¿La máquina no tiene Python?** El linter necesita un intérprete Python 3 (sin
> librerías, solo el intérprete). Si no lo tenés: instalá Python 3, **o** dejá que
> el agente haga ese chequeo leyendo los archivos vía el skill `okf-verify`. El
> resto del sistema no usa Python en absoluto.

---

## Cómo se usa (los "prompts mágicos")

Esta carpeta está pensada para que se la cites a un agente en frío. Abrís un
Claude Code (o cualquier CLI de IA) **sin contexto previo** y le decís:

**Para montar OKF en un repo (lo más común):**
```
Cloná okf-kit y aplicalo a mi repo <X>.
```

El agente debe entonces abrir el **`GUIDE.md`** del kit y arrancar por su **Paso 0
(START HERE)**, que lo orienta: el destino es **tu repo `<X>`** (nunca se escribe nada
dentro de `okf-kit`), confirmá su ruta, y elegí init (repo limpio) o `okf-migrate`
(repo con docs/contexto dispersos). Todos los paths de la doc son **relativos a la raíz
del kit**, así que apuntá al agente a donde clonaste `okf-kit`.

> **Tip:** instalá el skill `okf-init` (de `templates/skills/okf-init/`) en
> `~/.claude/skills/okf-init/` para que ese prompt dispare un procedimiento
> estructurado, en vez de depender de que el agente lea bien el `GUIDE`.

**Para actualizar el contexto de un repo que ya tiene OKF:**
```
Actualizá el bundle OKF de este repo según GUIDE.md (paso "Mantenimiento").
```
(o, si instalaste el skill, simplemente trabajá normal y pedile que corra `okf-update`.)

---

## Qué hay acá

| Archivo | Para qué |
|---|---|
| **`GUIDE.md`** | **El procedimiento ejecutable.** Lo que un agente sigue para montar OKF en un repo. Empezá acá si sos un agente. |
| **`OKF-SPEC.md`** | La especificación del formato (reglas normativas), condensada y self-contained. |
| `reference/profiles.md` | Cómo organizar carpetas y `type:` por dominio (código / datos / wiki / mixto). El núcleo de la universalidad. |
| `reference/examples.md` | Mini-bundles de ejemplo completos, en los tres dominios, para copiar el estilo. |
| `reference/verification.md` | Cómo **testear** un bundle: conformidad (PASS/FAIL), calidad y el test de comportamiento en frío. |
| `reference/maintaining.md` | El ciclo de vida **después del init**: cómo el contexto se mantiene fresco y las capas de enforcement. |
| `reference/install-per-tool.md` | Cómo conectar OKF a **cualquier IA** (Claude/Cursor/Copilot/Gemini…) — punteros a `AGENTS.md`, sin lock-in. |
| `reference/special-cases.md` | Monorepos, migración desde contexto existente, escala (cuándo partir), e idioma. |
| `reference/optional-tools.md` | Aceleradores externos **opcionales** (Repomix): entender el repo al bootstrapear y medir el tamaño del bundle en tokens. |
| `templates/AGENTS.md` | Template del entrypoint universal. |
| `templates/CLAUDE.md` | Shim que apunta a AGENTS.md (evita duplicar). |
| `templates/knowledge/` | Templates de `index.md`, `log.md` y de cada tipo de concepto. |
| `templates/skills/okf-init/` | Skill de **arranque** (greenfield): bootstrapea OKF en un repo (la versión ejecutable del GUIDE). Instalalo global para disparar el "prompt mágico". |
| `templates/skills/okf-migrate/` | Skill de **migración** (brownfield): consolida contexto disperso existente (AGENTS.md/ADRs/docs) en un bundle OKF, sin duplicar. |
| `templates/skills/okf-update/` | Skill que se instala en el repo destino para mantener el bundle fresco. |
| `templates/skills/okf-verify/` | Skill que se instala en el repo destino para **testear** el bundle y emitir un reporte PASS/FAIL. |
| `templates/scripts/okf_lint.py` | Linter determinista (solo stdlib, sin `pip install`) que valida conformidad OKF. Ideal para CI; lo usa el skill `okf-verify`. |
| `templates/scripts/okf_coldtest.py` | Arma un entorno aislado (solo el bundle, sin código ni `.git`) para correr el test en frío del Nivel 3. Stdlib, sin install. |
| `templates/ci/okf.yml` | Workflow de GitHub Actions que corre el linter en cada push. **Cero tokens** (Python puro). Copialo a `.github/workflows/`. |
| `templates/hooks/pre-commit` | Git hook **universal** (cualquier IA/herramienta): bloquea commits no conformes y avisa si cambió código sin actualizar `knowledge/`. |
| `VERSION` | Revisión semver de **este kit** (no del formato). `okf-init` la estampa como `kit_version` en el bundle del repo. |
| `CHANGELOG.md` | Historial de revisiones del kit. Aclara `kit_version` (kit) vs `okf_version` (formato OKF). |
| `DEVELOPING.md` | Proceso interno para **desarrollar el kit**: el gate de release (selfcheck + cold-review de 4 lentes). |
| `scripts/okf_selfcheck.py` | Meta-linter de consistencia *interna* del kit (kit-only, NO se instala en repos destino). |
| `knowledge/` | Bundle **dogfood**: el kit documentándose en su propio formato OKF (prueba viva del init). |

---

## El modelo mental: tres capas

El contexto de un proyecto se parte en tres, y OKF es solo una de ellas:

| Capa | Vive en | Responde a | La lee… |
|---|---|---|---|
| **Entrypoint** | `AGENTS.md` (raíz del repo) | "¿Quién soy, qué reglas sigo, dónde está todo?" | Todo agente, al arrancar |
| **Conocimiento** | `knowledge/` (bundle OKF) | "¿Qué es esto y **por qué**?" | El agente, bajo demanda, vía `index.md` |
| **Procedimientos** | `.claude/skills/` (Claude) — o markdown **vendor-neutral** que cualquier IA sigue | "¿**Cómo** hago la tarea X?" | El agente, cuando la tarea matchea |

Las tres capas son **cross-vendor**: `AGENTS.md` es el estándar que toda herramienta lee
(o se la apunta), el bundle es markdown, y los procedimientos son markdown que funciona
como skill de Claude *o* se sigue directo. Cómo conectar tu IA: `reference/install-per-tool.md`.

La capa **Conocimiento** (`knowledge/`) es el corazón y siempre va. Las otras dos
son convenientes cuando un *agente de código* trabaja el repo; para una wiki o un
bundle de datos que se navega a mano, podés omitirlas y usar `knowledge/index.md`
como entrypoint. (Ver `GUIDE.md`, Paso 5.)

Hay una cuarta capa que es una trampa: la **memoria privada de la herramienta**
(ej. la memoria de Claude Code en `~/.claude/...`). Es útil pero NO es portable
ni vive en el repo. **La fuente de verdad debe ser el bundle OKF en git.** La
memoria de la herramienta queda como atajo personal con un puntero ("el contexto
vive en `knowledge/`").

---

## Por qué este diseño cumple "nunca perder contexto"

- **No perder nunca** → está en git: versionado, diffeable, con `log.md` de historial.
- **A la hora que sea** → es estado en disco, no depende de ningún backend ni sesión.
- **Con la IA que sea** → markdown + `AGENTS.md` es lo más cercano a un estándar cross-vendor.
- **Desde donde sea** → `git clone` y el contexto completo te sigue.
- **Sin reventar la ventana de contexto** → los `index.md` dan *progressive disclosure*:
  el agente ve el mapa y baja solo a lo que necesita.

---

## Crédito

OKF (Open Knowledge Format) es un formato abierto publicado por Google Cloud en
[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(`okf/SPEC.md`). Allá está pensado para catálogos de datos; acá lo generalizamos a
**contexto de cualquier proyecto — código, datos o wikis**, que el formato permite
explícitamente (el `type` no se registra en ningún lado y la jerarquía es
independiente del dominio).
