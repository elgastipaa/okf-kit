# Lente B — Economía del agente (tokens, turnos, latencia)

Revisión con contexto fresco de `okf-kit` v0.7.3 · 2026-07-30
Fuentes: repo en disco + `eval/` (8 scorecards, 61 corridas) + `scripts/okf_selfcheck.py` (108/108 OK).

Notación: **[V]** verificado (con `path:línea`, conteo real o salida pegada) · **[H]** hipótesis.

---

## TL;DR

1. **El presupuesto del contrato mide el 80% de lo que realmente se paga por turno.** `BUDGET = 7000`
   solo cuenta `AGENTS.md`. El always-on real es **8.382 chars ≈ 2.095 tok** (contrato 6.684 +
   `CLAUDE.md` 308 + descripciones de skills ~1.390). **[V]**
2. **El instalador deja andamiaje instalado**: `CLAUDE.md` se copia crudo, con su comentario
   `<!-- TEMPLATE — copiá esto a la RAÍZ del repo destino… -->`. El `GUIDE.md:71` promete un shim
   de 1 línea; se instalan 9. **[V]**
3. **Fuera de q7, el efecto medido del kit está por debajo de su propio ruido.** Réplica de facto
   (blind2 vs blind3): |Δ| medio **3,29 turnos/pregunta**. Efecto del kit sin q7: **2,72
   turnos/pregunta**, con signo mixto. **[V]**
4. **El 25% del contrato always-on (§2, 403 tok) financia el camino de ESCRITURA, que el harness
   nunca midió.** La mitad del balance de ROI no existe. **[V]**
5. **Mecanismo #5 propuesto: "el code-of-record cierra la búsqueda"** — autoridad **negativa**
   acotada + ancla de símbolo. Ataca `trap`, la categoría más cara medida (6,4 turnos de promedio
   sobre n=19).
6. **El juez es arreglable y el bug es de una línea**: corre **sin `cwd=repo`**
   (`templates/eval/run-eval.py:82`), así que no puede verificar nada contra el código. **[V]**

---

## 1. Presupuesto real de contexto

### 1.1 Lo que se paga en CADA turno (prefijo cacheado)

Estimación en tokens = chars/4, la misma convención que usa el gate
(`scripts/okf_selfcheck.py:270`). No hay tokenizer en el entorno; para castellano c/4 es
**optimista** (~3,3–3,6 chars/tok es más realista), o sea los números de abajo son un piso. **[H]**

| Bloque | Chars | ~tok (c/4) | ¿Lo cuenta el gate? | Fuente |
|---|---:|---:|---|---|
| `AGENTS.md` instalado (full) | **6.684** | **1.671** | sí (6.684/7.000 = **95,5%**) | `build_agents()` de `okf_install.py` |
| `AGENTS.md` instalado (minimal) | 5.118 | 1.279 | sí | ídem `--minimal` |
| `CLAUDE.md` instalado (shim + comentario TEMPLATE) | **308** | **77** | **NO** | `okf_install.py:250` (`plan.copy`, sin strip) |
| Descripciones de skills instalados (Claude Code las inyecta al system prompt) | **1.040** | **260** | **NO** | frontmatter de `okf-update`/`okf-verify`/`okf-plan` |
| Descripción del subagente `okf-reviewer` | 350 | 87 | **NO** | `templates/agents/okf-reviewer.md` |
| **TOTAL always-on (full, Claude Code)** | **8.382** | **≈2.095** | — | |
| **TOTAL always-on (minimal, sin `okf-plan`)** | **6.485** | **≈1.621** | — | |

**[V]** Todos los conteos salen de ejecutar `build_agents()`/`build_index()`/`build_log()`/
`build_roadmap()` de `scripts/okf_install.py` en read-only y de `wc -c` sobre los templates.

### 1.2 Desglose del contrato por sección — ¿qué compra cada bloque?

