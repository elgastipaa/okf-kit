# OKF Bootstrap Guide

**Audiencia: un agente (Claude Code u otro) que tiene que montar un sistema de
contexto OKF en un repositorio.** Si sos ese agente, leé esto entero antes de
escribir nada, después seguí el procedimiento.

**Sin instalaciones ni apps externas.** OKF es markdown + git: no dependés de
Obsidian, de un visor de grafos, ni de la nube. El kit incluye un linter Python
opcional (`okf_lint.py`) para chequeos deterministas y CI — **solo stdlib, sin
`pip install`**. No hay nada que adoptar para *usar* el bundle.

Documentos hermanos que vas a necesitar:
- `OKF-SPEC.md` — las reglas del formato. Respetalas.
- `reference/profiles.md` — cómo organizar carpetas y qué poner en `type:`, según
  el dominio (código / datos / wiki / mixto). **Leelo: define la universalidad.**
- `reference/examples.md` — bundles de ejemplo bien hechos, en los tres dominios.
- `reference/special-cases.md` — monorepos, migración desde contexto existente, y escala.
- `reference/verification.md` — cómo testear el bundle (lo usás en el Paso 7).
- `reference/maintaining.md` — el ciclo de vida DESPUÉS del init (cómo no perder frescura).
- `reference/install-per-tool.md` — conectar OKF a cualquier IA (Claude/Cursor/Copilot/Gemini).
- `templates/` — archivos para copiar y completar.

---

## 1. Qué vas a construir

Hasta tres capas de contexto en el repo destino:

```
<repo>/
├── AGENTS.md            # Entrypoint para agentes (OPCIONAL — ver Paso 3)
├── CLAUDE.md            # Shim de 1 línea → @AGENTS.md (si usás Claude Code)
├── .claude/skills/      # Procedimientos como skills (OPCIONAL, tool-específico)
│   └── okf-update/
└── knowledge/           # El bundle OKF — el "qué/por qué". SIEMPRE.
    ├── index.md         # mapa raíz (progressive disclosure)
    ├── log.md           # historial de cambios de contexto
    └── <carpetas según el perfil>/
```

El **bundle `knowledge/` es el corazón y es obligatorio**. Las otras dos capas
(`AGENTS.md` y los skills) son convenientes cuando un *agente de código* va a
trabajar el repo; para una wiki pura o un bundle de datos que humanos navegan,
podés omitirlas y dejar que el entrypoint sea `knowledge/index.md` (ver Paso 3).

Las carpetas dentro de `knowledge/` **dependen del perfil** del proyecto. No las
asumas: elegilas en §2 (Elegí el perfil).

---

## 2. Elegí el perfil

Antes que nada, decidí qué clase de proyecto es, porque eso define el layout y el
vocabulario de `type`. Abrí **`reference/profiles.md`** y elegí:

- **Código / Software** — apps, librerías, servicios.
- **Datos / Analytics** — datasets, warehouses, pipelines.
- **Wiki / Base de conocimiento** — docs, manuales, notas (el contenido *es* el producto).
- **Genérico / Mixto** — combiná perfiles o inventá carpetas/tipos si nada encaja.

Para **monorepos**, **migrar desde un `AGENTS.md`/ADRs existentes**, o decidir
**cuándo partir un bundle** que creció, ver `reference/special-cases.md`.

No tiene que ser puro: un repo de código que también documenta su dataset combina
el perfil Código con carpetas del perfil Datos. Anotá el perfil elegido; lo vas a
usar en los Pasos 1 y 2 del Procedimiento. (Si dudás del tipo, mirá primero §3
"entendé el repo" y volvé.)

---

## 3. Antes de tocar nada: entendé el repo

No inventes. Primero **investigá** el repo destino:

1. **Estructura y stack** — leé el árbol de directorios y los manifiestos
   (`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml`…), o, si es una
   wiki/datos, qué tipo de contenido contiene.
