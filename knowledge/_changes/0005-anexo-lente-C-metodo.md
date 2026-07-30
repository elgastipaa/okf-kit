# Lente C — El agujero de producto: lineamientos para PROGRAMAR con IA

Revisión en frío sobre `okf-kit` v0.7.3 · solo lectura · 2026-07-30

---

## Veredicto

**Agujero real, pero no el que la pregunta sugiere.** El kit ya cruzó la frontera hacia
metodología —`okf-plan` son 215 líneas de método puro— y lo hizo bien. Lo que falta no es
"lineamientos para programar": es que **el kit gobierna todo el ciclo de un cambio EXCEPTO
el código**. Especifica antes (`_changes/`), cosecha después (harvest), audita los papeles
(4 niveles, 5 capas de enforcement, un revisor en frío) — y sobre "¿esto que escribí anda?"
tiene exactamente **una casilla** (`templates/knowledge/_change.md:60`), que además **se
borra en la instalación mínima**. Peor: el contrato le enseña al agente que "verificar"
significa *lintear el bundle*. Para un vibecoder cuyo fracaso número uno es "la IA dijo que
estaba listo y no estaba", eso no es neutral: es una ceremonia de cierre que se siente como
verificación y es más barata que verificar.

---

## 1. Qué dice hoy el kit sobre método (VERIFICADO)

El kit dice **bastante** sobre método. Todo concentrado en un solo archivo, y ese archivo es
opcional.

### 1.1 Tamaño de las tareas (sí, existe, y es bueno)

| Qué dice | Dónde |
|---|---|
| "Un cambio sano tiene **una intención que se dice en una frase**". Señales de que hay que partirlo: el alcance parece features sin relación, la mitad podría entregarse sola, **"revisarlo llevaría una tarde"**. "Partir es barato; un cambio gigante que nunca cierra es el que se abandona." | `templates/skills/okf-plan/SKILL.md:73-77` |
| **Límite de WIP = 3**: "Si 'Ahora' ya tiene 3 cambios activos, **no abras otro**: proponé al usuario terminar o repriorizar uno antes." | `templates/skills/okf-plan/SKILL.md:146-147` |
| "El roadmap es de una pantalla… un backlog infinito es otro tipo de rot." | `templates/skills/okf-plan/SKILL.md:212-213` |

Notá el criterio de partición: **"revisarlo llevaría una tarde"**. Es *casi* la regla anti-diff-de-800-líneas — pero está escrita en clave de "el doc no cierra", no de "el humano no lo va a leer".

### 1.2 Cuándo abrir un `_changes/`

| Umbral | Dónde |
|---|---|
| "Un typo, un fix chico o un ajuste puntual no necesitan doc; si el trabajo **tiene más de un paso, toca varios archivos o va a cruzar una sesión**, sí." | `templates/skills/okf-plan/SKILL.md:41-44` |
| Disparador en el contrato (no requiere que el usuario lo pida): "Te piden algo no trivial → **antes de codear**, acordá con el usuario qué tiene que pasar para considerarlo listo y qué queda afuera." | `templates/AGENTS.md:80-81` |
| **Explorar antes de comprometer**: pedido vago → "no abras un cambio todavía… Explorar no crea archivos." | `templates/skills/okf-plan/SKILL.md:63-69` |
| El propio kit reconoce que el umbral puede estar mal: "candidato: que sea *'¿podría no terminar en esta sesión?'* en vez de *'¿es no trivial?'*. No se cambia hasta medirlo." | `knowledge/decisions/0014-future-layer-measured.md:68-72` |

### 1.3 Definición de "hecho" y anti-scope-creep

| Qué dice | Dónde |
|---|---|
| El *Resultado esperado* se escribe **con el usuario**, como escenarios `CUANDO … ENTONCES …`, **incluyendo el caso que falla** ("ahí es donde viven los bugs"). | `templates/skills/okf-plan/SKILL.md:140-145`, `templates/knowledge/_change.md:24-37` |
| "**Nada que salga de 'Fuera de alcance' entra al código.**" | `templates/skills/okf-plan/SKILL.md:155-156` |
| "El resultado esperado **SÍ manda** sobre '¿está terminado?'… **Bajar la vara se hace renegociando con el usuario y editando el doc, nunca en silencio ni 'interpretando' que ya está.**" | `templates/skills/okf-plan/SKILL.md:196-201` |
| Idea fuera de alcance → una línea en "Después", **no la implementes de paso**. | `templates/skills/okf-plan/SKILL.md:51-53` |

