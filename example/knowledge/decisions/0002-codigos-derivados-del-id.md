---
type: Decision
title: El código corto se deriva del id de la fila, arrancando en FIRST_ID
description: "El código es el id de SQLite en base62; el piso FIRST_ID evita que existan códigos de uno o dos caracteres."
status: proposed
origen: reconstruido
verify: python3 -m unittest tests.test_codes -q
resource: src/codes.py
tags: [codigos, base62, dominio]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

Un acortador tiene que mapear código↔destino. Las dos familias habituales son
guardar un código aleatorio en una columna (con chequeo de colisión) o **derivarlo**
del id autoincremental. `cortito` hace lo segundo: `codes.encode` convierte el
`lastrowid` del `INSERT` a base62 y `codes.decode` lo revierte, así que el código no
se persiste en ninguna parte.

Encima de eso, `FIRST_ID = 100_000` funciona como piso del contador: en base62,
100.000 ya son tres caracteres, y el test `test_no_arranca_en_cero` fija exactamente
esa propiedad ("ningún código real es de 1 o 2 chars").

> Pendiente de confirmar: por qué el piso es 100.000 y qué se buscaba con él —
> estética de los códigos, no repartir los cortos primero, o alguna razón de
> integración. No hay razón registrada, y sin ella esta decisión queda `proposed`.

# Decisión

El código corto es una función pura del id de la fila (base62, alfabeto
`0-9A-Za-z`), y los ids arrancan en `FIRST_ID`. No hay columna de código en el
[schema](../schema/links.md).

# Consecuencias

- **Los códigos son enumerables.** Al ser secuenciales, quien tenga uno puede
  adivinar los vecinos: `q0V`, `q0W`, `q0X`… No hay nada en el servicio que lo
  impida, así que **los links de `cortito` no son secretos** — no sirven para
  compartir algo privado "por oscuridad".
- No hay colisiones ni reintentos posibles: el id es único por construcción.
- El piso `FIRST_ID` **no se aplica en una DB recién creada** — el efecto real está
  en [los primeros códigos de una DB nueva](../references/codigos-cortos-en-db-nueva.md).
- Borrar una fila no libera su código: `decode` sigue apuntando a un id que ya no
  existe y el `GET` responde 404.
- Cambiar `ALPHABET` o `FIRST_ID` **invalida todos los códigos ya emitidos**, porque
  no están guardados: se recalculan en cada resolución.
