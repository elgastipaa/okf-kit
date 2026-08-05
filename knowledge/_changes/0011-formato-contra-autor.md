---
type: Change
status: in-progress
title: Separar el formato del autor — ¿el kit recupera solo lo que un humano escribió a mano?
description: "Tercer brazo sobre the-conclave: un bundle generado por okf-init a ciegas, contra la wiki que escribió el dueño del repo y contra no tener nada."
tags: [okf, eval, alcance]
timestamp: 2026-08-05T00:00:00Z
---

# El problema

El mejor número del kit —**−34% de turnos y 14/15 de acierto contra 10/15**— se midió sobre
`the-conclave` con **la capa que escribió el dueño del repo a mano**. Eso deja la pregunta
importante sin contestar:

> ¿Ganó **el formato OKF**, o ganó **que Gasti sabe su repo y escribió una wiki buenísima**?

Si fue lo segundo, el kit no está vendiendo lo que cree: `okf-init` sobre un repo ajeno no
produciría nada parecido, y la promesa honesta sería "te damos un formato para escribir vos",
no "corré esto y tenés la capa".

# Diseño

Tres brazos, **mismo repo, mismas 5 preguntas, n=3**:

| brazo | estado del repo | quién escribió la capa | estado |
|---|---|---|---|
| **N** | sin front door (`docs/wiki`, `AGENTS.md`, `CLAUDE.md` apartados) | nadie | medido: 7.73 turnos, 10/15 |
| **W** | front door humano presente | el dueño, a mano | medido: 5.07 turnos, 14/15 |
| **K** | sin front door **+ bundle de `okf-init`** | el kit, a ciegas | **este cambio** |

`K − N` = lo que agrega el kit solo. `W − N` = lo que agrega el autor humano. `K` contra `W`
es la respuesta.

**La instalación es ciega de verdad**: corre en un proceso `claude -p` fresco que no vio la
golden set, con la instrucción explícita de no abrir `eval/`. Yo sí conozco las preguntas, así
que no toco el bundle ni contesto las preguntas abiertas que deje el init — el brazo mide
*instalar y soltar*, que es lo que haría un usuario sin nadie al lado.

Rama `okf-bundle` de `the-conclave`, sacada del mismo commit que los otros dos brazos.

<!-- GATE ESCRITO ANTES DE MIRAR EL RESULTADO (decisión 0028). No editar después. -->

# Gate

**Ruido de referencia**: la dispersión intra-condición en este repo es de ~3.5 turnos (sd del
brazo N), o sea un error estándar de la media de **~0.9 turnos** con n=15. Una diferencia de
medias **menor a 1.0 turno se informa como indistinguible**, no como mejora.

**Validación previa a leer** (si algo de esto falla, el scorecard no se lee):
- 15/15 corridas completas, **0 fallidas**.
- `mutated_repo` en falso en las 15.
- El bundle en disco al terminar la medición es byte-idéntico al commiteado.

**Lectura pre-registrada** — cuál de las tres se cumpla es el resultado:

1. **El formato carga el peso**: `|K − W| < 1.0` turno **y** el acierto de K está a lo sumo una
   celda de W (≥13/15). Es el resultado más fuerte posible y por eso el que más hay que
   desconfiar: si sale, se re-lee el bundle buscando por qué no puede ser cierto antes de
   publicarlo.
2. **El kit captura una parte**: K queda entre N y W. Se publica la fracción recuperada
   (`(N−K)/(N−W)`) sin redondearla para arriba.
3. **El valor era el autor**: `K ≥ N − 1.0` turno, o acierto de K ≤ N (10/15). Es un resultado
   **negativo y se publica igual** (0028 §4), y obliga a cambiar lo que el kit promete: pasa a
   ser un formato para que escribas vos, con routing, no una capa que se genera sola.

**Regla anti-autoengaño** (0028 §3): si K baja turnos pero mete errores nuevos —cualquier
`incorrecta`/`inventada`, o más `parcial` que W— **el brazo se rechaza** por más lindo que sea
el promedio. Una respuesta rápida y equivocada es peor que una lenta y correcta.

**Se cuenta aparte, y no como acierto**: cuántas preguntas abiertas dejó el init y si alguna
apunta a algo que la golden set pregunta. Eso mide la **elicitación** —el valor que ya se vio
en `forgeidle`— y es una promesa distinta a la de recuperar hechos.

# Lo que se puede leer sin el scorecard

Medido después de la instalación ciega y **antes** de correr el brazo K, para que no se pueda
acomodar a lo que dé el número.

