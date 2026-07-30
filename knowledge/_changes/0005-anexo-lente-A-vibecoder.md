# Cold review — Lente A: el vibecoder en frío (adopción y fricción)

Repo: `/home/gmendoza/coding/okf-kit` @ v0.7.3 · solo lectura · `okf_selfcheck.py` → 108/108 OK.
Camino recorrido: `README.md` → `GUIDE.md` → `templates/skills/okf-init` / `okf-migrate` →
`scripts/okf_install.py` → material instalado (`templates/AGENTS.md`, `templates/knowledge/`,
`templates/hooks/pre-commit`, `templates/scripts/okf_lint.py`, `templates/ci/okf.yml`) →
`reference/maintaining.md` / `reference/upgrading.md`.

Convención: **[V]** = verificado (archivo:línea o salida pegada) · **[H]** = hipótesis.

---

## 0. El personaje y el camino real

El vibecoder tiene un repo hecho conversando con Claude Code o Cursor. Casi con certeza
tiene un `CLAUDE.md` en la raíz (lo escribe `/init`) **[H, pero es el caso que el propio
kit declara como target: `README.md:45` habla de "repo con docs/ADRs dispersos"]**. Llega
por el plugin.

Pasos hasta ver algo:

| # | Paso | Quién decide | Fricción |
|---|---|---|---|
| 1 | `/plugin marketplace add elgastipaa/okf-kit` | — | tiene que saber qué es un marketplace de plugins |
| 2 | `/plugin install okf@okf-kit` | — | |
| 3 | decir "armá el contexto OKF en este repo" | — | tiene que decir **"OKF"** (§5) |
| 4 | perfil (`codigo`/`datos`/`wiki`/`mixto`) | agente | invisible al usuario. OK |
| 5 | nivel de instalación (capa de futuro sí/no) | **usuario** | 1 pregunta, bien redactada (`GUIDE.md:104-106`) |
| 6 | corre `okf_install.py` | agente | **acá se corta el camino modal** (§1) |
| 7 | triage de frescura: disposición de cada doc stale/dudoso | **usuario** | N preguntas (`okf-migrate/SKILL.md:39-41`) |
| 8 | sembrar el roadmap: visión / próximos / no-goals | **usuario** | 3 preguntas abiertas de producto (`okf-init/SKILL.md:94-97`) |
| 9 | sembrar conceptos: todo *por qué* no deducible | **usuario** | ilimitado (`GUIDE.md:167-170`, "regla de oro") |
| 10 | Nivel 3: pegar un prompt en una CLI nueva y calificar 5-10 respuestas | **usuario** | tarea manual sin payoff visible (`okf-verify/SKILL.md:118-121`) |

**Dónde abandona.** Dos puntos, en orden de probabilidad:

- **Minuto ~2 (paso 6)** si tiene `CLAUDE.md`: el instalador aborta con exit 2 y lo rutea a
  un camino que no instala nada (hallazgo A1). Se queda con un error y sin sistema.
- **Minuto ~15 (pasos 8-9)** si el paso 6 pasó: la conversación se convierte en una
  entrevista sobre decisiones que él no tomó (las tomó la IA, en un chat que ya no existe).
  Ese es exactamente el conocimiento que el kit dice capturar, y exactamente el que este
  usuario **no tiene**. El kit asume un dueño de proyecto con criterio arquitectónico; el
  vibecoder es un dueño de proyecto **sin** ese criterio. Ver A7.

---

## A1 — `okf-migrate` es un callejón sin salida: instala el bundle y **nada** de la maquinaria (BLOCKER)

**[V]** El instalador bloquea cualquier repo con `AGENTS.md`/`CLAUDE.md` escrito a mano:

`scripts/okf_install.py:392-402`
```python
if not args.upgrade and not args.force:
    _theirs = [f for f in ("AGENTS.md", "CLAUDE.md")
               if (target / f).is_file() and not _is_kit_entrypoint(target / f)]
    if _theirs:
        print(f"okf_install: '{target}' ya tiene {' y '.join(_theirs)} escrito a mano y NO se pisa.\n"
              "  → para consolidar ese contexto en un bundle OKF sin perderlo: el skill `okf-migrate`\n"
              "  → para instalar igual y REEMPLAZARLO (commiteá antes): --force", file=sys.stderr)
        return 2
```

