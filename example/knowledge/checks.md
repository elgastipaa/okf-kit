---
type: Runbook
title: Cómo se comprueba que este repo anda
description: "Los comandos que prueban que el código funciona, y qué cubre cada uno."
tags: [checks, verificación]
timestamp: 2026-08-07T00:00:00Z
---

# Los comandos

Hay uno solo, y es el mismo que corre el CI (`.github/workflows/ci.yml`). Se corre
desde la raíz del repo.

| comando | qué prueba | tarda |
|---|---|---|
| `python3 -m unittest discover -s tests -t . -q` | el roundtrip de códigos base62 y el acortar/resolver/expirar sobre una DB temporal | <1s |

# Qué NO cubren

Los tests tocan `codes.py` y `store.py`. **`server.py` no tiene ni un test**, así que
todo lo que es HTTP queda sin cubrir:

- los códigos de estado (302 / 404 / 410 / 400) y el header `Location`;
- el parseo del body del `POST` y el rechazo del request sin `url`;
- las [flags de entorno](references/flags-de-entorno.md) — que
  `FLAG_ANALYTICS` prenda o apague el conteo de hits no lo verifica nadie;
- el crash ante
  [paths que no son códigos](references/paths-invalidos-rompen-el-get.md).

Y dentro de lo que sí cubren, hay un hueco conocido: el piso `FIRST_ID` se testea
sobre la función, no sobre la base, así que el test pasa aunque
[una DB nueva emita códigos de un carácter](references/codigos-cortos-en-db-nueva.md).

No hay linter, ni type checker, ni chequeo de formato: el CI es exclusivamente esa
línea de tests.

# Antes de decir "listo"

Corré lo de arriba y **mirá que pase**. Si algo falla y no lo vas a arreglar en este
cambio, decilo explícitamente en vez de omitirlo. Si tocaste `server.py`, el comando
no te va a avisar de nada: probalo a mano con
[el runbook local](runbooks/levantar-local.md).