**Elicitación — 8 preguntas abiertas, y ninguna toca la golden set.** El init dejó 8
`> Pendiente de confirmar:` (CI de la wiki vieja, por qué no hay Supabase de dev, si hay
trabajo activo, si lanzar es la meta, nombres de subclase en el lore, telemetría de loot, y la
Vida como mecánica). **Cero** apuntan a algo que la golden set pregunta, y eso es exactamente
lo esperable: la golden set se armó con cosas que **sí** están en el repo. La elicitación
apunta a un conjunto **disjunto** — lo que nadie escribió nunca. Es evidencia de que recuperar
hechos y sacarle preguntas al dueño son **dos productos distintos**, no el mismo medido dos
veces.

**La 0027 se sostiene en un segundo repo.** Las 8 decisiones quedaron `accepted` +
`origen: dictado`, y las 8 **citan una fuente escrita por una persona** (`docs/01_architecture.md`
"A2"/"A3", `docs/PLAN.md`, los specs de `game-design/new-design/`, el ADR del Arcanista). O sea
que cosechó en vez de fabricar. Queda una espina que **no es un hallazgo probado**: el template
siembra `origen: dictado` pre-rellenado, así que **el valor peligroso es el default** y un
agente que no se detiene a pensar lo copia. Acá salió bien porque el repo tenía las razones
escritas; en un repo que no las tenga, la protección depende de que el agente elija.

**Arreglado mientras esperaba la cuota**: el template ahora viene con `origen: reconstruido`,
así que copiarlo sin elegir **rompe el linter** y obliga a decidir. `dictado` es la única de
las dos que nadie puede auditar después — no puede ser lo que sale gratis por no pensar. El
assert lo prueba de punta a punta (arma el archivo que dejaría un agente y corre el linter),
y su rotura es volver el template a `dictado`.

**Economía de contexto: el contrato instalado pesa 10 433 chars (~2608 tokens en cada turno),
2,1× el `AGENTS.md` de 4886 que escribió el dueño a mano.** `--budget` atribuye bien: 6155 son
prosa del kit (dentro del techo de 7000) y 4278 los agregó el agente en "Reglas duras" y
"Capas NO autoritativas". Nadie enforcea la mitad del usuario —es su plata— pero el brazo K
tiene que ganar **contra ese peso**, no gratis.

# El puntero plausible y equivocado (hallazgo, no resultado)

El primer intento del brazo K salió **inválido por el guard de mutación**: 15/15 corridas
completas, 0 fallidas, pero **una modificó el bundle mientras contestaba**. Se descartó sin
leer los turnos, como manda el gate. Lo que se encontró al revisar *por qué* mutó es más
importante que el brazo:

El init dejó en el glosario que el término **"Clase base"** tiene su code-of-record en
`src/lib/game/data/classes.ts`. **Ese archivo existe** —por eso el error es tan bueno— pero es
otra cosa: son las clases/arquetipos coleccionables de la decisión A1. Las clases base con su
triángulo de counters viven en `subclasses-types.ts`, `combat-tuning.ts` y `combat-engine.ts`,
que es exactamente lo que el agente terminó escribiendo cuando lo corrigió.

Es la **misma falla que la [0027](../decisions/0027-una-razon-reconstruida-no-manda.md), en un
campo que nadie protege**. Ahí el agente fabricaba un *porqué*; acá fabricó una *ubicación*, y
las dos comparten la propiedad que las hace dañinas: son plausibles, son citables y vienen con
la autoridad del bundle. Un puntero equivocado no se lee como error, se lee como dato — y el
que lo sigue paga el desvío sin saber que lo está pagando.

Se nota que costó: esa pregunta llevó 11 turnos hasta que el agente encontró los archivos
reales. Y el kit tiene la contracara buena en la misma escena: **el agente detectó la mentira
contra el código y arregló el bundle**, que es el keep-alive funcionando exactamente como está
diseñado. Para medir es contaminación; para usar es la propiedad más valiosa que tiene.

> Pendiente de confirmar: si esto merece regla propia (¿el linter puede exigir que un
> `code-of-record` exista **y** contenga el término?) o si alcanza con que el keep-alive lo
> corrija al primer uso. Lo segundo es gratis; lo primero ataja al que lee y no escribe.

# Enmienda al gate (declarada, no silenciosa)

El gate de arriba **no se toca**. Lo que cambia es el conjunto de preguntas, y el motivo es
público: el brazo K se invalidó **dos veces seguidas por la misma corrección determinista** en
`q2 rep1`. El bundle recién salido del init no es una condición estable — se arregla solo al
primer uso. Eso obliga a dos cosas:

1. **La condición pasa a ser K′ = el bundle después de una pasada de keep-alive.** Las
   correcciones las hizo el agente ciego mientras contestaba, **no yo**, que conozco la golden
   set. Quedaron commiteadas tal cual.
2. **q2 sale de la comparación, en los tres brazos.** La corrección cae exactamente sobre lo
   que q2 pregunta, así que medirla con el bundle corregido sería inflar el número. Sacarla
   solo del brazo que molesta sería peor: se saca de todos.