`okf-plan:196-201` es, para mí, la mejor línea de método de todo el kit: nombra exactamente el
failure mode del agente que se auto-aprueba.

### 1.4 Qué NO delegarle a la IA

| Qué dice | Dónde |
|---|---|
| Resultado esperado y Fuera de alcance **se acuerdan, no se asumen**. "No inventes visión, prioridades ni criterios de 'hecho': preguntá." | `templates/skills/okf-plan/SKILL.md:140-141, 214` |
| Violación de algo normativo: **reportar las dos salidas al usuario**, no arreglar de prepo. | `templates/AGENTS.md:58-62`, `reference/verification.md:235-237` |
| "Si algo no está claro… **preguntale al usuario**; no asumas." | `templates/AGENTS.md:44-45` |

### 1.5 Cuando el agente se va por las ramas o alucina

Acá el kit es sorprendentemente fuerte, y **está medido**:

| Qué dice | Dónde |
|---|---|
| "Este archivo es un **MAPA, no la respuesta**… Si una sección de acá *parece* contestarla, es coincidencia — verificá en la fuente." | `templates/AGENTS.md:47-52` |
| El caso medido: un agente contestó una regla de combate desde la sección de capas no-autoritativas del `AGENTS.md` porque *sonaba* a respuesta. | `GUIDE.md:236-242` |
| El caso medido inverso: un agente anotó en el roadmap una feature "nueva" que el repo **ya tenía implementada**, envenenando el contexto de todas las sesiones siguientes → de ahí el "chequeá primero si ya existe en el código". | `templates/skills/okf-plan/SKILL.md:55-61`, `knowledge/decisions/0014-future-layer-measured.md:44-48` |
| La lección estructural: "**Cualquier capa que parezca autoritativa y sea más barata de leer que la fuente invita a saltearse la fuente.**" | `knowledge/decisions/0014-future-layer-measured.md:51-56` |

Guardá esa última cita. Es el argumento que el propio kit se hace, y en §4 se la voy a aplicar
a él.

### 1.6 Cómo revisar lo que la IA escribió

Existe y es el mecanismo más nuevo del kit (v0.7.2, decisión `0021`): el subagente
`okf-reviewer` con contexto fresco, sin permiso de editar, con consigna refutatoria
(`templates/agents/okf-reviewer.md`). Tres propiedades explícitas, ninguna opcional
(`knowledge/decisions/0021-la-auditoria-no-se-auto-aprueba.md:37-44`).

**Pero su alcance está acotado por escrito al bundle**: `templates/agents/okf-reviewer.md:54-62`
("Qué NO hacés") y `0021:61-62`. Nivel 2 = *¿el concepto miente sobre el código?*; Nivel 4 =
*¿el código viola una decisión aceptada?*. **Ninguno de los dos es "¿este diff está bien / rompió
algo?"**.

### 1.7 El `DEVELOPING.md` — sabiduría kit-only que NO está en `templates/`

Esto es un hallazgo por sí solo. El proceso con el que el kit se desarrolla contiene el método
más duro del repo, y **casi nada de eso viaja al repo destino**:

| Regla del kit | Dónde | ¿Exportada? |
|---|---|---|
| "**Cada fix se testea adversarialmente antes de darlo por hecho** — la lección de esta historia: dos 'arreglos' metieron regresiones." | `AGENTS.md:26-28` (raíz) | **No.** Nada equivalente en `templates/` |
| Gate de release: 4 suites de roturas antes de bumpear versión | `DEVELOPING.md:14-20` | **No** |
| "Un **assert sin su rotura probada es decoración**" | `DEVELOPING.md:103-110` | **No** |
| Cold-review de 4 lentes para cambios grandes (A consistencia · B completitud · **C correctness: correr los scripts/hook contra fixtures buenos/malos** · D dogfood en frío) | `DEVELOPING.md:52-61` | **Parcial**: solo el rol revisor, y solo para Niveles 2 y 4 del bundle (`0021`) |
| Enforcement cableado para que el gate no dependa de la memoria (CI + hook) | `DEVELOPING.md:65-76` | **Sí**, pero apuntado al bundle |