2. **Docs existentes** — `README.md`, `CONTRIBUTING.md`, `/docs`, ADRs si hay.
3. **Contexto de IA ya presente** — `AGENTS.md`, `CLAUDE.md`, `.cursorrules`,
   `GEMINI.md`, `.github/copilot-instructions.md`. Si existen, **harvesteá** su
   contenido hacia el bundle en vez de duplicarlo, y dejá `AGENTS.md` como fuente.
   Si hay mucho contexto disperso, el skill `okf-migrate` automatiza esa consolidación.
4. **Historia** — `git log --oneline -30` y los nombres de branches dan pistas de
   qué se está construyendo y qué decisiones se tomaron.
5. **Memoria de la herramienta** — si hay una memoria de Claude Code u otra
   (`~/.claude/.../MEMORY.md` u archivos linkeados), leela: ahí suele estar el
   conocimiento tribal (decisiones, quirks, workflows) que más conviene migrar
   al bundle para que sea portable.

> **Regla de oro de esta fase:** lo que no puedas deducir de la fuente —el *por qué*
> de una decisión, una convención no escrita, un workflow operativo, el grano de
> una tabla— **preguntáselo al usuario.** No lo inventes. El valor de OKF está
> justamente en capturar lo que la fuente no dice.

> **Opcional (repos grandes):** en vez de caminar todo a mano, empaquetá el codebase
> con Repomix y leé ese único archivo comprimido — ver `reference/optional-tools.md`
> (uso 1). Repomix corre local y no consume tokens de LLM.

---

## 4. Procedimiento

### Paso 1 — Estructura

Creá el árbol `knowledge/` con las carpetas del **perfil elegido** (§2). Empezá
mínimo (`index.md`, `log.md`, y las carpetas que vayas a llenar). No crees carpetas
vacías "por las dudas".

### Paso 2 — Sembrá el bundle (lo más importante)

Escribí los conceptos iniciales como archivos OKF (formato exacto en `OKF-SPEC.md`
§3; tipos y carpetas por perfil en `reference/profiles.md`). **Qué priorizar según
el perfil:**

- **Código:** `architecture/overview.md` (el mapa) → `decisions/` (los *por qué*
  no obvios, ADRs numerados) → `domain/` → `schema/` → `runbooks/` → `references/`.
- **Datos:** `datasets/` y `tables/` (con `# Schema` y `# Common query patterns`)
  → `references/metrics/` y `references/joins/` → `glossary/`.
- **Wiki:** los `<temas>/` principales primero → `playbooks/` → `glossary`.

Reglas al escribir conceptos (todos los perfiles):
- **Capturá el *por qué*, no el *qué*.** Si algo se deduce de la fuente, no lo
  copies — **linkealo** (con `resource` o un cross-link). El bundle documenta lo
  que la fuente no dice.
- **No dupliques.** Una verdad, un archivo. Si dos conceptos comparten algo, uno
  linkea al otro.
- **Cross-linkeá liberalmente** con links **relativos al archivo** (`../otra/x.md`,
  `./y.md`) — funcionan en GitHub y en cualquier visor, sin herramientas. Nunca
  empieces un link con `/`. Detalle en `OKF-SPEC.md` §4.
- **`type:` del vocabulario** de `reference/profiles.md` (núcleo universal + perfil).
- **Frontmatter por defecto:** `type` + `title` + `description` (una sola frase) +
  `timestamp` + `tags`; `resource` cuando apunta a un activo real.

**Glosario de dominio (opcional, alto ROI en código grande/ambiguo con jerga).** Las
preguntas a nivel *término* ("¿qué es ATK?", "¿qué es el Vigor?") son las que más caro le
salen a un agente: sin un mapa término→página, fanea al código a reconstruir el dato. Un
`glossary.md` (template `_glossary.md`) que rutea cada término a su **página canónica** y a su
**code-of-record** (el archivo donde vive el *valor* exacto, p.ej. una tabla de tuning)
colapsa esas preguntas de muchos turnos a ~1 — medido ~−60% de turnos en un repo de juego
(ver `knowledge/decisions/0007`). Son **punteros, no fuente de verdad**: una línea por
término, sin copiar el valor (linkealo). **El ROI escala con el tamaño/ambigüedad del
código** (repos grandes, forked, con sistemas v1/v2 coexistiendo); en repos chicos y bien
nombrados rinde poco — no lo agregues por reflejo. Para que se use, ruteá hacia él desde el
`index.md` y desde el entrypoint (ver Paso 5).

