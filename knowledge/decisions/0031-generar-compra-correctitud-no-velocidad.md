---
type: Decision
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*traiga su propio check de drift"
origen: dictado
title: La capa generada se instala por correctitud, no por velocidad
description: "Generar hechos volátiles del código evita que el bundle mienta, pero no reduce los turnos; el kit lo pide por lo primero y no promete lo segundo."
tags: [okf, generated, eval]
timestamp: 2026-08-06T00:00:00Z
---

# Contexto

Para hechos que se preguntan seguido **y** cambian seguido —conteos, flags ON/OFF, miembros de
un enum, rutas, modelos— hay tres opciones: copiarlos a mano (driftea, y driftea **con la
autoridad del bundle**), dejar un puntero (correcto, pero el agente igual abre el código) o
**generarlos**. El kit enseñaba la tercera en `GUIDE.md` y tenía su template, pero el
procedimiento que el agente sigue de verdad **no la nombraba ni una vez**.

La hipótesis al agregarla era que bajaría los turnos, porque el dato queda a un archivo de
distancia. **Medida, no los bajó**: el brazo con capa generada quedó indistinguible del mismo
bundle sin ella. Lo que sí subió fue el acierto, de 10/12 a 11/12, empatando con una capa
escrita a mano.

El detalle que explica el mecanismo: el generado **ni siquiera cubría** la pregunta que más
empeoró. El bundle no desvió al agente — lo mandó por un camino más largo y más riguroso.

# Decisión

**Se genera para que el bundle no mienta, no para que el agente lea menos.** `okf-init` lo
pide con esa justificación y con el número real, y el kit **no promete ahorro de turnos** por
esta pieza.

- El generador vive en el repo, en su lenguaje, y **trae su propio `--check`** que sale ≠ 0 si
  el archivo difiere del código. Un generado sin check miente igual que la prosa, solo que más
  rápido.
- El check se cablea en `knowledge/checks.md` **y en el CI**. Sin CI es una promesa, no una
  garantía.
- **No se genera por generar**: si los hechos volátiles son pocos y estables, un puntero
  alcanza. Un generador es código a mantener.

# Consecuencias

- Un dato generado **no puede llevar un puntero equivocado**, que es la falla que apareció en
  el bundle anterior: el glosario mandaba "Clase base" a un archivo que existe pero es otra
  cosa. Ese error es imposible cuando la ruta la emite el parser.
- **Medir esto costó una instalación tirada.** El primer intento no valía: el agente **adaptó
  el generador que ya tenía el repo** en vez de escribir uno, lo que comparaba el generador del
  dueño contra su propia wiki. Para que un brazo mida una función del kit hay que sacar del
  repo la versión humana de esa función.
