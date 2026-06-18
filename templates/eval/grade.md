# Calificar acierto (la 4ª columna)

Tokens sin acierto miente: optimizar hacia respuestas vagas baja tokens y empeora el kit.
Por eso cada corrida debería tener una columna de **acierto**.

## Automático (`--grade`)

`run-eval.py --grade` llama a un **juez** (`claude -p`) por pregunta, comparando la
respuesta del agente contra el `expect` del golden-set, y devuelve una etiqueta:

| etiqueta | significa |
|---|---|
| `correcta` | contiene los hechos esperados **y** cita la fuente correcta |
| `parcial` | algo bien, falta un hecho clave o no citó la fuente |
| `incorrecta` | hechos equivocados, o **inventó** |
| `trampa-ok` | era una `trap` y el agente admitió "no está documentado" |

Aprueba = `correcta` ∪ `trampa-ok`. El resumen del runner cuenta esos como `aciertos`.

## El falso positivo: rápido Y mal (por qué `--grade` no es opcional)

El modo de falla más peligroso no es la respuesta lenta — es la **rápida y equivocada**. Una
capa de contexto puede hacer que un agente conteste en 1 turno citando una sección del
`AGENTS.md` que *suena* a la pregunta, **sin verificar el código**. Midiendo solo turnos, eso
parece una mejora; es una regresión de correctitud disfrazada.

> Caso real: preguntar "¿cuál es la regla anti-waste?" (una mecánica de combate) → el agente
> matcheó "anti-waste" con la sección *"no reconcilies basura"* del contrato y respondió mal en
> 1 turno (vs 5 turnos y correcto sin la capa).

**Regla dura del loop:** una mejora de turnos que introduce **un `incorrecta` nuevo se
rechaza**, por más que baje el promedio. Por eso cada iteración corre `--grade` y compara
acierto, no solo turnos/tokens.

## Cuándo calificar a mano

El juez automático es el **mismo modelo**: bueno para iterar rápido, no para el veredicto
final. Antes de declarar una mejora "ganada", revisá a mano las `parcial`/`incorrecta` y,
para portabilidad cross-vendor, pasá el golden-set por otra IA (ver
[`reference/verification.md`](../../reference/verification.md)).

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
