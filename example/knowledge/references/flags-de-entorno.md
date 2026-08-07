---
type: Reference
title: Las flags de entorno y cuáles no hacen nada
description: "De las tres flags que expone el healthcheck, sólo FLAG_ANALYTICS cambia el comportamiento; las otras dos están declaradas y sin uso."
resource: src/server.py
tags: [gotcha, flags, configuracion]
timestamp: 2026-08-07T00:00:00Z
verified_against: "d791cb8"
source_of_truth: code
---

`server.py` arma un diccionario `FLAGS` leyendo el entorno **una sola vez, al
importar el módulo**: cambiar una variable con el proceso vivo no tiene efecto, hay
que reiniciar. El `GET /` las devuelve tal cual, que es la forma rápida de ver con
qué configuración quedó levantado un proceso.

Qué hace cada una hoy (el detalle de defaults está en el propio `src/server.py`):

- **`FLAG_ANALYTICS`** — la única con efecto: si está prendida, cada resolución
  exitosa incrementa `hits`. Ojo: **incrementar es todo lo que pasa**; nada lee esa
  columna (ver [la tabla links](../schema/links.md)), así que apagarla no cambia nada
  observable desde afuera del archivo SQLite.
- **`FLAG_CUSTOM_ALIAS`** — se lee, se reporta en el healthcheck y **no la consulta
  ningún código**. Prenderla no habilita alias personalizados: la funcionalidad no
  existe.
- **`FLAG_QR`** — misma situación: declarada, reportada, sin implementación detrás.

El riesgo concreto es leer el healthcheck y concluir que la feature existe. Si vas a
implementar alguna de las dos, el nombre de la flag ya está tomado y el
[roadmap](../roadmap.md) es el lugar donde debería estar dicho si eso está planeado.

> Pendiente de confirmar: si `FLAG_CUSTOM_ALIAS` y `FLAG_QR` son trabajo empezado,
> intención declarada, o restos que conviene borrar.