| Sección | Chars | % | ~tok | ¿Paga en turnos de LECTURA? |
|---|---:|---:|---:|---|
| `# <Proyecto> — Contrato` | 128 | 2,0% | 32 | sí (identidad) |
| `## Reglas duras` | 289 | 4,3% | 72 | sí — contenido del usuario |
| **`## 1. Antes de actuar`** | **3.691** | **55,2%** | **922** | **sí — acá viven ADR 0007/0008/0009** |
| **`## 2. Mientras trabajás` (mantenimiento)** | **1.614** | **24,1%** | **403** | **NO — solo en turnos de escritura** |
| `## 3. Antes de cerrar` | 437 | 6,5% | 109 | parcialmente |
| `## Procedimientos` | 318 | 4,8% | 79 | redundante con las descripciones de skills (260 tok) |

En instalación mínima §2 sube a **32,9%** del contrato: cuanto menos kit instalás, mayor proporción
del peaje se va en instrucciones de mantenimiento.

### 1.3 Lo que se carga bajo demanda

| Artefacto | Chars | ~tok | Cuándo |
|---|---:|---:|---|
| `knowledge/index.md` (día 1) | 246 | 61 | primer hop |
| `knowledge/log.md` (día 1) | 174 | 43 | casi nunca (§3) |
| `knowledge/roadmap.md` (día 1) | 1.223 | 305 | disparadores de la capa de futuro |
| `okf-update/SKILL.md` | 5.545 | 1.386 | al invocar |
| `okf-verify/SKILL.md` | 9.880 | 2.470 | al invocar |
| `okf-plan/SKILL.md` | 11.994 | 2.998 | al invocar |
| `okf-reviewer.md` | 4.099 | 1.024 | al delegar |
| Bundle maduro (dogfood del propio kit) | 107.132 (40 .md) | ~26.800 | nunca entero (progressive disclosure) |

### 1.4 Veredicto sobre el presupuesto

**El techo de 7.000 chars es del orden correcto; la frontera de medición está mal.**

- **[V]** El gate mide un solo archivo. Lo always-on son tres cosas (contrato + shim + descripciones
  de skills). El error es **+25%** sobre lo declarado (2.095 tok reales vs "~1.750" que promete
  `templates/AGENTS.md`).
- **[V]** Queda **4,5% de headroom** (316 chars). Cualquier convención nueva que toque el contrato
  no entra sin sacar algo. El mecanismo #5 propuesto abajo cabe en ~250 chars; el siguiente ya no.
- **[V]** El chequeo de autosuficiencia (`okf_selfcheck.py:551-556`) pasa por `strip_comments`
  apoyado en la regla de diseño 2: *"los comentarios HTML no cuentan como contenido: la instalación
  los borra"*. **Esa premisa es falsa para `CLAUDE.md`** — ver hallazgo B1.
- **[H]** Anclaje empírico débil: `blind3 q7` (t=2, con contrato) `cache_read=21.541` vs
  `baseline q1` (t=2, sin contrato) `cache_read=19.011` → Δ ≈ 1.265 tok/turno, en el orden del
  estimado c/4. No es un A/B controlado (preguntas distintas) — no lo tomen como medición.
- El costo absoluto (0,8–1% de una ventana de 200k) es barato. **El costo caro es de atención, no
  de tokens**, y el propio kit lo dice: *"un contrato largo se skimea (pierde obediencia)"*
  (`templates/AGENTS.md`, comentario de cabecera). La evidencia lo respalda: el falso positivo de
  q5 en blind V1 salió de matchear una **sección del contrato**, no del bundle.

---

## 2. Lo más importante que encontré: el efecto está bajo el ruido

`run-eval.py` corre **n=1 por pregunta**. Nunca se midió la varianza. Se puede recuperar de los
scorecards existentes.

### 2.1 Réplica de facto — blind2 vs blind3