El kit se aplica a sí mismo una disciplina de verificación de **código** que no le da a nadie.
`AGENTS.md:26` de la raíz existe porque el kit se rompió dos veces "arreglando" cosas — es
literalmente la cicatriz del vibecoder, y se quedó adentro.

---

## 2. Los fracasos típicos del vibecoder: cuáles son atacables con markdown+git

| Fracaso | ¿Lo cura el contexto ordenado? | ¿Atacable con markdown+git (ADR 0004)? | Veredicto |
|---|---|---|---|
| **La IA rompe lo que andaba** | No | **Sí, y barato.** Markdown puede obligar a correr los chequeos del repo antes de decir "listo"; git puede recordarlo en el hook. Lo único que falta es que el kit **sepa cuáles son** esos chequeos — que es un hecho del repo, o sea, contexto | **El agujero. Ver §4** |
| **No tener tests** | No | **Parcialmente.** Markdown no escribe tests. Pero sí puede (a) hacer que el agente pregunte "¿cómo sabés que anda?" en el init y (b) **registrar la respuesta** para que no se redescubra cada sesión. El slot existe y está vacío: `templates/knowledge/_runbook.md:2-3` dice "build, **test**, deploy" y su ejemplo de título es literalmente *"Correr el smoke test"* (`:7`) — pero `runbooks/` es 5º de 6 en la prioridad de siembra (`GUIDE.md:204-207`) y el instalador no crea la carpeta (`templates/skills/okf-init/SKILL.md:89`) | **Atacable por el borde: registrar, no crear** |
| **Aceptar diffs de 800 líneas sin leerlos** | No | **Débil.** El right-sizing ya existe (`okf-plan:73-77`) pero en clave "el doc no cierra". Un hook que bloquee por tamaño de diff sería tooling nuevo obligatorio → choca con `0004` y con el no-goal del roadmap (`knowledge/roadmap.md:70-72`) | **No proponer.** El máximo honesto es reencuadrar la regla que ya existe |
| **La deuda se acumula sin que nadie la vea** | No | **No.** Ver deuda de código exige leer código; `okf_stale.py` rankea drift de *documentos*, no de código. Cualquier cosa que lo ataque cuesta tokens por definición | **Fuera de alcance, correctamente** |
| **Perder el hilo cuando se corta el contexto** | **Sí — y está medido**: "¿qué sigue?" cae de 12.3 a 4.0 turnos, rangos sin solaparse (`0014:22-29`) | Ya resuelto | **Cubierto.** El resto ya está en el roadmap ("Estado de sesión en vivo", `knowledge/roadmap.md:37-38`) |

---

## 3. La frontera: ¿dónde termina ingeniería de contexto y empieza metodología?

**La pregunta está mal planteada, porque el kit ya cruzó.** Y lo dice él mismo:
`reference/spec-driven-interop.md:38-58` enumera "**cinco ideas** adoptadas" de la filosofía SDD —
acordar el resultado antes de codear, no documentar de más, fluido no waterfall, explorar antes
de comprometer, el código no puede contradecir lo decidido. Eso es metodología de desarrollo, no
ingeniería de contexto. Y `0021` agregó un rol de revisión.

Los no-goals del roadmap **se sostienen** y no los refuto:

- **Los otros tres roles de harness-sdd** (`knowledge/roadmap.md:61-63`): correcto. `0021:29-31`
  argumenta que de los cuatro, el único que pagaba era el revisor — el resto es ceremonia de
  equipo grande. Nada de lo que propongo agrega un rol.
- **Spec-driven completo con specs vivas por capability** (`knowledge/roadmap.md:68-70`,
  `reference/spec-driven-interop.md:69-71`): correcto. "El kit apuesta a que el comportamiento se
  lee del código." Nada de lo que propongo agrega specs.
