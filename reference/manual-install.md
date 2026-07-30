# Instalar el material del kit a mano (sin Python)

Este documento es el **camino manual** de los pasos **mecánicos** del init: crear la
estructura, los `index.md`, el `log.md`, el entrypoint y el tooling. Existe para un solo
caso: **la máquina no tiene Python 3.**

> **Si hay Python, no uses esto.** Un comando hace todo lo de acá, sellado y verificado:
> ```
> python3 scripts/okf_install.py <repo-destino> --profile <perfil> --name "<Proyecto>"
> ```
> (`--minimal` sin capa de futuro · `--no-claude` si no se usa Claude Code · `--dry-run` para
> ver el plan). Corre el linter sobre lo instalado y lista lo que falta. Por qué existe la
> división: [decisión 0017](../knowledge/decisions/0017-plomeria-determinista-vs-criterio.md).

Lo que **no** está acá es lo que requiere criterio —sembrar los conceptos y verificar—: eso
vive en `GUIDE.md` §4 y no lo hace ningún script.

---

### 1. Estructura

Creá el árbol `knowledge/` con las carpetas del **perfil elegido** (`GUIDE.md` §2). Empezá
mínimo (`index.md`, `log.md`, y las carpetas que vayas a llenar). No crees carpetas
vacías "por las dudas".

### 2. `index.md` (progressive disclosure)

Generá un `index.md` en la raíz del bundle y en cada subcarpeta. Convención
(detalle y ejemplos en `OKF-SPEC.md` §5):
- En la **raíz**: lista los subdirectorios bajo `# Subdirectories`, cada uno con su
  descripción. Si hay **conceptos en la raíz** (`roadmap.md`, un `glossary.md`), van
  **antes**, agrupados por `type` como en una hoja — si no, el linter los marca sin linkear.
- En las **hojas**: agrupá los conceptos bajo un heading por su `type`, cada
  entrada `* [Título](archivo.md) - <description del frontmatter>`.
- Links **relativos al archivo**. Sin frontmatter, salvo el `index.md` **raíz**, que
  lleva `okf_version` (formato) y `kit_version` (revisión del kit; estampala desde
  `VERSION`).

Esto es lo que deja a un agente navegar sin cargar todo el bundle.

### 3. `log.md` (opcional)

> Si partís del template `templates/knowledge/log.md`, reemplazá su `{{KIT_VERSION}}` en la
> línea de `Initialization` con el contenido de `VERSION` — igual que en el `index.md` raíz.

Si vas a llevar un log curado, inicializá `knowledge/log.md` con una entrada de hoy
(fecha ISO `YYYY-MM-DD`) marcando la creación del bundle (formato en `OKF-SPEC.md` §6).
**En un repo bajo git podés saltarlo:** el historial ya son `git log` + las `decisions/`.
Elegí uno; no dupliques ambos.

### 4. Entrypoint (adaptá a cómo se va a consumir el repo)

**Para instalar el nivel mínimo, el borrado es mecánico** (no interpretes prosa). Se hace
**sobre las copias ya en el repo destino**, nunca sobre los `templates/` del kit (`GUIDE.md` Paso 0): en
el `AGENTS.md` que copiaste, borrá todo lo que esté entre cada par de marcadores
`<!-- OKF:future-layer:start -->` / `<!-- OKF:future-layer:end -->` (4 bloques) y los
marcadores mismos; en su `knowledge/index.md`, borrá el bloque `# Roadmap`; y no
copies el skill `okf-plan` ni creés `roadmap.md`/`_changes/`. En el nivel **completo** solo
borrás las 8 líneas de marcadores.


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

### 5. Mantenimiento, testeo y enforcement

Si se usa Claude Code, copiá **tres** skills a `<repo>/.claude/skills/`:
- `templates/skills/okf-update/` → para que futuros agentes mantengan el bundle al día.
- `templates/skills/okf-verify/` → para testear el bundle (conformidad + calidad +
  test de comportamiento). Ver `reference/verification.md`.
- `templates/skills/okf-plan/` → para gestionar el rumbo y los cambios en curso
  (abrir/retomar/cerrar con harvest). Si omitiste la capa de futuro, saltealo.

Y el **revisor** a `<repo>/.claude/agents/`: `templates/agents/okf-reviewer.md` — audita el
bundle con contexto fresco, para que los Niveles 2 y 4 no los corra quien hizo el trabajo. Sin
Claude Code va a `docs/okf/okf-reviewer.md`, junto a los procedimientos.

Copiá también los scripts a `<repo>/scripts/`: **`okf_lint.py`** (chequeador de conformidad
determinista, solo stdlib, sin `pip install`, ideal para CI), **`okf_coldtest.py`** (arma el
entorno aislado para el test en frío del Nivel 3) y **`okf_stale.py`** (rankea dónde buscar
divergencia entre el bundle y el código, con git + frontmatter: no es un gate, es el paso 1
del Nivel 2). Sirven aunque no uses Claude Code.

**Si decidís NO instalar el linter**, ajustá la línea de §3 del `AGENTS.md` que manda correrlo:
si no, el contrato ordena un comando inexistente en cada turno.

Para correrlo en cada push, copiá **`templates/ci/okf.yml`** a
`<repo>/.github/workflows/okf.yml`. Es Python puro: **cero tokens, cero LLM** (el
test "en frío" del Nivel 3 sí usa tokens, así que ese NO va en CI — se corre manual).

Instalá el **git hook universal** `templates/hooks/pre-commit` (`cp` a
`.git/hooks/pre-commit` + `chmod +x`, o `git config core.hooksPath`): bloquea el commit si
el bundle no es conforme y avisa si cambió código sin tocar `knowledge/`. Corre con
**cualquier** IA, porque es a nivel git.

**Si no se usa Claude Code** (no hay skills que se auto-disparen), copiá igual los tres
procedimientos a `<repo>/docs/okf/` como docs legibles, **renombrando cada uno** (los tres
archivos fuente se llaman `SKILL.md`: si los copiás con `cp` a la misma carpeta, se pisan y
te quedás con uno solo, sin ningún error):

```
mkdir -p <repo>/docs/okf
cp templates/skills/okf-update/SKILL.md <repo>/docs/okf/okf-update.md
cp templates/skills/okf-verify/SKILL.md <repo>/docs/okf/okf-verify.md
cp templates/skills/okf-plan/SKILL.md   <repo>/docs/okf/okf-plan.md   # si instalaste la capa de futuro
```

**Van fuera de `knowledge/`**: traen su propio frontmatter (`name`/`description`, sin `type`),
así que adentro del bundle serían conceptos inválidos y harían fallar el linter, el hook y el
CI. Y **dejá el disparador en `AGENTS.md`** — que sí lee toda herramienta. Ese es el punto: el
contrato ya trae *cuándo* actuar (rumbo, cambio no trivial, harvest); el skill solo agrega el
*cómo* detallado. Sin skills el sistema funciona igual, apenas menos automático. El ciclo de
mantenimiento completo está en `reference/maintaining.md`; cómo conectar cada herramienta
(Cursor/Copilot/Gemini…), en `reference/install-per-tool.md`.

> **El usuario nunca tiene que nombrar un procedimiento.** Ni "okf-plan" ni "okf-update":
> habla en lenguaje natural ("quiero que haga X", "¿en qué estábamos?") y el agente
> reconoce el momento por el contrato. Si al instalar dejás algo que **exija** que el
> usuario recuerde un comando, el sistema se va a dejar de usar en dos semanas.

