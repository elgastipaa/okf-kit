---
type: Architecture
title: Cómo está armado cortito
description: "Tres módulos stdlib en cadena: el handler HTTP llama al store, y el store deriva el código corto del id de SQLite."
resource: src/server.py
tags: [arquitectura, http, sqlite]
timestamp: 2026-08-07T00:00:00Z
verified_against: "d791cb8"
source_of_truth: code
---

El servicio son tres módulos y ninguna capa más: `server.py` (HTTP), `store.py`
(persistencia) y `codes.py` (la aritmética base62). No hay router, ORM, ni capa de
servicios — la decisión de quedarse en stdlib está en
[stdlib y nada más](../decisions/0001-solo-stdlib.md).

# El flujo de un request

- **`POST /`** → `server.do_POST` lee el JSON del body, exige `url`, y llama a
  `store.shorten`. El `INSERT` devuelve un `lastrowid` y ese id se convierte en el
  código con `codes.encode`. Se responde `201` con el código.
- **`GET /<code>`** → `server.do_GET` hace `codes.decode` del path y pide
  `store.resolve`. Tres salidas: `404` si no hay fila, `410` si la fila venció
  (ver [expirado no es inexistente](../decisions/0003-expirado-responde-410.md)),
  y `302` al target si está viva.
- **`GET /`** (path vacío) → healthcheck: devuelve `{"ok": true, "flags": ...}` con
  el estado de las [flags de entorno](../references/flags-de-entorno.md).

El código corto **no se guarda**: es una función pura del `id` de la fila, así que
`encode`/`decode` son la única fuente de la correspondencia código↔fila. Ver
[los códigos salen del id](../decisions/0002-codigos-derivados-del-id.md) y el
[modelo de datos](../schema/links.md).

# La conexión vive en el servidor, no en el request

`serve()` abre **una** conexión SQLite y la cuelga del objeto `HTTPServer`
(`srv.con`); el handler la lee de `self.server.con` en cada request. Funciona porque
`HTTPServer` es de un solo hilo y atiende un request por vez: nunca hay dos usos
concurrentes de esa conexión. **Es el supuesto que hay que revisar antes de meter
`ThreadingHTTPServer` o cualquier concurrencia** — las conexiones de `sqlite3` no se
comparten entre hilos por default.

> Pendiente de confirmar: si el single-thread es una elección o simplemente el default
> de `HTTPServer` que nunca hizo falta cambiar. No hay razón registrada.

# Lo que no existe

No hay autenticación, ni rate limiting, ni endpoint que lea la columna `hits` que
`store.count_hit` incrementa: hoy las analytics se **escriben** y no se leen por
ninguna vía del servicio. Ver [flags de entorno](../references/flags-de-entorno.md).