ADR 0010 estableció (y `eval/COMPARISON.md` lo dice) que **ninguna de las 7 preguntas leyó el
archivo generado** que blind3 agregó. Para efectos de estas preguntas, blind2 y blind3 son la
**misma condición corrida dos veces**:

| q | blind2 | blind3 | \|Δ\| | ratio |
|---|---:|---:|---:|---:|
| q1 | 9 | 8 | 1 | 1,1× |
| q2 | 17 | 4 | **13** | **4,2×** |
| q3 | 4 | 4 | 0 | 1,0× |
| q4 | 4 | 7 | 3 | 1,8× |
| q5 | 4 | 10 | **6** | **2,5×** |
| q6 | 6 | 6 | 0 | 1,0× |
| q7 | 2 | 2 | 0 | 1,0× |
| | | | **3,29 medio** | |

**[V]** Ruido intra-condición: **3,29 turnos por pregunta**.

Segunda réplica, en la condición **sin kit**: q1 midió **11 turnos** (`scorecard.adversarial.jsonl`,
la corrida del adendum) y **2 turnos** (`scorecard.adversarial.baseline.jsonl`). Misma pregunta,
mismo repo, sin capa: **5,5× de spread**. **[V]**

### 2.2 Efecto del kit vs ese ruido

| q | baseline | media de las 3 blind | efecto |
|---|---:|---:|---:|
| q1 (AoE, probar una negativa) | 2 | 9,3 | **+7,3** |
| q2 (contar skills por árbol) | 6 | 9,3 | +3,3 |
| q3 (subclases) | 7 | 4,0 | −3,0 |
| q4 (niveles de abismo) | 4 | 5,7 | +1,7 |
| q5 (anti-waste) | 5 | 5,0 | 0,0 |
| q6 (último kit de UI) | 7 | 6,0 | −1,0 |
| **q7 (cuántos docs viejos)** | **27** | **3,0** | **−24,0** |

- \|efecto\| medio con q7: **5,76** turnos → por encima del ruido (3,29).
- \|efecto\| medio **sin q7: 2,72** turnos → **por debajo del ruido (3,29)**, y con signo mixto
  (3 suben, 2 bajan, 1 empata). **[V]**

Agregados **sin q7** (turnos / ctx_tok / segundos / costo):

| condición | turnos | ctx_tok | seg | $ |
|---|---:|---:|---:|---:|
| baseline (sin kit) | 31 | 591.216 | 258 | 2,55 |
| blind V1 | 35 | 630.981 | 158 | 2,16 |
| blind V2 | 44 | 852.414 | 211 | 2,51 |
| blind V3 | 39 | 752.426 | 207 | 2,61 |

### 2.3 Qué significa esto para la promesa del kit

**[V]** El −21%/−31% publicado en `eval/COMPARISON.md` es real, pero **está concentrado en una sola
pregunta** (q7: "¿cuántos .md quedaron viejos?"). Sacándola, el kit **no ahorra turnos** en idlerpg
y en algunos casos cuesta más; lo único que sí mejora consistentemente es la **latencia** (258s →
158–211s, −18 a −39%), probablemente porque los turnos con puntero son más cortos que los turnos
exploratorios. **[H]** sobre la causa.

**Esto no invalida el kit** — invalida la *forma de contarlo*:
- q7 es una pregunta **meta** ("auditá los docs viejos"), que un usuario hace una vez, no todos los
  días. Vender −31% a partir de ella es sobreventa.
- La ganancia grande y estable del kit **sí existe** y es la de conclave: glosario sobre repo
  grande/forked (q2 12→4, q5 8→3, q1 4→2 — `eval/conclave/scorecard.kit*.jsonl`). Esa es la que hay
  que publicar, con su condición de aplicabilidad.
- **Para cualquier medición futura: n≥3 por celda.** Con n=1 y ruido de 3,3 turnos, el harness no
  puede distinguir un mecanismo que funciona de uno que no, salvo que valga >10 turnos.