- **Tooling nuevo obligatorio** (`knowledge/roadmap.md:71-72`): correcto. Nada de lo que propongo
  agrega tooling.

**Dónde SÍ está la frontera, entonces.** La regla que el kit debería usar, y que hoy aplica por
intuición: *si es un hecho de este repo que solo el usuario sabe, es contexto; si es una técnica
general de ingeniería, no.*

- "Escribí tests unitarios antes del código", "hacé PRs chicos", "usá feature flags" →
  **metodología general**. Es stack-specific, hay montañas escritas, y no cabe en markdown+git
  sin volverse una guía de estilo. **El kit no debe cruzar acá.** Correcto no-goal, hoy implícito.
- "En **este** repo, para saber si algo anda se corre `npm run check`, y el login hay que probarlo
  a mano porque no hay e2e" → **contexto puro**. No se deduce de ninguna fuente (es exactamente el
  criterio de la regla de oro, `GUIDE.md:167-170`), es lo primero que un compañero nuevo pregunta,
  y el kit **no lo captura**.

Esa segunda línea es la que falta, y no cruza ninguna frontera: es un concepto faltante del
bundle, no una metodología nueva.

---

## 4. Verificación: la asimetría (el hallazgo más grande)

### 4.1 Todo lo que el kit llama "verificar" verifica papeles

| Mecanismo | Qué verifica | Cita |
|---|---|---|
| Contrato §3, **"Antes de cerrar la tarea — verificá"** | `okf_lint.py knowledge` + actualizar el bundle | `templates/AGENTS.md:128-131` |
| Pre-commit hook | (1) conformidad del bundle staged — **bloquea**; (2) "cambió código pero knowledge/ no" — avisa; (3) `timestamp` sin bumpear — avisa | `templates/hooks/pre-commit:11-14` |
| CI | `okf_lint.py knowledge`, y solo dispara con `paths: ["knowledge/**", …]` | `templates/ci/okf.yml:15-17,31-32` |
| Nivel 1 | estructura del bundle | `reference/verification.md:24-75` |
| Nivel 2 | calidad del bundle / drift descriptivo | `reference/verification.md:79-141` |
| Nivel 3 | ¿un agente en frío entiende el bundle? | `reference/verification.md:145-200` |
| Nivel 4 | ¿el código viola una **decisión aceptada**? | `reference/verification.md:204-241` |
| `okf-reviewer` | Niveles 2 y 4, nada más — explícito | `templates/agents/okf-reviewer.md:54-62` |
| Las "5 capas de enforcement" | las cinco apuntan al bundle | `reference/maintaining.md:76-89` |

**El Nivel 4 es el único que abre el código, y solo para chequear conformidad con ADRs.** Ningún
mecanismo del kit pregunta jamás *"¿esto anda?"*.

### 4.2 Lo único que existe, y por qué no alcanza

Hay exactamente **una** línea en todo el material instalado que le pide al agente probar el
código:

> `- [ ] Verificado el "Resultado esperado" (probado de verdad, no asumido)`
> — `templates/knowledge/_change.md:60`, repetido en `templates/skills/okf-plan/SKILL.md:131`

Tres problemas, en orden de gravedad:

1. **Vive en la capa de futuro, que es opcional.** En la instalación **mínima** el bloque
   `OKF:future-layer` de `templates/AGENTS.md:132-136` se borra y `_change.md` ni se instala. El
   contrato mínimo queda con §3 = "corré el linter del bundle" y **cero** instrucción de tocar el
   código.
2. **La mínima se instala justo para quien más lo necesita.** `GUIDE.md:111-112`: *"No, o 'quiero
   que vayas directo al código' → mínimo"*. El usuario que declina la ceremonia es el vibecoder
   puro — y es al que el kit le saca la única casilla que menciona probar.
3. **Es un checkbox sin método ni datos.** "Probado de verdad" no dice con qué. Si el repo tiene
   `npm test`, el agente lo tiene que descubrir; si no tiene nada, no hay nada escrito que se lo
   diga y el agente completa el hueco con criterio.

### 4.3 Por qué esto es peor que la simple ausencia (HIPÓTESIS, con el argumento del propio kit)