**Capas no-autoritativas (alto ROI en repos ruidosos/legacy).** Si el repo arrastra `notes/`,
docs de refactors viejos o mockups que ya no reflejan el estado, **declaralos como
no-autoritativos en el entrypoint** (sección en `templates/AGENTS.md`): qué dirs son scratch y
que *gana el código*. Sin esa señal, un agente gasta turnos reconciliando basura — medido en
una pregunta de auditoría que cayó de 27 a 2 turnos al declararla (ver `knowledge/decisions/0008`).

> **Sobre los templates `templates/knowledge/_*.md`:** son plantillas de referencia,
> NO conceptos — el linter las ignora por el prefijo `_`. Cuando crees un concepto a
> partir de una, copiá su contenido a un archivo **sin** el `_` (p.ej. `0001-x.md`) y
> **borrá el comentario HTML del encabezado**: el archivo debe **empezar con `---`**,
> o no es un concepto OKF válido (el linter daría `ERROR — falta frontmatter`).

### Paso 3 — `index.md` (progressive disclosure)

Generá un `index.md` en la raíz del bundle y en cada subcarpeta. Convención
(detalle y ejemplos en `OKF-SPEC.md` §5):
- En la **raíz**: lista los subdirectorios bajo `# Subdirectories`, cada uno con su
  descripción.
- En las **hojas**: agrupá los conceptos bajo un heading por su `type`, cada
  entrada `* [Título](archivo.md) - <description del frontmatter>`.
- Links **relativos al archivo**. Sin frontmatter, salvo el `index.md` **raíz**, que
  lleva `okf_version` (formato) y `kit_version` (revisión del kit; estampala desde
  `VERSION`).

Esto es lo que deja a un agente navegar sin cargar todo el bundle.

### Paso 4 — `log.md` (opcional)

Si vas a llevar un log curado, inicializá `knowledge/log.md` con una entrada de hoy
(fecha ISO `YYYY-MM-DD`) marcando la creación del bundle (formato en `OKF-SPEC.md` §6).
**En un repo bajo git podés saltarlo:** el historial ya son `git log` + las `decisions/`.
Elegí uno; no dupliques ambos.

### Paso 5 — Entrypoint (adaptá a cómo se va a consumir el repo)

- **Si un agente de código va a trabajar el repo** (caso típico de perfil Código):
  copiá `templates/AGENTS.md` a la raíz y completá los placeholders. Mantenelo
  **chico** — es un índice: qué es el proyecto, las reglas duras, y "el contexto
  vive en `knowledge/`, empezá por `knowledge/index.md`". Copiá también
  `templates/CLAUDE.md` (un shim `@AGENTS.md`) si se usa Claude Code; para otra
  herramienta, hacé el equivalente (symlink o puntero de una línea).
