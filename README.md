# okf-kit — que la IA deje de olvidarse tu proyecto

> 🇬🇧 **English speaker?** Start at [`README.en.md`](README.en.md) — install instructions and
> the mental model. The rest of the docs are in Spanish; any coding agent will translate or
> follow them as-is. · Licencia: **Apache-2.0** ([`LICENSE`](LICENSE), [`NOTICE`](NOTICE)).

**El problema.** Venís hace meses construyendo con una IA. Cada sesión arranca explicándole
el proyecto de nuevo; las decisiones que tomaron juntos —por qué la base de datos es esa, por
qué ese hack raro no se toca— viven en chats que ya se borraron. Y el día que el agente rompe
algo, no hay dónde mirar por qué estaba así.

**Qué hace este kit.** Deja en tu repo, en markdown y git, el contexto que la IA necesita:
el **por qué** de las decisiones (`decisions/`), un mapa del presente que se recorre en
segundos, y el trabajo en curso. Sin apps, sin servicios, sin `pip install`. Cualquier IA lo
lee, en cualquier máquina, sin que se lo expliques.

**Lo que no vas a encontrar en otro lado:** el kit **se mide a sí mismo**. Trae un harness
([`templates/eval/`](templates/eval/)) que corre preguntas reales contra tu repo, con y sin
la capa de contexto, y te dice en turnos y tokens si te está sirviendo. Importa: el
[estudio más grande sobre archivos de contexto](https://arxiv.org/abs/2602.11988) (SRI Lab,
ETH Zürich, 2026) midió que en general **no mejoran el acierto y cuestan >20% más** — y que
lo único que sí paga (+4%) es lo que un humano sabe y el código no dice: las decisiones, las
restricciones que no se ven leyendo, la configuración no obvia. Eso es exactamente lo que OKF
te ayuda a escribir, y el harness es para que no tengas que creerme.

> Esta guía es **self-contained**: markdown + git, sin depender de ningún servicio, SDK ni
> nube. Si podés `cat` un archivo, podés leerla; si podés `git clone`, la podés llevar.

**Aplicable a cualquier proyecto.** OKF es agnóstico al dominio. La misma mecánica
sirve para repos de **código**, proyectos de **datos/analytics** y **wikis / bases
de conocimiento**. Lo único que cambia entre ellos es el layout de carpetas y el
vocabulario de `type:` — eso se elige con un *perfil* (ver `reference/profiles.md`).

**Sin apps externas ni instalaciones.** No hace falta Obsidian, Notion, MkDocs, un
visor de grafos ni ningún servicio: es markdown + git. Un humano lo lee en GitHub o
con `cat`; un agente lo lee como archivos. **No hay nada que adoptar para *usar* el bundle.**

El kit trae además herramientas opcionales para que el contexto no se pudra solo —un linter,
un ranker de drift, un revisor con contexto fresco—, pero eso es plomería: **no es el motivo
por el que esto sirve**, y funciona sin ellas. Están en la tabla de abajo si te interesan.

---

## Cómo se instala

**Como plugin de Claude Code (el camino corto):**

```
/plugin marketplace add elgastipaa/okf-kit
/plugin install okf@okf-kit
```

Eso te deja dos caminos, y **el que probablemente necesitás es el segundo**:

- **`/okf:okf-migrate`** — *"mi `AGENTS.md` es un despelote"*, *"tengo docs por todos lados y
  no sé cuáles siguen vigentes"*. **Este es el caso normal**: un repo que ya viene
  conversando con una IA y acumuló contexto disperso. Consolida lo que ya tenés —separando lo
  vigente de lo que el código dejó atrás— en vez de agregar una capa más encima.
- **`/okf:okf-init`** — un repo **sin** contexto previo. Es el caso menos común.

Los comandos de un plugin llevan su prefijo. Igual no hace falta que los tipees: alcanza con
describir el síntoma en tu idioma y el skill correcto se dispara solo.

**Sin plugin, o con cualquier otra IA** — clonalo y usalo desde ahí. Si el repo ya tiene
contexto disperso, el camino es `okf-migrate` (el instalador **aborta** ante un `AGENTS.md`
escrito a mano, justamente para no pisártelo). Si está limpio:

```bash
git clone https://github.com/elgastipaa/okf-kit
python3 okf-kit/scripts/okf_install.py <tu-repo> --profile codigo --name "Tu Proyecto"
```

El instalador hace **todo lo mecánico** (esqueleto del bundle, el contrato `AGENTS.md`
recortado según el nivel, procedimientos, linter, CI, git hook), verifica su propia salida
con el linter y **te lista lo que falta** — que es la parte que requiere criterio: **sembrar
los conceptos**, el *por qué* que el código no dice. Esa parte la hacés con un agente.
Flags: `--minimal` (sin capa de futuro) · `--no-claude` (procedimientos a `docs/okf/`) ·
`--dry-run` · `--upgrade` (subir la maquinaria de un repo que ya tiene OKF, sin tocar su
bundle). Es stdlib puro, te lista todo lo que escribió, y **no pisa nada tuyo**: aborta ante
un `AGENTS.md`/`CLAUDE.md` escrito a mano (para ese repo está `okf-migrate`) y nunca toca un
`pre-commit` ajeno.

Para deshacerlo: lo que escribe es **nuevo y untracked**, así que `git checkout` no lo borra
—`git clean -nd` para ver qué se iría y `git clean -fd` para hacerlo— y el hook, que git no
versiona, se saca con `rm .git/hooks/pre-commit`. Corré primero el `-n`: `git clean` también
se lleva otros archivos tuyos sin trackear.

## Cómo se usa (los "prompts mágicos")

