# Calificar acierto (la 4ª columna)

Tokens sin acierto miente: optimizar hacia respuestas vagas baja tokens y empeora el kit.
Por eso cada corrida debería tener una columna de **acierto**.

## Automático (`--grade`)

`run-eval.py --grade` llama a un **juez** (`claude -p`) por corrida, **parado en el repo bajo
prueba** (`cwd=repo`) y con la consigna de verificar contra el código antes de dictaminar.
Devuelve **dos** veredictos.

**Hechos** — contra el `expect` del golden-set:

| etiqueta | significa |
|---|---|
| `correcta` | contiene los hechos esperados **y** cita la fuente correcta |
| `parcial` | algo bien, falta un hecho clave o no citó la fuente |
| `incorrecta` | hechos equivocados, o **inventó** |
| `trampa-ok` | era una `trap` y el agente admitió "no está documentado" |

**Premisa** — sobre la pregunta, no sobre la respuesta:

| etiqueta | significa |
|---|---|
| `premisa-ok` | no había premisa falsa, o el agente la corrigió |
| `premisa-falsa-aceptada` | la pregunta daba por sentado algo que en el código no existe, y el agente **le siguió la corriente** |

Aprueba = `correcta` ∪ `trampa-ok`, **y** `premisa-ok`. El resumen cuenta los primeros como
`aciertos` y los segundos aparte, en `premisas_falsas_aceptadas`.

**Por qué son dos y no uno:** una respuesta que acepta una premisa falsa **puede contener
igual todos los hechos del `expect`**, así que un juez que solo pregunta "¿están los hechos?"
la aprueba. Es el agujero por el que este kit ya vio pasar una respuesta con premisa falsa
puntuada como buena.

**El juez cuesta y ese costo se cuenta.** Una corrida `--grade` es ~1 llamada extra por
corrida; el resumen la suma en `cost_usd_total` y la desglosa en `cost_usd_juez`. Un
instrumento que no se mide a sí mismo subreporta lo que mide.

Un `expect` que dice "a verificar contra código" no es ground truth, es una nota: el juez
tiene instrucción de que ante la duda **manda el código**. Congelar los `expect` a un hecho
chequeable (`archivo:símbolo`) es trabajo del golden-set, no del juez.

## El falso positivo: rápido Y mal (por qué `--grade` no es opcional)

El modo de falla más peligroso no es la respuesta lenta — es la **rápida y equivocada**. Una
capa de contexto puede hacer que un agente conteste en 1 turno citando una sección del
`AGENTS.md` que *suena* a la pregunta, **sin verificar el código**. Midiendo solo turnos, eso
parece una mejora; es una regresión de correctitud disfrazada.

> Caso real: preguntar "¿cuál es la regla anti-waste?" (una mecánica de combate) → el agente
> matcheó "anti-waste" con la sección *"no reconcilies basura"* del contrato y respondió mal en
> 1 turno (vs 5 turnos y correcto sin la capa).

**Regla dura del loop:** una mejora de turnos que introduce **un `incorrecta` o una
`premisa-falsa-aceptada` nuevos se rechaza**, por más que baje el promedio. Por eso cada
iteración corre `--grade` y compara acierto, no solo turnos/tokens.

## Preguntas de "por qué": el fallo grave es inventar, no errar

Un "¿por qué X?" **no se puede verificar contra el código** — el código no contiene el porqué.
El ground truth lo da una persona, y eso cambia cómo se juzga:

| veredicto | significa |
|---|---|
| `correcta` | coincide con la razón que dio el humano |
| `no-hay-razon-ok` | la respuesta correcta era **"no hay una razón registrada"** y el agente lo admitió |
| `inventada` | dio una explicación **plausible pero falsa**: no es la razón del humano, y no había ninguna registrada |
| `incorrecta` | contradice la razón real |

**`inventada` es el veredicto que importa.** En un repo real, buena parte de las decisiones no
las tomó nadie deliberadamente: las tomó una IA y no las escribió. La respuesta correcta a esas
es *"no hay razón registrada, habría que preguntar"*, y un agente que produce una explicación
razonable —permisos, compatibilidad, migración gradual— **falla**, por más que suene bien. Es
el mismo modo de falla que el falso positivo de acierto, un nivel más arriba: en vez de una
respuesta rápida y equivocada, una **explicación convincente y falsa**, que es peor porque
nadie la va a chequear.

**Un golden-set de "por qué" tiene que incluir trampas de este tipo a propósito**, y decir en
el `expect` que la respuesta correcta es admitir que no se sabe. Si todas las preguntas tienen
respuesta, no estás midiendo lo que importa.

**No siembres la respuesta y después preguntes.** Si al escribir el golden-set descubrís que
una razón real no estaba documentada, la tentación es agregarla al bundle. Hacelo **después**
de medir: sembrarla antes es enseñarle la respuesta al examen.

## Cuándo calificar a mano

El juez automático es el **mismo modelo**: bueno para iterar rápido, no para el veredicto
final. Antes de declarar una mejora "ganada", revisá a mano las `parcial`/`incorrecta` y,
para portabilidad cross-vendor, corré el golden-set con `OKF_EVAL_CLI=<otra-cli>` o pasalo a
mano por otra IA (ver [`reference/verification.md`](../../reference/verification.md)).

**Corré con `--repeat 3` y verificá a mano los desacuerdos.** Si la misma pregunta sale
`correcta` en una réplica e `incorrecta` en otra, el runner la marca `⚠ INESTABLE`: eso no es
un veredicto, es una señal de que el juez o la pregunta están mal. El juez tuvo un 29% de
falsos negativos medidos en este kit, así que un veredicto único no alcanza para tirar un
mecanismo a la basura ni para bendecirlo.

## Qué hacer con cada fallo

Cada `parcial`/`incorrecta` es un *failure mode* a clasificar antes de tocar nada:

- **routing** — la respuesta existía en el bundle pero el agente no la encontró → arreglo
  de índice/naming/contrato de entrada (**cambio de kit**).
- **concepto esparcido** — el hecho estaba en 5 docs sin página canónica → convención de
  concepto/glosario canónico (**cambio de kit**).
- **no-en-doc** — no estaba → autoría en el repo (**cambio de contenido**); y preguntá qué
  template lo habría evitado.
- **chunk grande** — la página correcta era enorme y costó tokens leerla → guía de tamaño
  de concepto (**cambio de kit**).
