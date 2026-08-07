# Decision

* [cortito se queda en la stdlib de Python, sin dependencias](0001-solo-stdlib.md) - Todo (HTTP, persistencia, tests) sale de la biblioteca estándar: no hay requirements ni manifiesto de paquete.
* [El código corto se deriva del id de la fila, arrancando en FIRST_ID](0002-codigos-derivados-del-id.md) - El código es el id de SQLite en base62; el piso FIRST_ID evita que existan códigos de uno o dos caracteres.
* [Un link vencido responde 410, no 404](0003-expirado-responde-410.md) - El servicio distingue 'existió y venció' (410) de 'nunca existió' (404) en vez de tratar ambos como no encontrado.

> Las tres están en `status: proposed` y `origen: reconstruido`: se dedujeron leyendo
> el código, nadie las dictó. **Todavía no obligan al código** — cada una tiene su
> pregunta abierta, y pasan a `accepted` cuando alguien que sabe confirme el porqué.
