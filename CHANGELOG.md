# Changelog del kit OKF

Revisiones de **este kit de templates** (`coding/OKF`). Formato basado en
[Keep a Changelog](https://keepachangelog.com/); versionado semver.

> **`kit_version` ≠ `okf_version`.** `okf_version` (ej. `0.1`) es la versión del
> **formato** OKF, fijada por `OKF-SPEC.md`. `kit_version` (ej. `0.1.0`) es la
> revisión de **esta guía + templates + tooling**. `okf-init` estampa el
> `kit_version` con el que se inicializó un repo en el `index.md` raíz del bundle y
> en su `log.md`, para que el repo sepa de qué revisión nació. La fuente de verdad
> de la versión es el archivo `VERSION`.

## 0.4.3 — 2026-06-17

### Arreglado — pre-commit hook seguro + 2 falsos positivos
- **GRAVE (regresión de 0.4.1):** el hook usaba `git stash --keep-index` + `pop`, que con
  *partial-staging* (stagear parte de un archivo y seguir editándolo) **inyectaba marcadores
  de conflicto y corrompía el working-tree** — y no solo en `knowledge/`, en cualquier archivo.
  Ahora el hook copia el contenido **staged** de `knowledge/` a un tempdir con
  `git checkout-index` y lintea ahí: el working-tree **nunca se toca**. Valida lo mismo (lo
  que se commitea) sin riesgo.
- **Linter (falsos positivos sobre YAML válido):** se tolera un **BOM UTF-8** antes del `---`
  (editores Windows ya no disparan "falta frontmatter"); y una **clave entrecomillada** con `:`
  (`"a:b": 1`) ya no se marca como línea malformada.

## 0.4.2 — 2026-06-17

### Arreglado — gate **determinista** (cierra la divergencia que tapaba el techo)
- **Linter sin PyYAML:** el frontmatter ahora se valida con un **validador del subconjunto
  YAML en Python puro** que corre siempre. Se **removió PyYAML** del camino del veredicto →
  el PASS/FAIL **no depende de qué tengas instalado** (probado: con y sin `yaml` da output
  idéntico). Antes, un `:` sin comillas u otros YAML rotos eran ERROR con PyYAML y pasaban sin
  él → un dev podía commitear local lo que el CI rechazaba. El validador atrapa `:` sin comillas
  (medio y trailing), comillas/brackets sin cerrar, tabs y líneas malformadas. Quitado el
  `pip install pyyaml` del CI (ya innecesario).
- **Falso positivo del linter:** links absolutos dentro de **code-blocks indentados** (≥4
  espacios / tab) ya no se marcan como ERROR.

> Trade-off: el validador stdlib no cubre el 100% del YAML inválido teórico (eso es
> re-implementar PyYAML); lo que se le escape pasa **uniforme** (local == CI) — gap acotado,
> no divergencia. A cambio: gate determinista y **cero dependencias**.

## 0.4.1 — 2026-06-17

### Arreglado — el gate de conformidad, ahora determinista (re-review en frío)
- **PyYAML:** un valor de frontmatter con `:` sin comillas ahora es **ERROR en ambos modos**
  (antes: ERROR con PyYAML, WARN sin → veredicto opuesto). El CI (`okf.yml`) **pinea PyYAML**
  para que el gate autoritativo corra siempre el camino fuerte; docstring sincerado.
- **Pre-commit hook:** ahora linta **lo staged** (`git stash --keep-index` + `trap`), no el
  working-tree — cierra el falso positivo (bloquear un commit que no toca `knowledge/`) y el
  hueco de soundness (snapshot roto entrando a la historia).
- **`okf_selfcheck`:** nuevo assert — el `kit_version` del dogfood debe **coincidir con
  `VERSION`** (antes solo grepeaba presencia → dejó pasar un stamp stale). Dogfood re-estampado;
  semántica fijada (born-at en repos destino, current en el dogfood que el kit mantiene).
- **Linter:** el match "concepto no linkeado en su index" compara el path resuelto, no el
  basename → cierra un falso negativo.

## 0.4.0 — 2026-06-17

Resultado de una **revisión de 4 lentes en frío + dogfood** (el kit aplicado a sí mismo).

### Arreglado (correctness + trampas)
- **Linter (`okf_lint.py`):** ya no chequea links dentro de comentarios HTML ni de
  inline-code (eran falsos positivos — el kit fallaba su propio linter), ni escanea el
  frontmatter buscando links. Se cerró un **falso-negativo**: un ` ``` ` huérfano (p.ej.
  dentro de un comentario) silenciaba chequeos duros y dejaba pasar un link absoluto roto
  por lint/hook/CI. Nuevo **aviso** si un valor de frontmatter lleva `:` sin comillas (la
  trampa que rompía el YAML, env-dependiente).
- **`okf-verify`:** criterio de FAIL completo (enumeraba mal los ERRORs de frontmatter).
- `reference/examples.md` ahora incluye `kit_version` en el root index (antes enseñaba a omitirlo).

### Cambiado (single-source-of-truth, anti-deriva)
- Keep-alive con **una fuente canónica**: `AGENTS.md §2` + `okf-update` (idénticos);
  `GUIDE §5` y `maintaining.md` pasaron a punteros. `okf-update` ahora incluye la
  agrupación del index por `# {type}` y el orden correcto de frontmatter.
- Resuelta la contradicción SPEC-vs-GUIDE: `OKF-SPEC` sanciona `kit_version` (y otras
  claves del productor) en el root index. Gotcha del `:` documentado en SPEC §3.1; `profiles.md`
  apunta a las reglas de frontmatter (antes las omitía).

### Agregado (prevención)
- **`scripts/okf_selfcheck.py`** — meta-linter que valida la consistencia *interna* del kit
  (kit-only; no se instala en repos destino). `DEVELOPING.md` documenta el gate de release
  (selfcheck + cold-review de 4 lentes).
- Bundle **dogfood** `knowledge/` — el kit documentándose en su propio formato (pasa 0/0).

## 0.3.0 — 2026-06-17

### Agregado — capa de mantenimiento y universalidad cross-vendor
- **Contrato de trabajo en `AGENTS.md`**: el entrypoint pasó de índice a **contrato
  completo** (1. leé el contexto → 2. mantené el contexto vivo → 3. verificá antes de
  cerrar), con guardrails inline. Sirve a **cualquier IA** sin depender de skills.
- **`reference/maintaining.md`**: el ciclo de vida post-init (simétrico a `GUIDE.md`) y las
  capas de enforcement (contrato → skill → git hook → CI → cold test).
- **`templates/hooks/pre-commit`**: git hook **universal** — bloquea commits no conformes y
  avisa si cambió código sin tocar `knowledge/`. Corre con cualquier herramienta/IA (nivel git).
- **`reference/install-per-tool.md`**: cómo conectar OKF a Claude Code, Cursor, Copilot,
  Gemini y otras — todo punteros a `AGENTS.md`, sin lock-in.
- Los **skills** se reencuadran como **procedimientos vendor-neutral** (funcionan como skill
  de Claude *o* se siguen directo). El núcleo (contrato + git hook + CI + linter) no depende
  de Claude Code.

## 0.2.0 — 2026-06-17

### Agregado
- Integración **opcional** con [Repomix](https://github.com/yamadashy/repomix) (externo,
  Node/`npx`, **nunca requerido**), documentada en `reference/optional-tools.md`:
  - **Entender el repo** al bootstrapear/migrar empaquetándolo en un único archivo
    comprimido (acelera `okf-init`/`okf-migrate` y `GUIDE.md §3`; un gasto único al
    estructurar, después es mantenimiento incremental).
  - **Token-sizer** del bundle para detectar `index.md`/conceptos demasiado grandes
    (smell de Nivel 2 en `verification.md`) y decidir cuándo partir (`special-cases.md`).
  - Aclaración: Repomix **no consume tokens de LLM** (es un tokenizador local).

## 0.1.0 — 2026-06-17

Primera versión versionada del kit. Contenido:

- **Formato**: `OKF-SPEC.md` (spec condensada y self-contained, OKF v0.1), con la
  convención de **cross-links relativos al archivo** (funcionan en GitHub sin tooling).
- **Guía**: `GUIDE.md` (procedimiento de bootstrap, perfil → siembra → índices →
  verificación) y `README.md`.
- **Universalidad**: `reference/profiles.md` (perfiles código / datos / wiki /
  mixto), `reference/examples.md` (ejemplos en los tres dominios),
  `reference/special-cases.md` (monorepos, migración, escala, idioma).
- **Testeo**: `reference/verification.md` (3 niveles), el linter determinista
  `templates/scripts/okf_lint.py` (solo stdlib, sin `pip install`) y
  `templates/scripts/okf_coldtest.py` (entorno aislado para el test en frío).
- **Skills**: `okf-init` (bootstrap), `okf-update` (mantenimiento), `okf-verify`
  (testeo), `okf-migrate` (migración brownfield).
- **Templates**: `AGENTS.md`/`CLAUDE.md` (entrypoint), `knowledge/` (index, log,
  conceptos), y `ci/okf.yml` (GitHub Action que corre el linter por push, cero tokens).

Sin dependencias externas ni `pip install`; cero apps (Obsidian, etc.) requeridas.