`GUIDE.md:23-25` confirma el ruteo: *"`okf-migrate` es solo si hay artefactos de contexto
para IA (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `GEMINI.md`)"*. Un `CLAUDE.md` de tres
líneas alcanza.

**[V]** Y `okf-migrate` **nunca menciona el instalador**:

```
$ grep -n "okf_install\|--force\|scripts/" templates/skills/okf-migrate/SKILL.md
71:de contexto existente a OKF"). Corré `python3 scripts/okf_lint.py knowledge` (o
```

Única mención de `scripts/` es para correr un linter **que el propio skill nunca instaló**.
El repo migrado queda sin: `scripts/okf_lint.py`, `okf_coldtest.py`, `okf_stale.py`,
`.claude/skills/okf-{update,verify,plan}`, `.claude/agents/okf-reviewer.md`,
`.github/workflows/okf.yml`, el pre-commit hook, y sin `kit_version` en `knowledge/index.md`
(el skill nunca dice de copiar `templates/knowledge/index.md`). Es decir: **cero enforcement,
cero mantenimiento, y day-30 indetectable** (A4 se vuelve permanente).

**[V] No hay salida limpia hoy.** Si el agente siembra `knowledge/` primero y después
intenta recuperar la maquinaria con `--upgrade`, el instalador la recorta:

- `okf_install.py:306` → `want_hook=not args.no_hook and _hook_is_ours(target)` → sin hook previo, **no instala el hook**.
- `okf_install.py:304` → `want_ci=... and (target/".github"/"workflows"/"okf.yml").is_file()` → **no instala el CI**.
- `install_upgrade()` (`:296-314`) **no escribe `AGENTS.md`** en ningún caso.

O sea: `--upgrade` es "reemplazá lo que ya está", inútil como primera instalación brownfield.
La única vía completa es `--force`, que pisa el `CLAUDE.md` del usuario — y `okf-migrate`
no la nombra.

**Fix (chico, alineado con la decisión 0017 y exento por la 0013 §"okf-init y okf-migrate
quedan exentos"):** un paso 0 en `templates/skills/okf-migrate/SKILL.md`, entre el
inventario (§1) y el triage (§2):

> **0. Guardá y después instalá la plomería.** Leé entero el `AGENTS.md`/`CLAUDE.md`
> existente (su contenido se harvestea en §3-4) y **commiteá**. Después corré
> `python3 <kit>/scripts/okf_install.py <repo> --force --profile <p> --name "<N>"`:
> instala el esqueleto sellado, el contrato, los skills, el linter, el CI y el hook, y
> reemplaza el entrypoint viejo — cuyo contenido ya tenés. Sin este paso el repo queda con
> bundle y sin enforcement, y la §5 te va a pedir un `scripts/okf_lint.py` que no existe.

Y un renglón en el mensaje del instalador (`okf_install.py:398-401`): *"→ okf-migrate
harvestea ese archivo primero y vuelve acá con `--force`"*, para que el ruteo sea un ciclo
cerrado y no una bifurcación.

**Gana:** el caso modal (repo vibecodeado con Claude Code) deja de terminar en un error o en
media instalación.

---

## A2 — "todo se revierte con `git checkout`" es falso, y es justo la frase que baja la guardia

**[V]** `README.md:61`: *"Es stdlib puro y todo lo que escribe se revierte con
`git checkout`."* — igual en `README.en.md:54`.

En una instalación fresca **casi nada** de lo que escribe el instalador es un archivo
*tracked modificado*: son archivos **nuevos untracked** (`AGENTS.md`, `CLAUDE.md`,
`knowledge/**`, `scripts/*.py`, `.claude/**`, `.github/workflows/okf.yml`), y `git checkout`
no toca untracked. Peor, el hook va a `.git/hooks/pre-commit` (`okf_install.py:244-245`),
que **git no versiona en absoluto**: ni `git checkout` ni `git clean` lo sacan.

**Fix:** reemplazar la frase por la verdad operativa, que además tranquiliza más porque es
verificable: *"No toca tu código: escribe archivos nuevos (`AGENTS.md`, `CLAUDE.md`,
`knowledge/`, `scripts/okf_*.py`, `.claude/`, el workflow de CI) y un `.git/hooks/pre-commit`.
Para ver exactamente qué va a hacer sin escribir nada: `--dry-run`. Para deshacerlo:
`git clean -nd` primero, y borrar `.git/hooks/pre-commit` a mano."*
Y mencionar `--dry-run` **antes** que la lista de flags, no al final de la línea 61.

