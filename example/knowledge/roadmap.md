---
type: Roadmap
title: Rumbo de cortito
description: "Un acortador de links mínimo y sin dependencias; el rumbo todavía no lo dictó nadie y está inferido del código."
tags: [roadmap]
timestamp: 2026-08-07T00:00:00Z
---

> **Este archivo está inferido del código y del README, no dictado.** El bundle se
> sembró sin poder preguntar. Cada punto marcado con *Pendiente de confirmar* es una
> pregunta abierta para el dueño del proyecto, no una intención registrada.

# Visión

`cortito` acorta links y los resuelve, sin nada más: un proceso de Python, un archivo
SQLite y cero dependencias
(ver [0001](decisions/0001-solo-stdlib.md)). Eso es lo que se puede afirmar mirando
el repo.

> Pendiente de confirmar: para quién es y hasta dónde tiene que llegar — si es un
> servicio que alguien va a usar de verdad, una herramienta interna, o un ejercicio.
> La respuesta cambia qué tiene sentido priorizar de la lista de abajo.

# Ahora (en curso)

- (nada activo)

El repo tiene un solo commit, una sola rama y ningún TODO en el código: no hay
trabajo empezado que se pueda detectar desde afuera.

# Después (próximo, en orden)

Esto **no es un plan acordado**: son los candidatos que el propio código sugiere,
sin orden confirmado.

- **Alias personalizados y QR** — `FLAG_CUSTOM_ALIAS` y `FLAG_QR` ya existen en
  `server.py` y no hacen nada
  ([detalle](references/flags-de-entorno.md)). Que las flags estén escritas sugiere
  intención, pero puede ser también algo que se descartó.
- **Leer las analytics que ya se escriben** — la columna `hits` se incrementa y no la
  lee nadie ([schema](schema/links.md)); hoy el dato se acumula sin ninguna forma de
  consultarlo.
- **Decidir qué hacer con los dos gotchas abiertos** —
  [los códigos de una DB nueva](references/codigos-cortos-en-db-nueva.md) y
  [los paths que rompen el GET](references/paths-invalidos-rompen-el-get.md). Los dos
  son cambios de comportamiento, así que hay que decidirlos antes de tocarlos.
- **Cubrir `server.py` con tests** — hoy no tiene ninguno
  ([qué no cubren los chequeos](checks.md)).

> Pendiente de confirmar: cuál de estos importa, en qué orden, y qué falta que no
> esté acá.

# No-goals (por ahora)

> Pendiente de confirmar: qué se decidió explícitamente **no** hacer. No hay nada
> registrado, y es justo lo que evita que un agente lo "agregue de paso". Candidatos
> que el código insinúa pero nadie confirmó: autenticación, panel web, códigos no
> enumerables ([0002](decisions/0002-codigos-derivados-del-id.md)), correr esto
> detrás de algo que no sea `http.server`.