También podés citarle el kit a un agente en frío, sin instalar nada. Abrís un
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
| `OKF-SPEC.md` | La especificación del formato, para quien quiera implementarlo o escribir tooling. **Como usuario no la necesitás**: lo que recibís es una carpeta de markdown con frontmatter. |
| `reference/profiles.md` | Cómo organizar carpetas y `type:` por dominio (código / datos / wiki / mixto). El núcleo de la universalidad. |
| `reference/examples.md` | Mini-bundles de ejemplo completos, en los tres dominios, para copiar el estilo. |
| `reference/verification.md` | Cómo **testear** un bundle: conformidad (PASS/FAIL), calidad, el test de comportamiento en frío, y la auditoría de cumplimiento (¿el código respeta lo normativo?). |
| `reference/maintaining.md` | El ciclo de vida **después del init**: cómo el contexto se mantiene fresco y las capas de enforcement. |
| `reference/upgrading.md` | Subir un repo que ya tiene OKF a la revisión actual del kit. El bundle es tuyo y no se toca; lo que se reemplaza es el material instalado. |
| `reference/manual-install.md` | El camino **manual** de los pasos mecánicos del init. Solo si la máquina no tiene Python — con Python, `scripts/okf_install.py` los hace sellados y verificados. |
| `reference/install-per-tool.md` | Cómo conectar OKF a **cualquier IA** (Claude/Cursor/Copilot/Gemini…) — punteros a `AGENTS.md`, sin lock-in. |
| `reference/special-cases.md` | Monorepos, migración desde contexto existente, escala (cuándo partir), e idioma. |
| `reference/optional-tools.md` | Aceleradores externos **opcionales** (Repomix) para empaquetar el *código* del repo. Para el bundle no hace falta: `okf_lint.py --pack` lo hace sin dependencias. |
| `reference/spec-driven-interop.md` | En qué difiere OKF de las herramientas spec-driven (OpenSpec, Spec Kit, Kiro), qué se tomó de su filosofía y cómo convivir con ellas en el mismo repo. |
| `templates/AGENTS.md` | Template del entrypoint universal. |
| `templates/CLAUDE.md` | Shim que apunta a AGENTS.md (evita duplicar). |
| `templates/knowledge/` | Templates de `index.md`, `log.md` y de cada tipo de concepto. |
| `templates/skills/okf-init/` | Skill de **arranque** (greenfield): bootstrapea OKF en un repo (la versión ejecutable del GUIDE). Instalalo global para disparar el "prompt mágico". |
| `templates/skills/okf-migrate/` | Skill de **migración** (brownfield): consolida contexto disperso existente (AGENTS.md/ADRs/docs) en un bundle OKF, sin duplicar. |
| `templates/skills/okf-update/` | Skill que se instala en el repo destino para mantener el bundle fresco. |
| `templates/skills/okf-plan/` | Skill que se instala en el repo destino para gestionar la **capa de futuro**: el rumbo (`roadmap.md`) y los cambios en curso (`_changes/`, spec-driven liviano con harvest al cerrar). |
| `templates/skills/okf-verify/` | Skill que se instala en el repo destino para **testear** el bundle y emitir un reporte PASS/FAIL. |
| `templates/agents/okf-reviewer.md` | Subagente que audita el bundle con **contexto fresco** (Niveles 2 y 4): quien escribió un concepto no puede auditarlo. Se instala en el repo destino. |
| `templates/scripts/okf_lint.py` | Linter determinista (solo stdlib, sin `pip install`) que valida conformidad OKF. Ideal para CI; lo usa el skill `okf-verify`. |
| `templates/scripts/okf_coldtest.py` | Arma un entorno aislado (solo el bundle, sin código ni `.git`) para correr el test en frío del Nivel 3. Stdlib, sin install. |
| `templates/scripts/okf_stale.py` | Rankea **dónde buscar drift** entre el bundle y el código usando `resource:` + `timestamp` + git — sin leer código ni gastar tokens. No es un gate: es el paso 1 del Nivel 2 de verificación. |
| `templates/ci/okf.yml` | Workflow de GitHub Actions que corre el linter en cada push. **Cero tokens** (Python puro). Copialo a `.github/workflows/`. |
| `templates/eval/` | Harness **opcional** para medir el bundle contra un golden-set de preguntas (turnos, tokens, acierto). Sirve para comparar antes/después de un cambio de contexto; no se instala por defecto. |
| `templates/hooks/pre-commit` | Git hook **universal** (cualquier IA/herramienta): bloquea commits no conformes y avisa si cambió código sin actualizar `knowledge/`. |
| `README.en.md` | Puerta de entrada en **inglés**: qué es, cómo se instala, el modelo mental. |
| `LICENSE` / `NOTICE` | **Apache-2.0** (la misma que el OKF de Google Cloud, del que deriva `OKF-SPEC.md`) + el aviso de atribución. |
| `VERSION` | Revisión semver de **este kit** (no del formato). `okf-init` la estampa como `kit_version` en el bundle del repo. |
| `CHANGELOG.md` | Historial de revisiones del kit. Aclara `kit_version` (kit) vs `okf_version` (formato OKF). |
| `DEVELOPING.md` | Proceso interno para **desarrollar el kit**: el gate de release (selfcheck + cold-review de 4 lentes). |
| `scripts/okf_install.py` | **El instalador** (kit-only, stdlib): ejecuta todo lo mecánico del init/upgrade en un comando y verifica su salida con el linter. Lo que requiere criterio se lo deja al agente. |
| `.claude-plugin/` | Manifiestos de **plugin + marketplace** de Claude Code. El plugin *es* este repo (apunta a `templates/skills/`, no copia nada) y shippea solo el par de bootstrap. |
| `scripts/okf_selfcheck.py` | Meta-linter de consistencia *interna* del kit (kit-only, NO se instala en repos destino). |
| `scripts/okf_lint_test.py` | Verifica que el **linter** reporte cuando debe (y que no reporte ante redacción legítima). Kit-only. |
| `scripts/okf_selfcheck_test.py` | Verifica que el gate **falle cuando debe**: inyecta cada rotura sobre una copia del kit. Un assert sin su rotura probada es decoración. |
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
como entrypoint. (Ver `GUIDE.md` §1, "Cuánto instalar".)

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
- **Sin perder el rumbo** → el contexto cubre pasado (`decisions/`, log), presente (los
  conceptos) **y futuro**: el rumbo vigente en `roadmap.md` y cada cambio no trivial
  especificado en `_changes/` antes de codearse, cosechado al bundle al cerrarse (`okf-plan`).

---

## Crédito

El formato que usa por debajo se llama **OKF (Open Knowledge Format)**, y no necesitás
aprender la sigla para usar el kit: lo que te queda en el repo es markdown con frontmatter,
legible con `cat` y en GitHub. Es un formato abierto publicado por Google Cloud en
[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(`okf/SPEC.md`). Allá está pensado para catálogos de datos; acá lo generalizamos a
**contexto de cualquier proyecto — código, datos o wikis**, que el formato permite
explícitamente (el `type` no se registra en ningún lado y la jerarquía es
independiente del dominio).