**Gana:** el hesitante prueba con `--dry-run` en vez de no probar; y el que quiera salir
puede salir de verdad.

---

## A3 — Nada detecta una instalación abandonada a mitad: los `{{placeholders}}` sobreviven en el archivo que se carga en cada turno

**[V]** El instalador deja placeholders a propósito y los reporta **una sola vez**
(`okf_install.py:343-350`, `:454-456`). Después de eso, ninguna capa los ve:

```
$ grep -n "{{\|placeholder" templates/scripts/okf_lint.py
157:  errs.append(f"`{key}`: '{{' sin cerrar")     # ← es sobre YAML, no sobre placeholders
```

El hook (`templates/hooks/pre-commit`) no los mira; el CI (`templates/ci/okf.yml`) corre solo
el linter; el checklist de 9 ítems del Nivel 1 de `okf-verify` (`SKILL.md:44-62`) tampoco los
nombra. Los archivos afectados son los peores posibles:

- `AGENTS.md` — se carga **en cada turno de cada sesión** y quedaría con
  `{{Lo que un agente DEBE o NO DEBE hacer, en bullets cortos, linkeando al concepto...}}`
  (`templates/AGENTS.md:35-38`) y `{{Listá los dirs/archivos scratch, legacy...}}` (`:96-98`)
  leídos como si fueran contrato.
- `knowledge/index.md` — el bloque `# Subdirectories` **nace** con placeholder por diseño
  (`okf_install.py:167-172`).
- `knowledge/log.md:12` — `{{qué conceptos sembraste en este primer pase}}`.

Un vibecoder cuya sesión de init se queda sin contexto a mitad (frecuentísimo: el paso 9 es
la parte larga) se queda con esto **para siempre**, y su repo *parece* initeado: el linter da
verde (`0 error(es), 0 warning(s)`).

**Fix:** un WARN nuevo en `templates/scripts/okf_lint.py` — *"`{{...}}` sin completar
(instalación a medias)"* — sobre cualquier `.md` del bundle no prefijado con `_`, y una línea
en el checklist del Nivel 1 de `okf-verify` para el `AGENTS.md`. Es WARN, no ERROR: no rompe
CI y respeta la [0002 consumo permisivo]. Efecto secundario deseable: el día 1 el bundle
recién instalado **avisa** que la instalación no terminó, en vez de dar verde.

**Gana:** "instalación a medias" pasa de invisible-para-siempre a visible en cada commit y en
cada CI.

---

## A4 — Día 30: el repo nunca se entera de que la maquinaria envejeció

**[V]** El material instalado se fosiliza (`reference/upgrading.md:10-12`) y la única forma de
saberlo es comparar a mano contra el kit (`upgrading.md:19-22`). Pero **nada de lo que queda
en el repo destino nombra esa posibilidad**:

```
$ grep -rn "kit_version" templates/ | grep -v Binary
templates/skills/okf-init/SKILL.md:36   ← se borra: okf-init no se instala
templates/skills/okf-init/SKILL.md:62   ← ídem
templates/knowledge/index.md:4,6,32     ← comentario de template que el instalador BORRA
```

`okf_install.py:157` elimina el comentario de la línea `kit_version`, así que en el repo
instalado queda `kit_version: "0.7.3"` **sin ninguna explicación**. Ni el `AGENTS.md`
instalado, ni `okf-update`, ni `okf-verify`, ni `okf-plan` mencionan que exista un upgrade.
Un vibecoder que actualiza el plugin (`/plugin update`) obtiene `okf-init`/`okf-migrate`
nuevos y su repo sigue en 0.7.3 sin que nadie se lo diga.

Además `reference/maintaining.md:54-58` explica esto correctamente… pero es un archivo del
**kit**, que por la decisión 0013 no está en el repo destino.

**Fix (barato, cero costo por turno):** que `build_log()` estampe la ruta de salida en
`knowledge/log.md` — el archivo ya se escribe en el init y **no** se carga en cada turno:

