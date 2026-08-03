# Contribuir a okf-kit

Gracias por mirar. Este repo tiene una forma de trabajar bastante particular, y conviene
saberla antes de abrir un PR: **casi todo lo que parece prosa acá está verificado por un
assert**, y los cambios de comportamiento se miden antes de darlos por buenos.

## Lo mínimo

```bash
python3 scripts/okf_selfcheck.py        # el gate: consistencia interna del kit
python3 scripts/okf_selfcheck_test.py   # ¿el gate falla cuando debe?
python3 scripts/okf_lint_test.py        # ¿el linter reporta cuando debe?
python3 scripts/okf_stale_test.py       # ¿el ranker de drift encuentra el drift?
```

Los cuatro tienen que estar en verde. Es lo mismo que corre el CI, así que si pasan
localmente el PR pasa.

## Las tres reglas que no son negociables

**1. Todo assert nuevo viene con su rotura probada.** Si agregás un chequeo al gate o al
linter, agregá en la suite correspondiente el caso concreto que ese chequeo debería cazar —y,
si puede dar falso positivo, el caso legítimo que **no** debe romperlo. Un assert que nunca se
probó rompiendo lo que dice cuidar es decoración: pasa siempre y da una falsa sensación de
red. Una revisión en frío encontró siete así en este mismo repo.

**2. Una fuente de verdad por regla; el resto apunta.** La causa raíz de los bugs de este kit
fue re-statear el mismo procedimiento en N archivos y que derivaran. Si tocás una regla, editá
su archivo canónico y dejá punteros desde el resto. Hay asserts que lo verifican.

**3. No agregues prosa al contrato instalado sin medirla.** El `templates/AGENTS.md` se paga
en **cada turno** de cada agente en cada repo instalado, tiene un techo duro, y está medido
que agregarle texto **no mueve el acierto**: un intento de hacerlo costó 28% más turnos y se
revirtió. Si tu cambio necesita lugar ahí, primero recortá y mostrá el número.

## Si tu cambio afecta el comportamiento del agente

No alcanza con que parezca mejor. El kit trae un harness (`templates/eval/`) que mide turnos,
tokens y **acierto** con contexto fresco, y la regla es:

- **el gate se escribe ANTES de mirar el resultado**;
- una mejora de turnos que introduce **un error nuevo se rechaza**, por más que baje el
  promedio — una respuesta rápida y equivocada es peor que una lenta y correcta;
- **n≥3**: el ruido intra-condición medido acá es de ~3 turnos por pregunta, así que un
  efecto menor a eso no es un efecto.

Sí, esto hace que contribuir sea más lento. También es la razón por la que el repo publica
resultados negativos sobre sí mismo en vez de solo los que le convienen.

## Decisiones

Las de `knowledge/decisions/` con `status: accepted` son **normativas**: obligan al código. Si
encontrás código que las viola, el bug es el código. Si creés que la decisión está mal, se
**supersede** con una decisión nueva que explique por qué — **no se edita** la vieja para que
coincida con lo que el código hace hoy. Eso es exactamente lo que el kit le enseña a no hacer
a sus usuarios.

## Antes de abrir el PR

Contá **qué medición o qué rotura respalda** tu cambio. "Lo probé y anda" no dice nada que el
gate no diga; lo que interesa es qué se rompe si alguien lo deshace.

Y si encontrás algo roto y no querés arreglarlo, abrí un issue igual: media docena de los
mejores hallazgos de este repo salieron de mirarlo con ojos que no lo escribieron.