El contrato pone un encabezado que dice **"Antes de cerrar la tarea — verificá"** y debajo pone
lintear markdown. Un agente que corre `okf_lint.py`, ve `0 errores` y cierra la tarea **cumplió
el contrato al pie de la letra** y no ejecutó una sola línea del proyecto.

Ese es, palabra por palabra, el mecanismo que el kit ya diagnosticó en `0014:51-56`:

> "**Cualquier capa que parezca autoritativa y sea más barata de leer que la fuente invita a
> saltearse la fuente.**"

Acá la "capa barata" es el ritual de cierre y la "fuente" es la ejecución real. Es la misma
trampa, un nivel más arriba. Y el kit ya sabe que esto no es un problema de agentes malos:
`0014:51-53` remarca que quien cometió el error medido fue **el propio autor de la medición**.

**Contra-evidencia, para ser justo:** `0014:31-34` registra que un agente en frío haciendo un
harvest *"corrió los smokes antes de dar nada por cerrado"* y renegoció los puntos del spec que
la realidad no cumplía. O sea: a veces pasa igual. Pero fue con la instalación **completa** (con
la casilla de `_change.md:60`), n=1, y en un conejillo que **ya tenía smokes escritos**. No
generaliza al repo del vibecoder, que es justo donde no hay smokes ni nadie los nombró.

### 4.4 La asimetría en una frase

> El kit le enseña al agente a **hacer verificable la documentación del repo**. No le enseña a
> **hacer verificable el repo**, ni le pregunta al usuario cómo ya lo es.

---

## Hallazgos rankeados

| # | Sev | Hallazgo | Evidencia |
|---|---|---|---|
| 1 | **Blocker de producto** | El contrato define "verificar" como lintear el bundle, en la sección titulada "Antes de cerrar la **tarea**". Ningún mecanismo del kit pregunta si el código anda | `templates/AGENTS.md:128-131`; `templates/hooks/pre-commit:11-14`; `templates/ci/okf.yml:15-17`; `reference/verification.md:8-13` |
| 2 | **Blocker de producto** | La única casilla que pide probar el código está en la capa opcional, y la mínima —la que se instala a quien dice "andá directo al código"— la borra | `templates/knowledge/_change.md:60`; `templates/AGENTS.md:132-136`; `GUIDE.md:111-112` |
| 3 | **Major** | El bundle nunca captura **cómo este repo demuestra que anda**. El slot existe (`_runbook.md` dice "build, test, deploy", ejemplo: "Correr el smoke test") pero `runbooks/` es 5º de 6 en prioridad y el instalador no lo siembra | `templates/knowledge/_runbook.md:2-3,7`; `GUIDE.md:204-207`; `templates/skills/okf-init/SKILL.md:89` |
| 4 | **Major** | El método más duro del repo es kit-only: "cada fix se testea adversarialmente", el gate de roturas, "un assert sin su rotura probada es decoración", la lente C del cold-review. Nada de eso viaja | `AGENTS.md:26-28`; `DEVELOPING.md:14-20,52-61,103-110` |
| 5 | Minor | El right-sizing ya dice "revisarlo llevaría una tarde" pero encuadrado como "el doc no cierra", no como "el humano no va a leer el diff". Reencuadre barato, sin texto nuevo | `templates/skills/okf-plan/SKILL.md:73-77` |
| 6 | Info | Lo que el kit **sí** cubre bien de método (sizing, WIP=3, explorar antes de comprometer, no bajar la vara en silencio, anti-scope-creep, anti-alucinación medido) está todo en `okf-plan`, que es opcional | §1 completa |

---

## 5. La propuesta mínima

**Reencuadre:** no propongo "lineamientos de programación". Propongo capturar **un hecho del
repo que hoy el kit no pregunta** —*cómo este proyecto demuestra que anda*— y apuntar el ritual
de cierre que ya existe hacia él. Es un concepto faltante del bundle, no una capa nueva.

No agrega tooling (`0004` OK), no agrega roles (`0021` OK), no agrega specs
(`spec-driven-interop.md:69-71` OK), y **no crea una segunda fuente de verdad**.

### Pieza A — el hecho, sembrado como concepto (fuente canónica)

