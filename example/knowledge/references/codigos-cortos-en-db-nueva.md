---
type: Reference
title: "SQLite: sqlite_sequence no tiene fila hasta el primer INSERT"
description: "El piso de ids no se aplicaba en una base nueva porque la fila del contador todavía no existía; arreglado, y el test que lo tapaba también."
resource: src/store.py
tags: [gotcha, sqlite, codigos]
timestamp: 2026-08-07T12:00:00Z
verified_against: "f55d2fe"
source_of_truth: code
---

`connect()` intenta poner el piso del contador con un `UPDATE sqlite_sequence SET seq
= MAX(seq, FIRST_ID) WHERE name = 'links'`. El problema es **cuándo** corre: SQLite
recién crea la fila de `links` en `sqlite_sequence` con el **primer `INSERT`**, así
que en una DB vacía ese `UPDATE` no afecta ninguna fila y se pierde en silencio.

Comportamiento real sobre una DB nueva (verificado corriendo el código):

```
connect(db_nueva) → shorten(...) → "1"
                    shorten(...) → "2"
connect(esa_db)   → shorten(...) → "q0V"     # ahora sí aplica el piso
                    shorten(...) → "q0W"
```

Es decir: los links que se creen **antes de la primera reconexión** rompen la
propiedad que fija [la decisión 0002](../decisions/0002-codigos-derivados-del-id.md)
("ningún código real es de 1 o 2 chars"). Los tests no lo detectan porque
`test_no_arranca_en_cero` sólo mide `len(encode(FIRST_ID))`, sin insertar.

Como los códigos **no se guardan** sino que se derivan del id, esos primeros links
quedan así para siempre: no hay backfill posible sin cambiarles el código.

# Arreglado

`connect()` ahora **inserta la fila** de `sqlite_sequence` si no existe, antes del `UPDATE`.
El primer código de una base nueva vuelve a ser de 3 caracteres.

**Y el test que lo tapaba también se arregló**, que es la parte que importa: `test_no_arranca_en_cero`
medía `len(encode(FIRST_ID))` —aritmética pura, sin tocar la base— así que **pasaba mientras la
propiedad estaba rota**. El de ahora abre una base nueva y mira el código que sale de verdad.

La trampa de SQLite es permanente, por eso este documento se queda: cualquiera que vuelva a
tocar el contador se la come de nuevo.
