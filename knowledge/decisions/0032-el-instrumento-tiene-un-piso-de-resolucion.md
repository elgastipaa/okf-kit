---
type: Decision
status: accepted
verify: none
verify_note: es un límite del instrumento de medición, no una regla sobre el código del kit
origen: dictado
title: El instrumento tiene un piso de resolución, y abajo de eso no se compara
description: "Con el n que el kit puede pagar, efectos menores a ~20-40% son indistinguibles del ruido; se declara el piso y se deja de gastar en ese eje en vez de comprar ruido."
tags: [okf, eval, metodo]
timestamp: 2026-08-06T00:00:00Z
---

# Contexto

La [0028](0028-la-medicion-manda-y-el-gate-se-escribe-antes.md) fijó que un cambio de
comportamiento no se acepta sin medirlo, con n ≥ 3 y reportando dispersión. Aplicándola a
cinco condiciones sobre el mismo repo apareció el límite de la propia herramienta:

Con **n = 12 por brazo** sobre un golden set de 4 preguntas, `2·EE` de la diferencia de medias
valió entre **1.1 y 3.4 turnos** según el par comparado. Sobre medias de 5 a 9 turnos, eso
significa que **ningún efecto menor a ~20-40% es distinguible del ruido**. Cuatro de las cinco
condiciones quedaron indistinguibles de a pares — no porque fueran iguales, sino porque el
instrumento no puede separarlas.

Cada brazo cuesta ~US$10 y ~20 minutos. Bajar el piso a la mitad exige cuadruplicar el n.

# Decisión

**Antes de medir se calcula qué efecto mínimo puede resolver el instrumento, y si el efecto
esperado es menor, no se mide: se decide por criterio y se declara que se decidió así.**

1. El gate de un cambio declara su **piso de resolución** junto con el criterio de éxito.
2. Un resultado por debajo del piso se informa **"indistinguible con n=N"** — nunca como
   mejora, y nunca como empate demostrado. Son cosas distintas.
3. Cuando un eje agota su presupuesto sin separar nada, **se para y se publica lo aprendido**,
   incluida la lista de hipótesis descartadas. Seguir es comprar ruido a precio de medición.

# Consecuencias

- **Un cambio que no se puede medir no es automáticamente un cambio que se revierte.** Se
  sostiene o se cae por su costo, su superficie y su riesgo — argumentos de ingeniería, no de
  estadística. Lo que **no** se hace es publicarlo con un número que no lo respalda.
- **El eje "prosa contra prosa" quedó cerrado** por esta regla, después de descartar tres
  hipótesis: la calidad de la prosa, la capa generada y la puerta de entrada. Ninguna separó
  por encima del piso.
- **Es incómodo y por eso hay que escribirlo.** La tentación cuando el número no alcanza es
  bajar el estándar —mirar la mediana, sacar la pregunta que molesta, contar una tendencia—.
  Declarar el piso de antemano es lo que hace que esa salida no esté disponible.