---

## 3. Material instalado que NO se lee nunca

**Método y su límite.** Los scorecards guardan solo `answer` (`run-eval.py:132`) — **no hay traza de
tool calls**. El prompt pide citar fuentes (`ASK_SUFFIX`, `run-eval.py:23`), así que las citas son un
**piso** de lo leído, y los archivos puramente de ruteo (index) están sub-representados por
construcción. Con esa advertencia, sobre 61 corridas:

| Artefacto | Citas | Lectura |
|---|---:|---|
| `knowledge/glossary.md` / `knowledge/domain/glossary.md` | **7** | el artefacto instalado más citado, lejos (q2,q3,q4,q5 en las 3 blind) |
| `AGENTS.md` | 6 | casi todas en q5/q7 → la **declaración de autoridad** (ADR 0008) |
| `docs/wiki/_generated/state.md` (conclave) | **4** | el generado **reactivo** SÍ se usa (q3,q4,q5,q9) — confirma el refinamiento de ADR 0010 |
| `knowledge/decisions/0002-*.md` | 2 | una sola decisión, en q5 |
| `knowledge/architecture/overview.md` | 1 | blind3 q6 |
| `docs/wiki/index.md` (conclave) | 1 | q8 |
| **`knowledge/index.md`** | **0** | nunca aparece en una respuesta |
| **`knowledge/log.md`** | **0** | nunca |
| **`knowledge/roadmap.md`** | **0** | nunca (ninguna pregunta era de rumbo) |
| **`<carpeta>/index.md`** | **0** | nunca |
| **`knowledge/_changes/*`** | **0** | nunca |
| **runbooks / references** | **0** | nunca |

### Ranking de peso muerto

1. **`knowledge/log.md` — el más claro.** 0 citas en 61 corridas, **13 ediciones** en la historia del
   propio kit. No es un router (es un diario cronológico), así que la excusa del sub-conteo no
   aplica. El contrato ya lo trata como opcional (*"si mantenés `log.md`"*, `templates/AGENTS.md` §2)
   pero `okf_install.py:256` lo instala siempre y `KEEPALIVE_TOKENS`
   (`okf_selfcheck.py:225`) lo exige en los pasos del keep-alive. **Recomendación: que sea opt-in.**
   El log real es `git log` + `decisions/`, como el propio contrato admite. **[V]**
2. **Los `index.md` de subcarpeta.** 24 ediciones en la historia; 0 citas. Son un segundo hop que el
   contrato ni siquiera menciona (solo apunta al index raíz). **[H]** de que no aportan: el
   sub-conteo por routing sí aplica acá, así que no lo cortaría sin medirlo.
3. **El comentario TEMPLATE dentro del `CLAUDE.md` instalado** — 308 chars pagados en cada turno,
   para siempre, diciéndole al agente cómo instalar el kit. Ver B1.
4. **`templates/eval/` no se instala nunca.** `okf_install.py` no lo copia (`SCRIPTS` en la
   línea 67 son solo lint/coldtest/stale) y `README.md:116` lo dice: *"no se instala por defecto"*.
   El diferencial que el roadmap llama *"el único kit que se mide a sí mismo"* **no llega al
   producto**: un usuario que instala OKF no tiene forma de medir su propio ROI. **[V]**

---

## 4. Costo de mantenimiento — el kit **no sabe** si se paga solo

### Lo verificado

- **[V]** Sobre 27 commits que tocan `knowledge/` en este repo: **114 archivos tocados**, de los
  cuales **46 (40%) son andamiaje** (`index.md` 24, `log.md` 13, `roadmap.md` 9). Se crearon 40
  conceptos nuevos → **0,93 ediciones de andamiaje por concepto nuevo**, además del concepto.
- **[V]** Un registro típico son **3 escrituras mínimas** (concepto + `<carpeta>/index.md` + línea de
  `log.md`), y un harvest son 4–6 (ver `24b58ad`: 2 borrados de `_changes/`, 2 decisiones, 2 índices,
  log, roadmap = 8 archivos).
