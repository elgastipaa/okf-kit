# Changelog del kit OKF

Revisiones de **este kit de templates** (`okf-kit`). Formato basado en
[Keep a Changelog](https://keepachangelog.com/); versionado semver.

> **`kit_version` ≠ `okf_version`.** `okf_version` (ej. `0.1`) es la versión del
> **formato** OKF, fijada por `OKF-SPEC.md`. `kit_version` (ej. `0.1.0`) es la
> revisión de **esta guía + templates + tooling**. `okf-init` estampa el
> `kit_version` con el que se inicializó un repo en el `index.md` raíz del bundle y
> en su `log.md`, para que el repo sepa de qué revisión nació. La fuente de verdad
> de la versión es el archivo `VERSION`.

## 0.6.0 — 2026-07-26

### Agregado — la capa de FUTURO (rumbo + cambios con harvest)
Hasta acá el kit ordenaba el pasado (`decisions/`, log) y el presente (los conceptos),
pero excluía el trabajo futuro — el nicho de spec-driven development (OpenSpec y
similares), y justo lo que un proyecto "vibecodeado" más necesita para no perder el
rumbo. Se incorpora una versión liviana y nativa, sin tooling nuevo:

- **`knowledge/roadmap.md`** (template `_roadmap.md`, `type: Roadmap` en el núcleo
  universal de `profiles.md`): la **intención vigente** — visión, "Ahora", "Después",
  no-goals. Es un concepto normal (estado presente *de la intención*); se edita, sin
  checkboxes.
- **`knowledge/_changes/NNNN-<slug>.md`** (template `_change.md`): un doc **efímero por
  cambio no trivial** — mini-spec (por qué, resultado esperado, fuera de alcance),
  tareas con checkboxes, decisiones staging. El linter lo ignora (prefijo `_` ya
  existente); nace antes de codear y **muere en un harvest** al bundle, tras lo cual se
  borra (git guarda la historia).
- **Skill `okf-plan`** (vendor-neutral, se instala en el repo destino): los cinco
  disparadores (primer mensaje de la sesión / pedido de cambio / "¿qué sigue?" / cierre con
  harvest / idea fuera de alcance → "Después"), el umbral de trivialidad, el límite de ~3
  cambios activos y las reglas anti-zombie.
- **Spec §3.4 aclarada** (resolvía una tensión previa): la intención vigente (roadmap)
  SÍ es estado presente y puede ser concepto; el plan/progreso de un cambio concreto NO
  — vive en `_changes/`. §2 suma `_changes/` a los ejemplos de prefijo `_`.
- Integrado en el resto del sistema: `GUIDE.md` (árbol, siembra del roadmap preguntando
  al usuario, tercer skill en el Paso 6), `templates/AGENTS.md` (rumbo/en-curso en §1,
  harvest en §3, `okf-plan` en Procedimientos), `okf-init`/`okf-migrate` (los TODOs y
  roadmaps existentes se triagean hacia la capa) /`okf-update` (puntero), `maintaining.md`
  (señal anti-rot: cambios zombie), README.
- **`okf_selfcheck.py`**: nuevos asserts de consistencia — contrato, skill `okf-plan` y
  template `_change.md` describen la misma capa (rumbo + `_changes/` + harvest), y el kit
  **se auto-aplica** la capa (su `AGENTS.md` rutea a `roadmap.md`/`_changes/` y el dogfood
  tiene su roadmap).
- Dogfood: decisión `0011-future-work-layer` + `knowledge/roadmap.md` + el primer cambio
  real del kit en `knowledge/_changes/` (validar la capa midiendo en los conejillos del
  eval — criterio reactivo de la 0010).

### Agregado — cosechado de la comparación con OpenSpec (spec-driven development)
Se revisó [OpenSpec](https://github.com/Fission-AI/OpenSpec) para ver qué de su filosofía
aplicaba. Se tomaron **cinco ideas** —enumeradas como tales en
`reference/spec-driven-interop.md`— sin tomar la herramienta ni su ceremonia. Lo que
cambiaron en el kit:

- **`reference/spec-driven-interop.md`** (nuevo): en qué difiere OKF de las herramientas
  SDD, qué se adoptó, qué se descartó a propósito (deltas `ADDED/MODIFIED/REMOVED`,
  `changes/archive/`, specs vivas por capability) y **cómo convivir** con OpenSpec en el
  mismo repo sin montar dos dueños del trabajo en curso.
- **Descriptivo vs normativo** (decisión `0012`, y el gap más importante que destapó la
  comparación): "gana el código" aplica a los conceptos; el *Resultado esperado* de un
  cambio **activo** es normativo — si el código no lo cumple, el trabajo no está terminado,
  y bajar la vara se renegocia con el usuario, no se asume. La autoridad caduca en el
  harvest. Reflejado en `OKF-SPEC.md` §3.5, `templates/AGENTS.md` y `okf-plan`.
- **Escenarios `CUANDO … ENTONCES …`** en el "Resultado esperado" del template `_change.md`
  (incluyendo el caso que falla), para que "hecho" sea chequeable en vez de opinable.
- **Explorar antes de comprometer** y **right-sizing** del cambio (una intención que se dice
  en una frase, + señales de cambio sobredimensionado) en `okf-plan`.
- **No planificar de más:** specs de trabajo hipotético se pudren porque nada las obliga a
  seguir la realidad — el trabajo no arrancado es *una línea* en "Después" del roadmap, no
  una spec (`okf-plan`, `GUIDE.md`).

### Cambiado — el disparo es automático: el usuario nunca nombra un procedimiento
El riesgo de adopción más serio de la capa de futuro era que dependiera de que el usuario
recordara pedir "okf-plan" — con el público objetivo (gente que desarrolla conversando, no
ingenieros), eso equivale a que no se use. Los **disparadores se movieron al `AGENTS.md`**,
que lee toda herramienta, en vez de vivir solo en el skill (que solo existe en Claude Code):

- El contrato ahora lista **cuándo actuar sin que se lo pidan**: primer mensaje de la sesión
  (continuidad: "venías con X, quedó en Y"), pedido no trivial (acordar el "listo" antes de
  codear), pregunta de rumbo, cierre con harvest, idea fuera de alcance → "Después".
- **Regla nueva "hablale al usuario en su idioma, no en OKF"** (contrato y `okf-plan`): no
  anunciar archivos ni metodologías, preguntar en concreto ("¿cómo te das cuenta de que
  quedó bien?"), una o dos preguntas y no un cuestionario, y **respetar** al usuario que
  pide ir directo al código. La metodología tiene que ser invisible.
- `okf-plan` suma el disparador 0 (primer mensaje de sesión) y una sección de cómo
  conversarlo; `GUIDE.md` e `install-per-tool.md` aclaran que **sin skills el sistema sigue
  funcionando** (el contrato trae el *cuándo*; el skill solo agrega el *cómo*).
- El template `AGENTS.md` avisa qué secciones borrar si no se instaló la capa de futuro o el
  linter (evita mandar al agente a archivos que no existen).

### Agregado — presupuesto del contrato y niveles de instalación
`AGENTS.md` es lo único que se carga en **cada turno de cada sesión**, así que su tamaño es
el costo permanente del sistema (y un contrato largo se skimea: pierde obediencia). Al medirlo
se detectó que las adiciones de esta versión lo habían inflado ~66%; se recortó sin perder
comportamiento y se cableó el límite:

- Contrato **instalado**: ~1600 tokens (era ~1178 antes de esta versión; llegó a ~2260 antes
  del recorte; el valor exacto lo imprime el `okf_selfcheck`, no se transcribe a mano). El
  delta paga la regla normativa, los disparadores del rumbo y la regla de hablarle al
  usuario en su idioma.
- **`okf_selfcheck.py`**: assert nuevo de **presupuesto** — el contrato instalado no puede
  superar los 7000 chars. "Mantenelo chico" pasó de consejo a chequeo.
- **Dos niveles de instalación** documentados en `GUIDE.md` §1: **completo** (~1600 tokens,
  con capa de futuro) y **mínimo** (~1300, sin ella — pasado + presente, sin ceremonia previa
  a codear), con instrucciones de qué borrar y cómo subir de uno a otro después.
- **`reference/install-per-tool.md`**: tabla de **qué tan fuerte es cada garantía** (instrucción =
  default fuerte y dependiente del vendor; git hook + CI y auditoría = independientes del
  vendor), con el corolario "si te importa que no se pierda, no lo dejes solo en la capa de
  instrucción"; más un **canario** de una pregunta para comprobar si una herramienta nueva
  está leyendo el contrato.

### Cambiado — la autoridad frente al código ahora depende del tipo de documento
El agujero que destapó la comparación era más grande que la capa de futuro y tocaba el
corazón del bundle: bajo "gana el código" sin tipos, **código que viola un ADR aceptado
convertía al ADR en el bug** — o sea, el kit instruía a borrar en silencio la razón por la
que alguien decidió algo. Corregido:

- **`OKF-SPEC.md` §3.5** (nueva, fuente canónica): dos clases de documento y en qué
  dirección corre la autoridad. **Descriptivo** (default: arquitectura, schema, dominio,
  runbooks, references, glosario) → gana el código. **Normativo** (`Decision` con
  `status: accepted`, `Convention`, `Roadmap`, `Change` activo) → el código que difiere está
  **en violación**. Ante una violación hay dos salidas y ninguna tercera: **arreglar el
  código** o **superseder** la decisión; editar el documento para emparejarlo está prohibido.
  Dos límites evitan reintroducir drift: lo normativo nunca responde "¿qué hace el código
  hoy?", y la autoridad de un trabajo en curso caduca en el harvest.
- **`authority: normative | descriptive`**: clave de frontmatter **opcional** (§3.1) para
  cuando el `type` no lo deja claro; el default se deduce del tipo
  (tabla nueva en `reference/profiles.md`).
- **Nivel 4 de verificación — Cumplimiento** (opcional, periódico) en
  `reference/verification.md` y `okf-verify`: auditar el **código contra lo normativo**
  (violación / decisión obsoleta / decisión ambigua). Es auditoría con criterio, no script:
  no va en CI. Hasta acá el kit solo cubría el drift del doc que envejece; ahora también el
  del **código que se desvía de lo decidido**.
- `templates/knowledge/_decision.md` invita a declarar **cómo verificar** la decisión
  (comando/grep/test) — una decisión chequeable es la que sobrevive.
- Propagado con **punteros** a §3.5 desde `reference/maintaining.md`,
  `reference/verification.md`, `reference/spec-driven-interop.md`, `reference/profiles.md`,
  `templates/knowledge/_decision.md`, `GUIDE.md` y el `AGENTS.md` del propio kit. El material
  que se **instala** (`templates/AGENTS.md`, `okf-update`, `okf-verify`) enuncia la regla en
  vez de apuntar, a propósito: el repo destino no recibe `OKF-SPEC.md`, y un puntero a un
  archivo inexistente es peor que una copia. El `okf_selfcheck` vigila que esas copias no
  pierdan la rama normativa.
- **`okf_selfcheck.py`**: assert nuevo — la rama normativa no puede caerse del contrato, de
  `okf-update` ni de `okf-verify`, y el `GUIDE` tiene que enseñar la regla (es el tipo de
  regla que ya derivó históricamente en este kit).
- Dogfood: la decisión `0012` se generalizó a la regla tipada completa.

### Arreglado — lo que encontró el cold-review de 4 lentes (gate de release)
Antes de publicar el minor corrió el gate de `DEVELOPING.md` §3: cuatro revisores en frío e
independientes (consistencia / completitud / correctness ejecutando el tooling / dogfood
siguiendo el `GUIDE` sobre un repo de juguete). Encontraron 2 blockers y ~12 majors, **ninguno
en el diseño**: todos en la capa de propagación e instalación. El patrón común es uno solo —
**el material instalado suponía que `okf-kit` seguía en disco**:

- **El camino "no uso Claude Code" rompía el linter.** El `GUIDE` mandaba copiar los tres
  `SKILL.md` a `knowledge/runbooks/`; traen frontmatter sin `type`, así que adentro del bundle
  son conceptos inválidos → 3 ERROR, hook bloqueando cada commit y CI en rojo, para la mayoría
  de los usuarios. Ahora van a `docs/okf/`, fuera del bundle.
- **La instalación mínima dejaba el contrato roto.** La instrucción "borrá lo que no
  instalaste" era prosa y enumeraba 2 lugares; la capa de futuro aparecía en 3, y la garantía
  "si te pide ir directo al código, respetalo" vivía **dentro** del bloque a borrar. Ahora el
  borrado es **mecánico**: 3 pares de marcadores `OKF:future-layer:start/end` en el template,
  y dos asserts nuevos (marcadores balanceados; la versión mínima no puede mencionar
  `_changes/`, `okf-plan` ni `roadmap.md`). Medido: completo ≈1590 tokens/turno, mínimo ≈1300.
- **Autosuficiencia del material instalado.** `okf-plan` mandaba crear el roadmap y los
  cambios "desde el template `templates/knowledge/_change.md`", `okf-verify` había perdido su
  hedge y citaba `reference/verification.md` para el formato del reporte, y el contrato
  apuntaba a `reference/maintaining.md` e `install-per-tool.md`. Todo eso se **inlineó** (los
  esqueletos de `_roadmap.md`/`_change.md` viven ahora en `okf-plan`; el formato del reporte,
  en `okf-verify`), y un assert nuevo prohíbe que el material instalado cite rutas del kit.
- **La regla del `index.md` raíz decía una cosa y el kit hacía otra.** Cinco archivos
  afirmaban "la raíz solo lista subdirectorios" mientras el template y el dogfood ponen
  `roadmap.md` ahí: todo repo que instalara la capa siguiendo el `GUIDE` arrancaba con un WARN.
  Corregido en el canónico (`OKF-SPEC.md` §5) y en las siete copias que la repetían.
- **El alcance de lo normativo tenía tres versiones.** §3.5 no incluía el `Roadmap`,
  `profiles.md` sí, y `verification.md` sumaba "las reglas duras del `AGENTS.md`". Peor: §3.5
  listaba "dominio" como descriptivo mientras `profiles.md` ubica `Convention` (normativo) en
  `domain/` — respuestas opuestas para el mismo archivo. §3.5 es ahora la fuente única: **la
  clase la da el `type`, no la carpeta**, e incluye el entrypoint explícitamente.
- **Bomba de tiempo en el dogfood:** la decisión `0011` —permanente— linkeaba a
  `_changes/0001`, que el harvest manda borrar: el gate quedaba verde hoy y rojo el día que se
  cerrara el cambio. Cortado, y la regla ("ningún doc permanente linkea a `_changes/`") quedó
  en `okf-plan` y en el checklist de harvest, que además ganó dos ítems que faltaban
  (carpeta nueva → `# Subdirectories`; entrada en `log.md`).
- **La pregunta de instalación estaba escrita en el vocabulario del kit** ("¿1600 o 1200
  tokens por turno?") — violando, en el primer paso que involucra al usuario, la regla
  "hablale en su idioma" que esta misma versión agrega. Ahora se pregunta por el
  comportamiento, con un fallback documentado si el usuario no contesta la entrevista del
  roadmap.
- Menores: `status: idea` del template de cambio (contradecía la regla de `okf-plan` de no
  abrir docs para ideas sin compromiso), conteos que no cerraban, `okf-init` desalineado del
  `GUIDE` en los dos niveles de instalación, y descripciones stale del `okf_selfcheck`, del
  registro anti-deriva de `DEVELOPING.md` y del linter (atribuía a PyYAML un chequeo que hace
  un parser propio).
- **`okf_selfcheck.py`: 26 → 35 asserts.** Los nuevos cubren exactamente las reglas que este
  review vio derivar. Los cuatro revisores convergieron de forma independiente en 5 findings,
  y 7 de 7 roturas deliberadas del gate fallaron correctamente.

Y como el kit exige que **cada fix se testee adversarialmente**, los arreglos de arriba
pasaron por su propia revisión en frío (consistencia del diff + dogfood re-caminando el
`GUIDE`). Encontró 1 blocker y ~14 majors **introducidos por los propios fixes**, todos
cerrados acá. Los que valen como lección:

- **`cp` de los tres `SKILL.md` a `docs/okf/` los pisaba entre sí** (los tres archivos fuente
  se llaman igual): el camino vendor-neutral instalaba **un** procedimiento de tres, sin error
  visible. Ahora la instrucción renombra explícitamente.
- **`okf-update` desactivaba en silencio la capa normativa:** su lista de frontmatter no
  nombraba `status:`, y el Nivel 4 filtra por `status: accepted`. Una decisión escrita
  siguiendo el contrato al pie de la letra quedaba fuera de la auditoría — la capa que esta
  misma versión construye se apagaba sola en el uso normal.
- **El Nivel 4 de la copia instalada no excluía el rumbo**, así que reportaría cada ítem no
  implementado del roadmap como "violación del código": el falso positivo exacto que la
  decisión 0012 dice mitigar.
- Varias afirmaciones de la primera tanda eran **falsas y estaban escritas como verificadas**
  (números transcritos a mano que ya no coincidían, "sin punteros huérfanos", "nadie lo
  describe en prosa", conteos de copias). Corregidas, y los asserts que las cubren se
  ajustaron para medir lo que dicen medir.

## 0.5.0 — 2026-06-17

### Agregado — buenas prácticas cosechadas de un sistema de contexto real
Tras investigar la "LLM-Wiki" de un repo real (the-conclave) —un sistema de contexto
maduro, equivalente a OKF y en partes más avanzado— se incorporaron sus mejores ideas:

- **Regla "gana el código" (staleness):** si un concepto contradice la fuente
  (código/schema/datos), el concepto es un bug — se arregla, no al revés. En `OKF-SPEC.md`
  (nueva §3.4), el contrato `templates/AGENTS.md`, `okf-update` y `reference/verification.md`
  (nuevo smell **grave**).
- **Ciclo de deprecación** (gap que la revisión en frío ya había marcado): `_decision.md`
  suma `status` (`proposed`/`accepted`/`superseded by NNNN`) + `supersedes`; `okf-update` y
  `reference/maintaining.md` documentan el procedimiento (decisión nueva que *supersedes* a
  la vieja, mover a `archive/` o marcar `SUPERSEDED`, **nombrar el concepto viejo** para grep).
- **"No transcribas hechos del código"** afilado: clasificación in-code vs *por qué*, el
  framing "un número a mano = drift", y el patrón opcional **`_generated/`** (hechos volátiles
  derivados del código por un script propio). En §3.4 y `reference/profiles.md`.
- **Header de frescura** opcional en references (`verified_against`, `source_of_truth`) —
  `OKF-SPEC.md` §3.1 y `templates/knowledge/_reference.md`.
- **"Concepto = estado presente"** (no historial ni planes; sin checkboxes) — §3.4.
- **`log.md` des-enfatizado a claramente opcional:** en un repo bajo git, `git log` + las
  `decisions/` cumplen su función. `OKF-SPEC.md` §6, `GUIDE.md`, `templates/AGENTS.md`,
  `okf-update`, `maintaining.md`.
- **Scratchpad efímero** (`knowledge/_scratchpad.md`) para tareas multi-sesión — `maintaining.md`.

### Cambiado — linter
- `okf_lint.py` ahora ignora **archivos y carpetas con prefijo `_`** (no solo archivos):
  habilita `_generated/` y `_scratchpad.md`. Verificado: el dogfood sigue 0/0 y un `.md`
  normal sin frontmatter sigue dando ERROR.

### Dogfood
- Las `decisions/` del propio bundle adoptan el nuevo `status: accepted`.

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