```
* **Initialization**: Bundle OKF inicial creado con OKF kit v0.7.3.
  La maquinaria (contrato, skills, scripts, CI, hook) se fosiliza en esta versión:
  para subirla, `python3 <okf-kit>/scripts/okf_install.py <este-repo> --upgrade`.
```

Opcionalmente, un chequeo de 3 líneas en `okf-verify` Nivel 1: *"si `okf-kit` está en disco,
comparar `kit_version` contra su `VERSION`"*.

**Gana:** el upgrade deja de depender de que el usuario recuerde que el kit existe.
(No está en `knowledge/roadmap.md`: el roadmap habla de adopción y de deudas de tooling,
no de descubribilidad del upgrade desde el repo destino.)

---

## A5 — El `README.md` (la puerta principal, en español) vende abstracción; la versión en inglés tiene el gancho que le falta

**[V]** Comparar las primeras líneas:

- `README.en.md:9-11`: *"**The problem.** You build a project by talking to AI. The reasoning
  lives in a chat that expires. Next session — new machine, new tool, new model — you explain
  everything again."* ← esto es el vibecoder, literal.
- `README.md:7-9`: *"Esta carpeta es una **guía self-contained + librería de templates** para
  montar un sistema de contexto duradero en cualquier proyecto, usando el **Open Knowledge
  Format (OKF)**."* ← tres términos abstractos antes del primer verbo útil.

**[V] Cero números en la puerta.** `README.md` no tiene una sola cifra de resultado. Las
promesas son de diseño, no de outcome (`README.md:159-169`: "no perder nunca / a la hora que
sea / con la IA que sea…"). Y sin embargo el kit **ya tiene dos números medidos, públicos y
en el propio repo**:

- `knowledge/decisions/0007-domain-glossary-and-code-of-record.md:32` — *"~−62% en turnos y
  −66% en latencia"* en preguntas de término.
- `knowledge/decisions/0008-declare-non-authoritative-layers.md:31-32` — *"de **27 a 2
  turnos**"* en una pregunta de auditoría.

Ambos aparecen recién en `GUIDE.md:230` y `GUIDE.md:256` — un documento cuya audiencia
declarada es *"un agente"* (`GUIDE.md:3`), no el humano que decide si adoptar.

**[V] La tabla "Qué hay acá" (`README.md:89-128`) tiene 35 filas** e incluye
`okf_selfcheck_test.py`, `DEVELOPING.md`, `.claude-plugin/`, el dogfood: es el inventario del
**toolsmith**, no el onboarding del usuario. El vibecoder scrollea 40 líneas de archivos que
nunca va a abrir.

**Fix:** (a) portar el párrafo "El problema" de `README.en.md:9-11` arriba de `README.md:7`;
(b) inmediatamente después, un bloque de 3 líneas con los dos números y su link a la decisión
que los respalda — es *citar lo que ya está publicado*, no requiere medir ni publicar nada
nuevo (distinto del ítem del roadmap "Publicar la medición del harness de eval", que sí
requiere decidir qué se publica); (c) partir la tabla en dos: **"Para usar el kit"** (6 filas:
`GUIDE.md`, `OKF-SPEC.md`, `reference/profiles.md`, `reference/examples.md`,
`reference/verification.md`, `reference/upgrading.md`) y, colapsada bajo un `<details>`,
**"Para trabajar sobre el kit"** (el resto).

**Gana:** el desconocido entiende el problema en 10 segundos y ve una cifra antes de decidir.

---

## A6 — Para disparar el kit hay que ya conocer el kit

**[V] a) El vocabulario de disparo exige la sigla.** `templates/skills/okf-init/SKILL.md:6-7`:
*"Usalo cuando el usuario pide 'armá/inicializá/bootstrapeá este repo con **OKF**' o 'creá el
contexto **OKF** acá'."* Las dos variantes contienen "OKF". Ídem `okf-migrate/SKILL.md:6-7`.
El `description:` del frontmatter es **la única superficie de auto-disparo** de un skill, y no
contiene ninguno de los síntomas con los que este usuario describe su problema: *"cada sesión
le tengo que explicar todo de nuevo"*, *"documentá este proyecto"*, *"que la IA se acuerde de
cómo funciona esto"*, *"ordenemos la doc"*. Contraste: `okf-plan/SKILL.md:3-9` **sí** lista
disparadores en lenguaje natural ("¿qué sigue?", "¿en qué estábamos?") — el patrón correcto
ya existe adentro del kit, solo que no en los dos skills de entrada.

