---
type: Decision
status: accepted
origen: dictado
title: Un cambio de comportamiento no se acepta sin medirlo, y el gate se escribe antes de mirar
description: "El kit revierte sus propias mejoras cuando la medición no las respalda, y para que eso sea posible el criterio de éxito se fija antes de ver el resultado."
tags: [okf, eval, metodo, correctness]
timestamp: 2026-08-05T00:00:00Z
---

# Contexto

Durante un ciclo de optimización el kit publicó un **−31% de turnos** como su número de
referencia. Al re-medirlo con un instrumento arreglado, ese número **no replicó**: estaba
concentrado en una sola pregunta, y el `27` del baseline que lo producía era, con toda
probabilidad, un outlier de **n=1**.

Al auditar el instrumento aparecieron cuatro defectos, todos capaces de fabricar un resultado:

- **n=1** contra un ruido intra-condición medido de **~3 turnos por pregunta**: cualquier
  efecto menor a eso era indistinguible de haber corrido dos veces.
- El **juez corría sin `cwd=repo`**: no podía abrir un archivo del repo que juzgaba, así que
  degradaba a matcheo de paráfrasis.
- El brazo "sin capa" **le pedía al agente que ignorara el contrato** en vez de apartarlo — y
  el harness lo auto-carga antes de que el agente decida nada.
- El **costo del juez se descartaba**, subreportando ~40% del gasto real.

Y una tentación estructural: cuando el número confirma la hipótesis propia, **el primer
reflejo es creerle**. Pasó dos veces en el mismo ciclo — una corrida con 11 de 18 llamadas
fallidas mostró "3/18 inventadas" y parecía una mejora enorme; era el hueco de los datos
faltantes.

# Decisión

**Ningún cambio que afecte el comportamiento del agente se da por bueno sin medirlo**, y para
que la medición signifique algo:

1. **El gate se escribe ANTES de mirar el resultado**, en el doc del cambio. Un criterio
   fijado después es una racionalización.
2. **n ≥ 3**, y se reporta la **dispersión**. Un efecto menor al spread observado se informa
   como *"indistinguible con n=N"* — no como mejora ni como empeoramiento.
3. **Una mejora de turnos que introduce un error nuevo se rechaza**, por más que baje el
   promedio: una respuesta rápida y equivocada es peor que una lenta y correcta.
4. **Los resultados negativos se publican igual.** Un kit que solo publica lo que le conviene
   no está midiendo: está haciendo publicidad.
5. **Antes de leer un scorecard se valida que sea uno**: corridas completas, cero fallidas, y
   el repo bajo prueba sin modificar por la propia corrida.

# Consecuencias

- **Ya se ejerció, y por eso vale.** La [0022](0022-el-bundle-tambien-es-un-mapa.md) se aceptó
  con su gate escrito, se midió, **no lo pasó** (+28% de turnos sin alcanzar el acierto
  exigido) y se revirtió en la [0023](0023-verificar-siempre-no-paga.md). Una regla que nunca
  tumbó nada propio no está probada.
- **Cuesta.** Cada iteración de comportamiento son ~20 minutos y ~US$15-25 de medición. Es el
  precio de no acumular mejoras imaginarias, y es más barato que descubrirlas tarde.
- **El alcance también se mide.** Aplicando esto se estableció que la capa **no paga** en
  recuperación de hechos sobre un repo chico y bien nombrado, y **sí paga** (−34% de turnos,
  más acierto) sobre uno grande con código forkeado. El kit no sirve siempre, y decirlo con
  una condición medida es más defendible que prometer que sirve para todo.
- **Es el diferencial.** Ningún competidor del ecosistema mide su propio efecto con brazo de
  control; el único que publica un número lo hace sin dispersión ni condición de control.