Los umbrales se recomputan sobre las mismas 4 preguntas (q1, q5, q8, q10), con los datos que
ya estaban guardados:

| brazo | n | turnos | sd | acierto |
|---|---|---|---|---|
| **N** (sin capa) | 12 | 7.00 | 3.46 | 9/12 |
| **W** (wiki humana) | 12 | 4.92 | 1.44 | 11/12 |

Las tres lecturas pre-registradas se leen contra **estos** números, sin cambiarles la forma.

**Y queda dicho como resultado, no como incidente:** el bundle recién generado por `okf-init`
**no se pudo medir en su estado original**. Dos intentos, misma corrección. Eso es información
sobre el producto — el init entrega algo que todavía no es correcto y necesita un uso para
estabilizarse — y va publicado aunque no favorezca.

# Resultado: gana el autor. Se cumple la lectura 3, la que no conviene

Scorecard válido: 12/12 corridas, 0 fallidas, 0 mutaciones, capa intacta.

| brazo | n | turnos | sd | acierto | ctx tokens |
|---|---|---|---|---|---|
| **N** — sin capa | 12 | 7.00 | 3.46 | 9/12 | 233 533 |
| **W** — wiki humana | 12 | **4.92** | 1.44 | **11/12** | **154 444** |
| **K′** — bundle de `okf-init` | 12 | 7.33 | 3.17 | 10/12 | 242 076 |

- **K′ − N = +0.33 turnos** (2·EE = 2.71) → **indistinguible de no tener capa.**
- **K′ − W = +2.42 turnos** (2·EE = 2.01) → **distinguiblemente peor que la wiki humana.**
- En contexto leído, K′ (242k) tampoco mejora a N (233k); W lee **154k**.

Se cumple la **lectura 3** del gate: *el valor era el autor*. El −34% que el kit venía citando
como su mejor número **no lo produjo el formato OKF: lo produjo que Gasti escribió su wiki**.

Por pregunta (mediana de turnos) se ve dónde:

| | q1 ATK/DEF | q5 Vigor | q8 por qué flags | q10 trampa |
|---|---|---|---|---|
| N | 11.0 | 6.0 | 6.0 | 5.0 |
| W | **4.0** | 6.0 | 5.0 | 4.0 |
| K′ | 11.0 | 8.0 | **3.0** | 6.0 |

K′ **gana en una sola**: `q8`, el "por qué" — que es donde viven las decisiones, y donde el
init cosechó razones que una persona había escrito. Justo el eje que la 0027 trabajó. En
recuperación de hechos (`q1`) empata con no tener nada.

## La causa es concreta, no un misterio de calidad

La wiki que gana tiene `docs/wiki/_generated/state.md`: **37 líneas emitidas por un script
desde el código** (`scripts/wiki-gen.mjs`), con `wiki:check` fallando en CI si driftea. Dice
qué flags están ON/OFF, cuántas subclases hay y cuáles, qué modelos existen. **Es fiel por
construcción: no puede mentir.**

El bundle de `okf-init` **no generó nada**. Y el puntero equivocado que costó 11 turnos era
**imposible** en un archivo generado: `subclasses-types.ts` es exactamente la fuente que
`state.md` cita.

**El kit conoce la idea y no la instala.** `GUIDE.md` la enseña —"hechos volátiles: generalos,
no los copies", con el patrón `_generated/state.md` + `gen`/`check`—, `templates/knowledge/_generated.md`
existe… y `templates/skills/okf-init/SKILL.md` **no la menciona ni una vez**. El procedimiento
que el agente sigue de verdad se saltea la mejor idea que el kit tiene escrita.

## Qué cambia

- **El número que el kit publica.** El −34% pasa a ser *"lo que gana una capa bien escrita por
  una persona"*, no *"lo que gana instalar el kit"*.
- **La promesa del `init`.** Hoy entrega, medido: prosa que **no** acelera la recuperación de
  hechos, **sí** preserva los porqués que alguien escribió (`q8`), preguntas abiertas útiles, y
  al menos un puntero plausible y equivocado que se corrige al primer uso.
- **El candidato con causa medida:** que `okf-init` produzca la capa generada. Es el único
  cambio de esta lista que ataca la brecha donde se midió.

# Tareas

- [x] Rama `okf-bundle` con el front door humano apartado
- [x] Gate escrito antes de mirar
- [ ] Instalación ciega de `okf-init` (corriendo)
- [ ] Brazo K: `--repeat 3 --grade` sobre las mismas 5 preguntas
- [ ] Leer contra el gate y publicar, salga lo que salga
- [ ] Cosechar: decisión sobre el alcance del kit + roadmap