**Fix:** agregar esas frases-síntoma al `description:` de `okf-init` y `okf-migrate`. Es una
edición de dos líneas y multiplica la superficie de disparo.

**[H] b) Los nombres de slash-command del README pueden estar mal.** `README.md:45` promete
*"Eso te deja `/okf-init` … y `/okf-migrate`"*, y `reference/install-per-tool.md:64` repite
*"shippea `/okf-init` y `/okf-migrate`"*. Pero `.claude-plugin/plugin.json` los declara bajo
`"skills"`, y los skills de plugin en Claude Code se nombran `plugin:skill` — acá sería
`/okf:okf-init`. No lo puedo verificar desde el repo. **Es de verificación trivial y de costo
altísimo si está mal**: el usuario tipea `/okf-init`, no pasa nada, y se va en 10 segundos.

---

## A7 — No existe el "arranque más chico posible", y el kit ya sabe cuál sería

El kit pide, en el init, un trabajo que él mismo describe como *el* modo correcto de operar
más adelante:

**[V]** `reference/maintaining.md:116-117`: *"el bundle vale solo si se mantiene. **Una pieza
de conocimiento por vez, como efecto colateral del trabajo normal — no como un proyecto
aparte.**"* Y `GUIDE.md:330`: *"No documentes todo de una: el bundle crece orgánico, una pieza
por vez."*

Pero el init exige lo contrario: `GUIDE.md:197` — *"**A.** Sembrá el bundle (lo más importante
— y lo único que ningún script puede hacer)"* con una lista de prioridades por perfil
(`GUIDE.md:203-207`), la regla de oro de preguntar todo lo no deducible (`GUIDE.md:167-170`),
y tres preguntas abiertas para el roadmap (`okf-init/SKILL.md:94-97`). Para el vibecoder eso
es un proyecto aparte de una hora, sobre decisiones que tomó una IA en un chat borrado.

**[V]** Y sin embargo el estado "esqueleto sin conceptos" ya es válido y conforme: el
instalador no crea carpetas vacías a propósito (`okf_install.py:52-54`) y su salida pasa el
linter en `--strict` desde el segundo cero (`okf_install.py:428-433`; el selfcheck lo verifica:
`PASS okf_install.py deja una instalación mínima que el linter acepta (--strict)`). Con el
contrato instalado, cada sesión posterior acumula conceptos sola (`templates/AGENTS.md:102-126`,
§2 "el trato").

**Fix (criterio, no plomería):** nombrar explícitamente ese arranque en `GUIDE.md` §4 y en
`okf-init/SKILL.md` §3, como **cota inferior legítima**, no como fracaso:

> **Si el usuario no tiene el *por qué* a mano** (típico en un repo desarrollado conversando
> con IAs: las decisiones las tomó un chat que ya no existe): **no lo entrevistes**. Sembrá
> solo lo que se deduce de la fuente —`architecture/overview.md` (el mapa) y el roadmap con
> `> Pendiente de confirmar:` en cada hueco— completá el `AGENTS.md`, y decile que el resto lo
> va a ir capturando el contrato a medida que trabajen. El bundle crece orgánico
> (`maintaining.md`); una entrevista de una hora que él no puede contestar es la forma más
> común de no adoptar nada.

Esto **no** contradice ninguna decisión: la 0014 mide que un documento vacío cuesta más que no
tenerlo, y acá no se propone sembrar vacío sino sembrar **poco y verdadero**. Sí está en
tensión con el énfasis retórico del kit ("todo el valor está en sembrar") — es una tensión de
prosa, no normativa.

**Gana:** convierte el punto de abandono #2 (minuto ~15) en un final feliz de 5 minutos con un
sistema que se llena solo.

---

## A8 — El puente a Cursor/Copilot/Gemini es plomería y la hace el usuario