- **[V]** El camino de escritura consume **403 tok/turno** del contrato always-on (§2, 25%) **en
  todos los turnos**, incluidos los de solo lectura. Más el skill que se cargue: `okf-update` 1.386
  tok, `okf-plan` 2.998 tok, `okf-verify` 2.470 tok.
- **[V] Barato de verdad:** el enforcement es determinista y cuesta cero LLM — hook pre-commit
  (`templates/hooks/pre-commit`) y CI (`templates/ci/okf.yml`, *"CERO tokens, cero LLM"*). Buena
  decisión de economía; no la toquen.

### Lo que NO está medido (y es la mitad del balance)

`run-eval.py` corre **solo preguntas de lectura**. No existe ninguna medición de cuántos turnos
cuesta un harvest, un registro de decisión o un keep-alive. **La pregunta "¿el kit se paga solo?" no
se puede contestar con los datos del kit.** **[V]** (por ausencia).

Aritmética disponible, como **[H]** explícita: en el único repo medido a ciegas, el ahorro de lectura
es de ~17 turnos sobre 7 preguntas, **concentrado en una sola**. Si un harvest cuesta ≥4 escrituras
más la lectura del skill (~1.400–3.000 tok), bastan **2–3 eventos de mantenimiento** para consumir
todo el ahorro de lectura de una semana de preguntas. No lo afirmo — señalo que el kit se vende sobre
un balance del que solo tiene un lado.

