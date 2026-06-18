<!--
  TEMPLATE de "hechos generados" (volatile facts). Copialo como `_generated/state.md`
  (o donde tu generador lo escriba) y BORRÁ este comentario.

  PARA QUÉ: hay un punto medio entre copiar un valor a mano (drift garantizado, respuesta
  rápida pero a veces falsa) y dejar solo un puntero (correcto, pero el agente igual abre y
  lee el código). Para hechos VOLÁTILES que se preguntan seguido —conteos, niveles de
  desbloqueo, flags ON/OFF, listas de cosas— la respuesta buena es **generarlos del código**:
  rápido de leer Y no puede driftear, porque un script los regenera y el CI falla si quedaron
  viejos. Es el patrón `_generated/state.md` + `wiki:gen`/`wiki:check` de repos maduros.

  CUÁNDO vale el esfuerzo: el repo tiene hechos volátiles que (a) se preguntan seguido y (b)
  cambian seguido. Si son estables, un puntero al code-of-record alcanza. No generes por
  generar — un generador es código a mantener.

  REGLAS:
  - Este archivo es de SOLO LECTURA para humanos/agentes: NO se edita a mano (el header lo
    dice). Si está mal, se arregla el GENERADOR o el código, no el archivo.
  - El generador vive en el repo (ej. `scripts/<gen>.{js,py,…}`) y corre en CI con un check
    de frescura que falla si el archivo quedó desincronizado del código.
  - El glosario/index apunta acá como **code-of-record** de esos hechos (no a 8 archivos).
-->
---
type: Reference
title: {{Hechos generados de <proyecto> (estado vivo)}}
description: Hechos volátiles generados del código — fuente rápida y fiel por construcción; NO editar a mano.
source_of_truth: code
tags: [generated, state]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

<!-- GENERADO por `{{comando, ej. npm run facts:gen}}` — NO editar a mano.
     Verificado en CI por `{{comando de check}}`. Si difiere del código, gana el código. -->

# {{Categoría de hechos, ej. Conteos}}

| {{Hecho}} | {{Valor}} | Origen |
|---|---|---|
| {{ej. # de clases base}} | {{generado}} | `{{src/data/x}}` |
| {{ej. nivel de desbloqueo de subclases}} | {{generado}} | `{{src/data/y}}` |