- **Si es una wiki o un bundle de datos que humanos/otros agentes navegan**:
  `AGENTS.md` es opcional. El entrypoint natural es `knowledge/index.md`; agregá un
  puntero de una línea en el `README.md` del repo ("el conocimiento vive en
  `knowledge/`").

### Paso 6 — Mantenimiento, testeo y enforcement

Si se usa Claude Code, copiá **dos** skills a `<repo>/.claude/skills/`:
- `templates/skills/okf-update/` → para que futuros agentes mantengan el bundle al día.
- `templates/skills/okf-verify/` → para testear el bundle (conformidad + calidad +
  test de comportamiento). Ver `reference/verification.md`.

Copiá también los scripts a `<repo>/scripts/`: **`templates/scripts/okf_lint.py`**
(chequeador de conformidad determinista, solo stdlib, sin `pip install`, ideal para
CI) y **`templates/scripts/okf_coldtest.py`** (arma el entorno aislado para el test
en frío del Nivel 3). Sirven aunque no uses Claude Code.

Para correrlo en cada push, copiá **`templates/ci/okf.yml`** a
`<repo>/.github/workflows/okf.yml`. Es Python puro: **cero tokens, cero LLM** (el
test "en frío" del Nivel 3 sí usa tokens, así que ese NO va en CI — se corre manual).

Instalá el **git hook universal** `templates/hooks/pre-commit` (`cp` a
`.git/hooks/pre-commit` + `chmod +x`, o `git config core.hooksPath`): bloquea el commit si
el bundle no es conforme y avisa si cambió código sin tocar `knowledge/`. Corre con
**cualquier** IA, porque es a nivel git.

Si no se usa Claude Code, dejá ambos procedimientos como `runbooks/` dentro del
bundle, o seguí §5 de esta guía y `reference/verification.md` a mano (el script
`okf_lint.py` igual corre). El ciclo de mantenimiento completo está en
`reference/maintaining.md`; cómo conectar cada herramienta (Cursor/Copilot/Gemini…), en
`reference/install-per-tool.md`.

### Paso 7 — Verificá (testeá el resultado)

Seguí **`reference/verification.md`** (o corré el skill `okf-verify`). Son tres
niveles:
1. **Conformidad** (objetivo, PASS/FAIL): corré `python3 scripts/okf_lint.py knowledge`
   — chequea frontmatter + `type` en cada concepto, reservados, links **relativos**
   que resuelven, índices que coinciden con los archivos, carpetas vacías. Exit 1 = falla.
   *(¿Sin Python? El agente hace este mismo nivel leyendo, vía `okf-verify` — no se
   necesita Python para nada más.)*
2. **Calidad** (smells): que capture el *por qué* y no duplique el código, que esté
   cross-linkeado, que los índices sean chicos (progressive disclosure real).
3. **Outcome** (la prueba de fuego): generá 5-10 preguntas que haría un recién
   llegado + una trampa, y pasáselas a un agente **en frío con acceso solo a
   `knowledge/`**. Si responde ≥80% citando archivos y admite la trampa, pasa.

Mostrale al usuario el reporte (formato en `reference/verification.md`), el árbol
final, el perfil elegido, qué conceptos sembraste, y **qué te faltó por no tener la
info** (para que él lo complete o te lo dicte). Cada fallo del nivel 3 es un concepto
faltante → `okf-update`.

---

## 5. Mantenimiento (cómo NO perder contexto con el tiempo)

El bundle solo sirve si se mantiene vivo. **El procedimiento canónico es el contrato del
`AGENTS.md` (§2) que se instala en el repo, y el skill `okf-update`** — ambos con los
mismos pasos: elegir carpeta por tipo → frontmatter → actualizar el `index.md` de la
carpeta (hoja: por `# {type}`) y `knowledge/log.md`. El ciclo de vida completo y las capas
de enforcement, en `reference/maintaining.md`.

**Cuándo** actualizar: ante una **decisión** no trivial, un cambio de **arquitectura/schema**,
un **gotcha**, un cambio de **runbook**, o algo que te explican y "ya deberías saber". No
documentes todo de una: el bundle crece orgánico, una pieza por vez.

---

## 6. Principios (no negociables)

1. **Sin instalaciones ni apps externas.** Markdown + git. El único extra es un
   linter Python opcional (stdlib-only, sin `pip install`) para CI. Nada que adoptar
   ni que ate a un vendor para *usar* el bundle.
2. **Progressive disclosure.** El entrypoint y los `index.md` son chicos; el detalle
   vive en los conceptos, que se cargan bajo demanda.
3. **No dupliques.** Si está en la fuente, linkealo, no lo copies. Una verdad, un lugar.
4. **Capturá el *por qué*.** La fuente ya dice el *qué*.
5. **Links relativos al archivo.** Para que funcionen en GitHub y en cualquier visor.
6. **Si no sabés, preguntá.** No inventes decisiones ni razones.
7. **Consumo permisivo.** Campos opcionales faltantes, `type` desconocidos y links
   rotos NO invalidan el bundle. Sé prolijo al escribir; tolerante al leer.
