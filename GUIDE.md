# OKF Bootstrap Guide

**Audiencia: un agente (Claude Code u otro) que tiene que montar un sistema de
contexto OKF en un repositorio.** Si sos ese agente, leé esto entero antes de
escribir nada, después seguí el procedimiento.

## Paso 0 — START HERE (leé esto primero)

Te dijeron algo como *"cloná okf-kit y aplicalo a mi repo X"*. Antes de nada:

1. **El destino es OTRO repo (el "repo X"), no este.** `okf-kit` es solo la fuente de
   la guía y los `templates/`. **NUNCA escribas el bundle `knowledge/`, `AGENTS.md`, ni
   nada dentro de `okf-kit`** — este repo ya tiene su propio `knowledge/` (es su dogfood)
   y pisarlo es un bug grave. Todo lo que generes va en el **repo destino**.
2. **Confirmá cuál es el repo destino y su ruta.** Si no está claro, **preguntale al
   usuario** cuál es y dónde está. No asumas que es el directorio actual.
3. **Elegí el camino:**
   - ¿El destino **ya tiene contexto disperso abundante** (un `AGENTS.md`/`CLAUDE.md`
     rico, `/docs`, ADRs, notas)? → seguí el skill **`okf-migrate`** (consolidación
     brownfield), apoyándote en esta guía.
   - ¿Está **limpio**, o su único contexto es el `README`? → camino de **init**
     (greenfield): seguí el procedimiento de abajo (lo mismo que ejecuta `okf-init`).
   - **Regla de corte**, porque el caso más común cae justo en el medio: si lo único que hay
     es un `README` —por sustancioso que sea— es **init**. `okf-migrate` es solo si hay
     artefactos de *contexto para IA* (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`,
     `GEMINI.md`), ADRs, o una carpeta `/docs` con varios documentos. Ante la duda, init: el
     `README` se harvestea igual al sembrar el bundle (§4).
   - ¿**Ya tiene OKF**, de una revisión anterior del kit (mirá el `kit_version` de su
     `knowledge/index.md` contra el `VERSION` de acá)? → no es init ni migración: es
     **actualización**, y va por `reference/upgrading.md`. El bundle no se toca; lo que
     envejeció es el material instalado.
4. **¿Hay Python en la máquina? Entonces no hagas la plomería a mano.** El
   `scripts/okf_install.py` de este kit ejecuta **todo lo mecánico** del init (esqueleto del
   bundle sellado, contrato recortado, skills, scripts, CI, hook) en un comando, verifica su
   salida con el linter y te lista lo que falta. El procedimiento de §4 describe lo mismo
   **a mano**: seguilo entero solo si no hay Python. Qué queda para vos y qué hace el script,
   está dicho **una sola vez**, al principio de §4.
5. Recién entonces, leé el resto y procedé.

---

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
- `reference/verification.md` — cómo testear el bundle (lo usás al verificar, §4).
- `reference/maintaining.md` — el ciclo de vida DESPUÉS del init (cómo no perder frescura).
- `reference/upgrading.md` — subir un repo que ya tiene OKF a la revisión actual del kit.
- `reference/install-per-tool.md` — conectar OKF a cualquier IA (Claude/Cursor/Copilot/Gemini).
- `reference/spec-driven-interop.md` — cómo se relaciona con OpenSpec/Spec Kit (si el repo
  ya usa una de esas, leelo **antes** de montar la capa de futuro: no montes dos).
- `templates/` — archivos para copiar y completar.
- `reference/manual-install.md` — el camino manual de los pasos mecánicos (solo si la máquina no tiene Python).

---

## 1. Qué vas a construir

Hasta tres capas de contexto en el repo destino:

```
<repo>/
├── AGENTS.md            # Entrypoint para agentes (OPCIONAL — ver abajo)
├── CLAUDE.md            # Shim de 1 línea → @AGENTS.md (si usás Claude Code)
├── .claude/skills/      # Procedimientos como skills (OPCIONAL, tool-específico)
│   ├── okf-update/      # mantener el bundle
│   ├── okf-verify/      # testearlo
│   └── okf-plan/        # rumbo y cambios (solo si instalás la capa de futuro)
└── knowledge/           # El bundle OKF — el "qué/por qué". SIEMPRE.
    ├── index.md         # mapa raíz (progressive disclosure)
    ├── log.md           # historial de cambios de contexto
    ├── roadmap.md       # el rumbo vigente (recomendado en desarrollo activo)
    ├── _changes/        # specs de trabajo en curso, efímeras (el linter la ignora)
    └── <carpetas según el perfil>/
```

El **bundle `knowledge/` es el corazón y es obligatorio**. Las otras dos capas
(`AGENTS.md` y los skills) son convenientes cuando un *agente de código* va a
trabajar el repo; para una wiki pura o un bundle de datos que humanos navegan,
podés omitirlas y dejar que el entrypoint sea `knowledge/index.md`.

### Cuánto instalar (el costo permanente es el contrato)

Lo único que se carga en **cada turno de cada sesión** es `AGENTS.md`; el bundle, los
procedimientos y los docs de cambios se leen **solo cuando hacen falta**. Así que el costo
fijo del sistema es el tamaño del contrato, y hay dos niveles:

- **Completo** (default, ~1600 tokens por turno): incluye la capa de futuro.
- **Mínimo** (~1300 tokens por turno): sin capa de futuro — queda pasado + presente (el
  bundle), sin ninguna ceremonia previa a codear.

**Preguntáselo al usuario en su idioma, no en el del kit** (la regla de `okf-plan`: la
metodología es invisible). No le preguntes por tokens por turno: no puede contestarlo y no es
su problema. Preguntale por el comportamiento que va a ver:

> *"¿Querés que además lleve el rumbo del proyecto —qué estás haciendo, qué sigue— para
> retomar sin explicarme todo de nuevo cada vez? Suma un poco de ida y vuelta antes de
> codear."*

Sí → completo. No, o "quiero que vayas directo al código" → mínimo. **Ante la duda,
completo** (es el default). **Si no hay nadie que conteste** —corrés sin usuario en la
sesión— instalá **completo** y decilo en el reporte final, para que quede visible que fue
un default y no una decisión. Se puede subir de mínimo a completo después: agregar la sección
al contrato y sembrar el roadmap. En **los dos** niveles, el contrato ya dice que si el
usuario pide ir directo al código, se respeta.

El nivel elegido es un flag del instalador (`--minimal`), no un trabajo: el recorte del
contrato lo hace él. **A mano** —solo si no hay Python— el borrado es mecánico y está en
[`reference/manual-install.md`](reference/manual-install.md).

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
   **Triage de frescura ANTES de usarlas:** verificá cada doc contra el código (gana el
   código). Vigente → harvesteá/pointeá; **stale/contradice el código → declarala
   no-autoritativa** (no la pointees como verdad: eso consagra el drift); dudosa →
   **preguntale al usuario** si mantener/actualizar/descartar. "Mucha doc vieja" no se
   resuelve pointeando a todo — se separa lo vivo de lo legacy (detalle: skill `okf-migrate`).
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

**Lo mecánico ya está hecho: un comando.** La estructura, los `index.md`, el `log.md`, el
entrypoint recortado y el tooling los instala, sellados y verificados:

```
python3 scripts/okf_install.py <repo-destino> --profile <perfil> --name "<Proyecto>"
```

(`--minimal` si el usuario declinó la capa de futuro · `--no-claude` si no se usa Claude Code ·
`--dry-run` para ver el plan sin escribir). Al terminar corre el linter sobre lo instalado y
lista lo que falta, que es exactamente lo que sigue acá abajo.

> **¿La máquina no tiene Python?** Entonces esos pasos van a mano:
> [`reference/manual-install.md`](reference/manual-install.md). Es el único motivo para
> hacerlo a mano — y también sirve si querés saber qué hace el script.

**Los dos pasos que quedan son los que requieren criterio, y donde está todo el valor.**

### A. Sembrá el bundle (lo más importante — y lo único que ningún script puede hacer)

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
  empieces un link con `/`. Detalle en `OKF-SPEC.md` §4. **Una excepción:** ningún concepto
  linkea a `_changes/` — esos docs se borran al cerrarse, y el link queda roto justo el día
  del harvest. El único que linkea ahí es el `roadmap.md`, que se edita en ese mismo momento.
- **`type:` del vocabulario** de `reference/profiles.md` (núcleo universal + perfil).
- **Frontmatter por defecto:** `type` + `title` + `description` (una sola frase) +
  `timestamp`; `tags` y `resource` cuando apliquen.

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
`index.md` y desde el entrypoint (`AGENTS.md`).

> **Cubrí los términos-mecánica calientes, no solo los stats.** Un *hueco* de cobertura es
> peligroso: si falta el término que preguntan, el agente agarra lo más parecido que tenga a
> mano —a veces una sección del `AGENTS.md` que *suena* a respuesta— y contesta mal sin mirar
> el código (medido: una "regla" de combate respondida desde la sección de capas
> no-autoritativas). Mejor sin entrada que una entrada con el valor horneado, pero mejor aún:
> cubrí los términos que un agente confundiría, apuntando al code-of-record.

**Descriptivo vs normativo — en qué dirección corre la autoridad.** Casi todo lo que sembrás
*describe* lo que existe: si difiere del código, gana el código y el documento es el bug. La
excepción son los que *prescriben* —decisiones aceptadas, convenciones, el rumbo, el
resultado esperado de un cambio activo—: ahí el **código está en violación** y el documento
**no se edita** para emparejarlo. Sembrá con eso en mente: una decisión redactada como
descripción ("el sistema usa X") pierde su fuerza normativa. La regla completa, con las dos
salidas legítimas ante una violación, es `OKF-SPEC.md` §3.5; el mapeo `type` → clase está en
`reference/profiles.md`.

**Capas no-autoritativas (alto ROI en repos ruidosos/legacy).** Si el repo arrastra `notes/`,
docs de refactors viejos o mockups que ya no reflejan el estado, **declaralos como
no-autoritativos en el entrypoint** (sección en `templates/AGENTS.md`): qué dirs son scratch y
que *gana el código*. Sin esa señal, un agente gasta turnos reconciliando basura — medido en
una pregunta de auditoría que cayó de 27 a 2 turnos al declararla (ver `knowledge/decisions/0008`).

**Hechos volátiles: generalos, no los copies (template `_generated.md`).** Entre copiar un
valor a mano (drift) y dejar solo un puntero (el agente igual lee el código), hay un punto
medio para hechos volátiles que se preguntan seguido (conteos, niveles, flags, listas):
**generarlos del código** con un script + un check de frescura en CI. Quedan rápidos de leer
*y* no pueden driftear (patrón `_generated/state.md` + `wiki:gen`/`wiki:check`). El glosario los
apunta como code-of-record. Vale el esfuerzo solo si esos hechos cambian seguido; si son
estables, alcanza el puntero. **Aplicalo REACTIVO** —cuando observás un hecho volátil
preguntado seguido y lo hacés la *única* ruta a ese hecho— **no especulativo**: medido, un
archivo generado a ciegas no lo usó ningún agente (prefirieron el code-of-record del glosario)
y fue overhead sin payoff (ver `knowledge/decisions/0010`).

**La capa de futuro: rumbo + cambios (recomendado si el repo está en desarrollo activo).**
El bundle también lleva el trabajo *por venir*, en dos piezas: **`knowledge/roadmap.md`**
(un concepto `type: Roadmap`, template `_roadmap.md`: visión, qué está en curso, qué sigue,
no-goals — la intención vigente, sin checkboxes) y **`knowledge/_changes/`** (un doc efímero
por cambio no trivial, template `_change.md`: mini-spec + tareas; el linter la ignora y al
cerrarse se harvestea al bundle — ciclo completo en el skill `okf-plan`). **Sembrá el
roadmap preguntándole al usuario** — visión, próximos pasos, qué decidió NO hacer: es
exactamente el conocimiento que no se deduce de ninguna fuente, y para un proyecto que se
desarrolla conversando con IAs es lo que evita perder el rumbo entre sesiones. **Si no
contesta o dice "hacelo vos": escribí lo que sí puedas inferir del código/README y marcá
cada hueco con un blockquote `> Pendiente de confirmar: …`. No omitas el archivo** — si
instalaste el nivel completo, el contrato lo linkea y quedaría un link roto. Si detectás
trabajo a medio hacer (branches, TODOs, features a medias), proponé abrir su doc en
`_changes/`. Para una wiki/datos sin desarrollo activo, omití la capa: eso es la
instalación **mínima**, y se recorta con los marcadores (§1, "Cuánto instalar"). **Si el repo ya usa OpenSpec/Spec Kit u otra herramienta
spec-driven, NO montes `_changes/`**: esa herramienta ya es el dueño del trabajo en curso y
tendrías dos — leé `reference/spec-driven-interop.md` para hacerlas convivir.

> **No planifiques de más.** Sembrá el roadmap y, a lo sumo, los cambios que están
> *realmente* en curso. Escribir specs de trabajo hipotético se siente productivo y no lo
> es: nada las obliga a seguir la realidad, así que se pudren igual que la doc abandonada.

> **Sobre los templates `templates/knowledge/_*.md`:** son plantillas de referencia,
> NO conceptos — el linter las ignora por el prefijo `_`. Cuando crees un concepto a
> partir de una, copiá su contenido a un archivo **sin** el `_` (p.ej. `0001-x.md`) y
> **borrá el comentario HTML del encabezado**: el archivo debe **empezar con `---`**,
> o no es un concepto OKF válido (el linter daría `ERROR — falta frontmatter`).

### B. Verificá (testeá el resultado)

Seguí **`reference/verification.md`** (o corré el skill `okf-verify`). Son tres
niveles (más un cuarto opcional y periódico, **Cumplimiento**: ¿el código viola alguna
decisión aceptada? — no se corre en el init, sino cada tanto):
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

El trabajo **futuro** tiene su propio ciclo: cada cambio no trivial nace como doc en
`knowledge/_changes/` y muere en un **harvest** hacia el bundle (skill `okf-plan`); el rumbo
vive en `knowledge/roadmap.md` y se edita cuando cambia.

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
