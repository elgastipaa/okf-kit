---
type: Data Model
title: La tabla links
description: "Una fila por link acortado; el id es también el código, y no hay más tablas ni migraciones."
resource: src/store.py
tags: [sqlite, schema]
timestamp: 2026-08-07T00:00:00Z
verified_against: "d791cb8"
source_of_truth: code
---

Toda la persistencia es **una tabla, `links`**, en un archivo SQLite. El `CREATE
TABLE IF NOT EXISTS` vive en la constante `SCHEMA` de `src/store.py` y se ejecuta en
cada `connect()`: **no hay sistema de migraciones**. Cambiar una columna existente
implica migrar a mano las DB que ya estén dadas de alta, o borrarlas.

# Schema

Las columnas exactas están en `src/store.py` (constante `SCHEMA`) — acá va lo que el
DDL no dice:

- **Grano:** una fila = un link acortado. Nunca se actualiza el destino ni se borra
  una fila; lo único que muta es `hits`.
- **`id`** es la clave y **además el código público**: el código corto se deriva de
  él (ver [0002](../decisions/0002-codigos-derivados-del-id.md)). Por eso el
  contador tiene un piso, y por eso reciclar ids sería reciclar links.
- **`expires`** es un epoch en segundos y es **nullable**: `NULL` significa "no
  vence". Se calcula al insertar a partir del `ttl_days` del request; no hay forma de
  cambiarlo después.
- **`hits`** lo incrementa `count_hit` en cada resolución exitosa, pero **nada lo
  lee**: no hay endpoint ni consulta que exponga el contador
  (ver [flags de entorno](../references/flags-de-entorno.md)).
- **No hay índice sobre `target`**: no se puede preguntar "¿ya acorté esta URL?" sin
  un scan, y de hecho acortar dos veces la misma URL crea dos filas distintas.

# Dónde vive el archivo

`DB = Path("links.db")` es un path **relativo al directorio de trabajo**, así que la
DB aparece donde se haya levantado el proceso — ver
[levantar cortito local](../runbooks/levantar-local.md). Está en `.gitignore`.