**Dónde vive canónicamente:** `knowledge/runbooks/checks.md` en el repo destino, `type: Runbook`,
sembrado por `scripts/okf_install.py` con `{{placeholders}}` — **exactamente el tratamiento que
ya recibe `roadmap.md`** (`scripts/okf_install.py:186-187,258`; `templates/skills/okf-init/SKILL.md:94-100`).
Es el único artefacto nuevo, y no es un artefacto del kit: es un concepto del repo del usuario.

Contenido sembrado (nuevo template `templates/knowledge/_checks.md`):

```markdown
---
type: Runbook
title: Cómo se comprueba que {{PROJECT_NAME}} anda
description: "Los chequeos que hay que ver pasar antes de dar un cambio por terminado."
tags: [ops, verificacion]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Antes de decir "listo"

{{Los comandos exactos, en orden. Ej:}}
```bash
npm run lint && npm test
```

# Lo que NO cubren (se mira a mano)

{{Lo que ningún comando prueba y hay que abrir y mirar. Ej: "el login con Google —
no hay e2e; entrá a /login y probalo". Si el repo no tiene NINGÚN chequeo
automático, decilo acá explícitamente y listá qué se mira a mano: un repo sin
chequeos es un hecho del repo, y no registrarlo hace que cada sesión lo
redescubra — o que un agente declare "listo" sin haber mirado nada.}}

# Cuánto tarda

{{Si algo tarda minutos, decilo: es la razón por la que se saltea.}}
```

Justificación de que el archivo se siembre **siempre** (no solo si hay chequeos): un repo sin
chequeos es información valiosa y hoy invisible. Y el riesgo conocido —sembrar un archivo con
placeholders sin completar es peor que no tenerlo (`0014:36-43`, `okf-init:96-99`)— se mitiga
igual que con el roadmap: el reporte final del instalador lo lista como pendiente.

### Pieza B — el contrato apunta (208 chars, la única prosa nueva por turno)

En `templates/AGENTS.md`, **§3**, como primera línea de la sección (antes de la línea del
linter), **fuera de los marcadores `OKF:future-layer`** — el punto entero es que sobreviva a la
instalación mínima:

```markdown
**Si tocaste código:** corré los chequeos del repo —[`knowledge/runbooks/checks.md`](knowledge/runbooks/checks.md)— y no declares "listo" sin verlos pasar. Si no hay ninguno, decilo; no lo supla tu criterio.
```

La última cláusula es la que hace el trabajo: prohíbe explícitamente el movimiento por defecto
del agente, que es rellenar el hueco con su propio juicio.

### Pieza C — quién apunta a quién (anti-deriva)

| Archivo | Qué dice | Rol |
|---|---|---|
| `knowledge/runbooks/checks.md` (repo destino) | **los chequeos concretos** | **canónico** (el hecho) |
| `templates/AGENTS.md` §3 | la obligación de correrlos al cerrar | **canónico** (la regla) |
| `templates/knowledge/_change.md:60` / `okf-plan:131` | "Verificado el Resultado esperado (probado de verdad, no asumido)" | ya existe, **no se toca** — es compatible y más específico |
| `GUIDE.md` §4A + `okf-init` §3 | sembrarlo preguntándole al usuario | puntero al procedimiento |
| `reference/verification.md` | **no se toca**. Sus 4 niveles siguen siendo del bundle | sin cambios |

Nada se re-statea. La única regla nueva ("corré los chequeos antes de cerrar") vive en un solo
lugar: el contrato.

### Pieza D — la siembra (~530 chars en `GUIDE.md`, se leen una vez, en el init)

En `GUIDE.md` §4 A, después de la lista de prioridades del perfil Código:

```markdown
**El primer runbook es `runbooks/checks.md`: cómo este repo demuestra que anda.** Es el dato
que más falta le hace a un agente *para no romper nada* y el que menos se deduce de la fuente:
preguntale al usuario qué corre él antes de dar algo por bueno (un `npm test`, un script, abrir
la página y hacer login) y escribí el **comando exacto**. **Si no hay nada, escribilo igual
diciendo que no hay nada y qué se mira a mano** — un repo sin chequeos es un hecho del repo, y
dejarlo sin registrar hace que cada sesión lo redescubra o, peor, que un agente declare "listo"
sin haber mirado.
```