**[V]** `reference/install-per-tool.md:68-80` da los contenidos exactos, de una línea, para
`.cursor/rules/okf.mdc`, `.github/copilot-instructions.md` y `GEMINI.md`. **[V]** El
instalador no escribe ninguno: `install_machinery()` (`okf_install.py:218-245`) solo maneja
skills, agentes, scripts, CI y hook, y `--no-claude` únicamente cambia el destino a
`docs/okf/` (`:208-214`). El único puntero es una frase al final de
`okf-init/SKILL.md:113-114`.

Un vibecoder de Cursor termina con `AGENTS.md` + bundle y **sin** el refuerzo de la regla, que
es exactamente el archivo que su herramienta lee siempre.

**Fix:** un flag `--tool cursor|copilot|gemini` (repetible) en `okf_install.py` que escriba el
puntero de 2 líneas ya redactado en `install-per-tool.md`. Es determinista, cero criterio →
va al script por la [decisión 0017]. Y una pregunta más en `okf-init` §1: *"¿con qué
herramienta trabajás este repo?"* — es la única pregunta de las 10 que el vibecoder contesta
sin pensar.

---

## 1. Lo que el kit asume que el vibecoder sabe (y no explicita)

Inventario de conocimiento tácito exigido en el camino del usuario, con dónde aparece:

| Asume | Dónde | ¿Se explica? |
|---|---|---|
| plugins/marketplaces de Claude Code | `README.md:40-43` | no |
| que existe `python3` y cómo instalarlo | `README.md:29-32` | avisa, no ayuda |
| **frontmatter YAML** y que un `:` sin comillas rompe | `templates/AGENTS.md:116`, `okf-update/SKILL.md:48` | se nombra la trampa, nunca el concepto |
| **ADR** (los `decisions/NNNN-slug.md` son ADRs) | `GUIDE.md:204`, `reference/profiles.md:22` | la sigla aparece en `README.md:45`, `GUIDE.md:150` sin definirse nunca |
| qué es un **skill** y qué un **subagente** | `README.md:106-111`, `okf-verify/SKILL.md:22-27` | no |
| git hooks, `.git/hooks/`, `--no-verify` | `templates/hooks/pre-commit:15` | menciona el escape, no el mecanismo |
| GitHub Actions / CI | `templates/ci/okf.yml` | el comentario del yml lo explica bien, pero está dentro del archivo |
| semver y qué significa `kit_version` vs `okf_version` | `README.md:120-121` | sí, en la tabla de 35 filas |
| **monorepo**, "partir un bundle", "perfil" | `GUIDE.md:133-134` | perfil sí (`profiles.md`); monorepo se asume |
| descriptivo vs normativo, y qué es "superseder" | `templates/AGENTS.md:53-62` | **sí, y bien** — es de lo mejor escrito del kit |

Lo notable: lo *difícil* (autoridad descriptiva/normativa) está explicado con cuidado; lo
*básico* (ADR, frontmatter, skill) se asume. Es el patrón de un autor experto escribiendo para
sí mismo. Un glosario de 8 líneas al pie del `README.md` —o mejor, el propio kit dogfoodeando
su `_glossary.md`, que hoy no usa— lo cierra.

## 2. Jerga propia: cuánta hay y cuánta hace falta

Conteo sobre los tres archivos que el vibecoder o su agente ven siempre:

```
término                   README  GUIDE  templates/AGENTS.md
bundle                       22     25       4
concepto                      4     12       8
perfil                        1     14       0
contrato                      1      8       5
entrypoint                    3      6       0
capa de futuro                2      6       1
harvest                       1      6       3
normativ*                     2      2       4
frontmatter                   0      4       2
code-of-record                0      4       0
no-autoritativ*               0      4       0
drift                         1      3       1
progressive disclosure        1      3       0
greenfield / brownfield       1/1    1/1     0/0
keep-alive                    0      0       0   ← no existe en el kit
```

Veredicto por término:

- **Se gana el lugar** (nombra algo que no tiene nombre corto en castellano y el agente lo
  usa): `bundle`, `concepto`, `perfil`, `harvest`, `normativo/descriptivo`, `frontmatter`,
  `drift`. Siete términos es un presupuesto razonable.
- **Es jerga evitable en la puerta de entrada**: `entrypoint` (= "el contrato" o "el archivo
  que la IA lee primero" — el kit ya usa las dos), `progressive disclosure` (aparece 1 vez en
  `README.md:165` explicándose a sí misma en la misma línea → se puede borrar el término y
  dejar la explicación), `greenfield`/`brownfield` (`README.md:106-107` — "repo limpio" /
  "repo con docs" ya está al lado, en la misma frase: sobran).