**Propuesta concreta:** `run-eval.py --mode write`, con un golden-set de *tareas* ("acabamos de
decidir X, registralo"; "terminaste el cambio Y, cerralo") en vez de preguntas, midiendo los mismos
4 números. Es la única forma de cerrar el balance, y reusa todo el harness.

### Un dato a favor del kit que sí se puede afirmar

La ganancia grande de q7 (27→2 turnos) **es exactamente una de auditoría/mantenimiento**: preguntarle
al repo "qué quedó viejo". O sea: **el kit puede pagarse en el lado de escritura antes que en el de
lectura**, y nadie lo midió. Es la hipótesis más interesante que dejan estos datos.

---

## 5. El harness y su juez

### Defectos verificados

| # | Defecto | Evidencia |
|---|---|---|
| J1 | **El juez corre ciego.** `grade_one` llama `claude_json(jp)` **sin `cwd`** → hereda el cwd del harness (el kit), no el repo bajo prueba. No puede verificar ni una afirmación contra el código; solo hace matching contra `expect`. Peor: si decidiera usar tools, grepearía **el repo equivocado**. | `templates/eval/run-eval.py:82` vs `:116` (`claude_json(prompt, cwd=repo)`) |
| J2 | **No hay ground truth que juzgar.** Los `expect` dicen literalmente *"nivel exacto a verificar contra código"*, *"número exacto a verificar contra código"*, *"expect best-effort"*. | `eval/idlerpg/golden-set.adversarial.md:12,17,22`, cabecera |
| J3 | **29% de falsos negativos medidos.** blind2 marcó q4 y q7 `incorrecta`; ambas verificadas correctas a mano. | `eval/idlerpg/scorecard.adversarial.blind2.jsonl` + `eval/COMPARISON.md` ("Meta-hallazgos") |
| J4 | **Falso positivo con premisa falsa** (lo del roadmap): `trampa-ok` a una respuesta con premisa falsa, `incorrecta` a tres correctas. | `knowledge/decisions/0014-future-layer-measured.md:79-81` |
| J5 | **El costo del juez se descarta.** `grade_one` usa solo `j["result"]` y tira `total_cost_usd`/`usage`. En una corrida `--grade`, `cost_usd_total` **subreporta** ~1 llamada por pregunta. | `run-eval.py:82-87` vs `:151-163` |
| J6 | **El modo `nokit` está contaminado y sin usar.** `NOKIT_PRE` *pide* no leer `AGENTS.md`, pero Claude Code lo auto-carga en el prefijo antes de que el agente decida: mide "kit instalado y pedile que lo ignore", no "sin kit". Además **61/61 corridas son `mode=kit`**: nunca se ejecutó. | `run-eval.py:24-25`; conteo sobre los 8 scorecards |

### ¿Es arreglable? Sí, y por orden de retorno

1. **`cwd=repo` en el juez** + prompt que exija verificar contra el código antes de dictaminar. Es
   *un argumento*. Convierte un detector de paráfrasis en un verificador. (Consecuencia: el juez pasa
   a gastar turnos — registralos, arregla J5 de paso.)
2. **Congelar los `expect`** a un hecho chequeable con `archivo:símbolo`. Un `expect` con la palabra
   "verificar" es un bug del golden-set, no del juez. Es lintable en 10 líneas.
3. **Separar dos veredictos**: (a) ¿los hechos son correctos? (b) **¿la respuesta acepta una premisa
   falsa de la pregunta?** J4 es invisible para un prompt que solo pregunta *"¿contiene los hechos
   esperados?"*, porque una respuesta con premisa falsa **puede contener** los hechos esperados.
4. **n=3 y reportar desacuerdo** en vez de un veredicto. Vale para el juez **y para los turnos** (§2).
   Verificar a mano solo los desacuerdos: es lo que `grade.md` ya manda hacer, pero sin un mecanismo
   que lo detecte.
5. **Juez configurable (comando por env var)** para el veredicto cross-vendor que `grade.md` exige y
   el código no soporta (`"claude"` hardcodeado en `run-eval.py:55`). **Esto NO viola la
   [0004](knowledge/decisions/0004-vendor-neutral-no-external-apps.md)**: el harness es tooling de
   desarrollo opt-in que **no se instala** en repos destino, y hacerlo configurable es *menos*
   vendor-lock, no más.

**Sin juez confiable no hay loop — pero el problema mayor no es el juez, es n=1.** Aun con un juez
perfecto, el harness no puede resolver efectos menores a ~3,3 turnos, y todos los mecanismos que
quedan por descubrir son de ese tamaño.

---

## 6. Hallazgos rankeados por (turnos ahorrados / riesgo de romper acierto)

| # | Hallazgo | Turnos ahorrados | Riesgo de acierto | Esfuerzo | Estado |
|---|---|---|---|---|---|
| **B1** | **`CLAUDE.md` instalado con el comentario TEMPLATE.** `okf_install.py:250` copia crudo; `build_agents()` (línea 249) sí recorta. 308 chars ≈ 77 tok/turno de andamiaje, con texto que le dice al agente *"copiá esto a la RAÍZ del repo destino"*. `GUIDE.md:71` promete "shim de 1 línea". El gate no lo caza porque el assert 3k solo busca `OKF:future-layer` y `{{KIT_VERSION}}` (`okf_selfcheck.py:399-406`), y el de autosuficiencia hace `strip_comments` (`:553`) apoyado en una premisa que acá es falsa. | ~0 (77 tok/turno) | **cero** | trivial (1 línea + 1 assert) | **BUG [V]** |
| **B2** | **El presupuesto mide un archivo de tres.** Extender `BUDGET` a `AGENTS.md + CLAUDE.md + Σ descripciones de skills`. Con B1 arreglado: 6.684+11+1.040 = **7.735** → el techo hay que subirlo a ~8.500 **o** recortar §2. La honestidad del número importa más que el número. | 0 | cero | bajo | **[V]** |
| **B3** | **n=1 es menos que el ruido.** Ningún mecanismo futuro se puede validar así. `run-eval.py --repeat N` + reportar mediana y spread. Sin esto, el loop de optimización del kit **no puede continuar**. | habilitante | **negativo** (evita falsos "ganamos") | bajo | **[V]** |
| **B4** | **Mecanismo #5: el code-of-record cierra la búsqueda.** Ver §7. | **~5 turnos/pregunta trap** (31% de las preguntas medidas) | **MEDIO-ALTO** — gatear | medio | **[H] con evidencia** |
| **B5** | **El lado de escritura nunca se midió** (`--mode write`). El kit vende un ROI del que tiene un solo lado. | habilitante | cero | medio | **[V] por ausencia** |
| **B6** | **`log.md` es peso muerto**: 0 citas / 13 ediciones. Pasar a opt-in y sacarlo de `KEEPALIVE_TOKENS`. | ~1 escritura por concepto | bajo (`git log` + `decisions/` cubren) | bajo | **[V]** |
| **B7** | **Arreglos del juez** J1→J5. | habilitante | **negativo** | bajo (J1 es un argumento) | **[V]** |
| **B8** | **`templates/eval/` no se instala.** El diferencial del kit no llega al usuario. Instalarlo con `--with-eval`, o al menos documentar cómo copiarlo. | 0 directo | cero | bajo | **[V]** |
| **B9** | **`nokit` contaminado y sin usar** (J6). Un A/B real tiene que **mover los archivos**, no pedir que se ignoren. | habilitante | cero | bajo | **[V]** |
| **B10** | **Ancla de símbolo en el code-of-record** (enabler de B4): la columna pasa a `archivo` + **símbolo greppable** (`ABYSS_UNLOCKS`, `FINISHER_ANTI_WASTE_RULES`), no `:línea` (que driftea). El template ya lo permite pero no lo pide (`templates/knowledge/_glossary.md`). `grade.md` ya nombra el failure mode ("chunk grande") para páginas del bundle; no existe para archivos de código. | 1–3 turnos en `domain` | bajo (sigue siendo puntero, no valor → ADR 0009 intacto) | bajo | **[H]** |

### Lo que NO propongo (y por qué)

- **Recortar §1.** Es donde vive todo el valor medido (0007/0008). Su costo (922 tok) está
  justificado.
- **Recortar §2 sin más.** Existe por decisión: la
  [0013](knowledge/decisions/0013-installed-material-is-self-sufficient.md) exige que un agente sin
  skills pueda mantener el bundle solo con el contrato. Es una tensión **real y explícita** entre
  autosuficiencia y presupuesto: 403 tok/turno de peaje en todos los turnos de lectura para que
  funcione el caso sin-skills. Si algún día hace falta headroom, esta es la palanca — y hay que
  superseder o acotar la 0013, no editarla en silencio.
- **Bajar el techo de 7.000.** El costo caro es de atención, no de tokens, y no hay forma de medir
  atención con este harness.

---

## 7. Candidato #1 a mecanismo 5

### **"El code-of-record cierra la búsqueda" — autoridad negativa acotada**

**La convención.** Dos piezas:

1. En el glosario, la columna *code-of-record* pasa a llevar **archivo + símbolo greppable**
   (`src/engine/progression/abyssProgression.js` → `ABYSS_UNLOCKS`), nunca `:línea` (driftea) ni el
   valor (ADR 0009).
2. En el contrato, **una frase** (~250 chars, entra en el headroom que queda):
   > *El code-of-record de un término es autoridad también para la **negativa**: si el término no
   > está ahí, no existe — contestá "no existe hoy" citando el archivo que barriste. Una lectura
   > confirmatoria alcanza; no barras el repo buscando una segunda fuente.*

**Por qué es el #1, con la evidencia:**

- **`trap` es la categoría más cara medida**: **6,4 turnos** de promedio sobre **n=19** corridas,
  contra `domain` 5,5 (n=35), `where` 2,8 (n=4), `ops` 1,5 (n=2). Y es **31% de todas las preguntas
  medidas**. **[V]**
- **Las tres preguntas de "probar una negativa" cuestan lo mismo en los tres repos**, con o sin kit:
  idlerpg q1 (AoE) 8–11 turnos, conclave q10 (Stripe) 6, forgeidle q6 (PvP) 6. Ninguna convención
  del kit las toca. **[V]** — leí las tres respuestas: en todas el agente **barre** (grep de
  `aoe|splash|cleave` en todo `src/`, abrir cada hit) para poder afirmar la negativa.
- **Es la mitad que falta de la ADR 0008.** La 0008 declara qué **NO** es autoritativo (`notes/` es
  scratch) y esa fue la palanca grande (q7 27→2). Nunca declaró el dual: **qué SÍ es autoritativo es
  además exhaustivo para su término**. Sin eso, *"src/ manda"* le dice al agente **dónde** mirar pero
  no **cuándo parar**, así que barre `src/` entero.
- **No pelea con ADR 0009.** La 0009 prohíbe contestar **desde el mapa**; esto no da esa licencia:
  la negativa la habilita **una lectura vacía del code-of-record declarado**, o sea el agente sigue
  yendo al código y sigue citando la fuente. Lo que se acota es la **amplitud** de la verificación,
  no su existencia. Es exactamente el trade que `eval/COMPARISON.md` llama "el diseño correcto" en
  q4 (el glosario dio puntero, el agente igual abrió el archivo).

**Ahorro estimado [H]:** q1 de ~9 a ~3–4 turnos; las trap de conclave/forgeidle de 6 a ~3. Sobre el
set adversarial de idlerpg son ~5–6 turnos = **12% del total**, y es justamente la parte donde hoy el
kit no ayuda.

**Riesgo: MEDIO-ALTO, y hay que gatearlo.** Es la misma forma que el falso positivo de q5 en blind V1
(rápido y mal). Mitigaciones dentro de la convención:
- la licencia negativa la da **una lectura vacía del code-of-record**, jamás el mapa;
- la respuesta **debe citar el archivo barrido** (verificable en el scorecard);
- se aplica solo a términos que **tienen** code-of-record declarado — si el glosario no cubre el
  término, no hay licencia (esto además cierra el hueco de cobertura que causó q5).

**Gate obligatorio** (regla dura de `templates/eval/grade.md`): re-correr las 7 adversariales
**n≥3** con el juez arreglado (B7) + verificación a mano de q1/q6/q7. **Un `incorrecta` nuevo lo
mata**, por más que baje el promedio.

**Candidato #2** (por si el #1 no pasa el gate): **B10 solo** — ancla de símbolo sin licencia
negativa. Menos ahorro (1–3 turnos en `domain`) pero riesgo casi nulo: sigue siendo un puntero, y
ataca el residuo real que dejó ADR 0007. La evidencia: con el glosario apuntando al archivo
correcto, q4 igual costó 4/6/7 turnos y q5 4/10 — **el costo residual es intra-archivo, no de
routing**. El glosario resolvió término→archivo; nada resuelve archivo→símbolo.

---

## Anexo — cómo reproducir los conteos

```bash
# presupuesto instalado (read-only, no escribe en ningún repo)
python3 - <<'PY'
import importlib.util
s=importlib.util.spec_from_file_location("i","scripts/okf_install.py")
m=importlib.util.module_from_spec(s); s.loader.exec_module(m); v=m.kit_version()
for n,t in [("AGENTS full",m.build_agents(v,False,"P")),("AGENTS min",m.build_agents(v,True,"P")),
            ("CLAUDE.md",open('templates/CLAUDE.md').read())]:
    print(f"{n:14s} {len(t):6d} chars ~{len(t)//4} tok")
PY

# ruido intra-condición y efecto (§2)
# turnos por scorecard: jq -s 'map(.num_turns)|add' eval/idlerpg/scorecard.adversarial.*.jsonl
# tax de keep-alive (§4)
git log --numstat --format='@@%h' -- knowledge/
```