Y una línea en `templates/skills/okf-init/SKILL.md` §4, junto a los otros `{{placeholders}}`.

### El costo de contexto, explícito

| Dónde | Costo | Cuándo se paga |
|---|---|---|
| **Contrato `AGENTS.md`** | **+208 chars ≈ +52 tokens** | **Cada turno de cada sesión, para siempre** |
| `GUIDE.md` | ~+530 chars | Una vez, en el init |
| `templates/knowledge/_checks.md` | ~700 chars | Nunca (es un template; el linter ignora `_*`) |
| `knowledge/runbooks/checks.md` en el destino | ~400 chars | Bajo demanda, cuando el agente va a cerrar |

**El presupuesto está al 96%: hoy son `6692/7000` chars** (medido reproduciendo el cálculo de
`scripts/okf_selfcheck.py:262-270`), o sea **308 chars libres**. Sin compensación, la propuesta
deja `6900/7000` — pasa el gate pero se come el 68% del margen restante, y `0021:52-55` dice que
*"cualquier capa nueva del kit tiene que cumplir"* no hacer crecer el contrato.

**Recorte compensatorio propuesto** (`templates/AGENTS.md:147-149`, no lo cubre ningún assert del
selfcheck, verificado):

```diff
-Son **vendor-neutral**: corren como skills de Claude Code *o* los sigue cualquier agente
-leyendo su procedimiento (si no se usa Claude Code, están en `docs/okf/<nombre>.md`).
+Si no se usa Claude Code, están en `docs/okf/<nombre>.md`.
```

Se va la explicación de *por qué* los procedimientos son vendor-neutral —que es prosa para un
humano, no algo sobre lo que el agente actúe— y queda el único dato accionable: dónde están.
Ahorra 116 chars.

**Neto: +92 chars ≈ +23 tokens por turno. Total `6784/7000`, y el margen libre pasa de 308 a
216.** Ese es el precio honesto de la propuesta: veintitrés tokens por turno y un tercio del
margen que quedaba.

---

## Lo que decidí NO proponer, y por qué

- **Ampliar `okf-reviewer` para que revise diffs.** Viola directamente `0021:61-62` (*"Ampliar su
  alcance sería pagar tokens sin comprar nada"*) y sería el rol `implementer/reviewer` de
  harness-sdd que el roadmap declara no-goal. Habría que superseder la 0021, y no tengo evidencia
  que lo justifique.
- **Un hook que bloquee por tamaño de diff o que corra tests.** El hook no puede saber el comando
  sin configuración = tooling nuevo obligatorio (`0004`, `knowledge/roadmap.md:71-72`). Parsear
  `checks.md` desde shell para extraer comandos sería frágil y ejecutar prosa del usuario es una
  mala idea. **El hook se queda como está.**
- **Una sección de "buenas prácticas de desarrollo con IA".** Es exactamente lo que el kit debe
  no ser: prosa general, no verificable, que se paga en cada turno y se skimea
  (`templates/AGENTS.md:5-10`).
- **Exportar el gate de release del `DEVELOPING.md`.** Tentador (hallazgo #4), pero es proceso de
  mantenedor de una librería, no de un vibecoder con un juego. La pieza transferible de ahí —
  *"no des un fix por hecho sin probarlo"*— ya queda cubierta por la Pieza B.

---

## Nota de método de esta revisión

Todo lo marcado VERIFICADO tiene `path:línea` y fue leído en esta sesión. Lo único marcado
**HIPÓTESIS** es §4.3 (que el ritual de cierre *desplace* activamente la verificación real, no
solo que la omita): el mecanismo lo argumenta el propio kit en `0014:51-56`, pero no está medido,
y hay contra-evidencia parcial en `0014:31-34`. Si se quiere cerrar, el instrumento ya existe:
`templates/eval/run-eval.py` con un golden-set que incluya una tarea de código y mida si el
agente ejecutó algo antes de decir "listo" — leyendo las respuestas a mano, porque el juez
automático no sirve para preguntas de comportamiento (`0014:79-81`,
`knowledge/roadmap.md:53-54`).