- **`code-of-record`**: 4 usos, todos en `GUIDE.md`, ninguno en material instalado. Es un buen
  concepto (el archivo donde vive el *valor* exacto) pero solo lo necesita quien siembra un
  glosario. Que se quede donde está.
- **`keep-alive`**: **[V]** no existe en el kit (0 ocurrencias en `README/GUIDE/templates`;
  solo aparece como nombre de un assert en `AGENTS.md:56` del propio repo). Sin problema.

**Conclusión de vocabulario:** el kit **no** tiene un problema de exceso de jerga; tiene un
problema de **densidad en la primera pantalla**. `README.md:7-9` mete "self-contained",
"librería de templates", "sistema de contexto duradero" y "Open Knowledge Format" antes de
decir para qué sirve. La jerga que sobra son 4 términos (`entrypoint`, `progressive
disclosure`, `greenfield`, `brownfield`) y todos ya tienen su traducción escrita al lado.

## 3. Lo que sí está muy bien (para no romperlo)

- La pregunta del nivel de instalación (`GUIDE.md:99-112`) es un modelo de cómo preguntarle a
  un no-técnico: prohíbe hablar de tokens, da la frase exacta, y define el default y el
  comportamiento sin usuario presente.
- La regla "hablale al usuario en su idioma, no en OKF" (`templates/AGENTS.md:91-94`,
  `okf-plan/SKILL.md:34-35`) es exactamente el instinto correcto para este público.
- El corte mecánico/criterio de la [0017] es real y se nota: el instalador hace ~40
  operaciones que antes se le pedían a la IA.
- `okf_install.py` protege el `AGENTS.md`/`CLAUDE.md` del usuario en vez de pisarlo
  (`:388-402`). El instinto es correcto; el problema (A1) es que la salida de emergencia no
  lleva a ningún lado.

---

## Ranking final (impacto para el vibecoder / esfuerzo)

| # | Hallazgo | Impacto | Esfuerzo | Estado |
|---|---|---|---|---|
| 1 | A1 — `okf-migrate` no instala maquinaria y es el destino forzado del repo modal | crítico | ~15 líneas de prosa + 1 renglón en el instalador | [V] |
| 2 | A6a — el disparo exige decir "OKF" | alto | 2 líneas de `description:` | [V] |
| 3 | A5 — README sin problema ni número en la primera pantalla | alto | ~20 líneas | [V] |
| 4 | A3 — instalación a medias invisible para siempre | alto | 1 WARN en el linter + 1 línea en okf-verify | [V] |
| 5 | A7 — no existe el arranque mínimo, y el kit ya sabe cuál es | alto | 1 blockquote en GUIDE §4 + okf-init §3 | [V] |
| 6 | A4 — el upgrade es indescubrible desde el repo | medio-alto | 2 líneas en `build_log()` | [V] |
| 7 | A6b — ¿los slash-commands del README existen con ese nombre? | crítico si es cierto | 1 minuto de verificación | [H] |
| 8 | A2 — "se revierte con `git checkout`" es falso | medio | 2 líneas | [V] |
| 9 | A8 — el puente a Cursor/Copilot lo hace el usuario a mano | medio | flag `--tool` | [V] |

## Si tuviera que elegir una sola cosa

**A1.** Todo lo demás es fricción; esto es una pared. El repo modal del público objetivo
—vibecodeado con Claude Code, con un `CLAUDE.md` de tres líneas— es rechazado por el
instalador (`okf_install.py:392-402`) y derivado a `okf-migrate`, que no instala el linter,
ni el hook, ni el CI, ni los skills, ni `kit_version`, y que en su último paso le pide correr
un script que nunca copió (`okf-migrate/SKILL.md:71`). El resultado no es "menos kit": es un
repo con una carpeta `knowledge/` sin ninguna de las capas que hacen que no se pudra, y sin
forma de detectar el desfasaje después. El arreglo es un paso 0 en el skill que harvestea el
entrypoint viejo y corre `okf_install.py --force`, más un renglón en el mensaje de error del
instalador para cerrar el ciclo. Es media hora de trabajo y desbloquea el caso más común que
el kit dice servir.
