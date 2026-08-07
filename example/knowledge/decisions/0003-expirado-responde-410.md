---
type: Decision
title: Un link vencido responde 410, no 404
description: "El servicio distingue 'existió y venció' (410) de 'nunca existió' (404) en vez de tratar ambos como no encontrado."
status: proposed
origen: reconstruido
verify: python3 -m unittest tests.test_store -q
resource: src/server.py
tags: [http, expiracion]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

`shorten` acepta un `ttl_days` opcional que se guarda como `expires` (epoch) en el
[schema](../schema/links.md). Al resolver, `store.resolve` devuelve una tupla
`(target, expired)` en vez de un `None` para los dos casos, y el handler traduce eso
a **410 Gone** cuando venció y **404** cuando no hay fila. El test
`test_expirado_se_distingue_de_inexistente` cubre justamente esa distinción, lo que
sugiere que es deliberada y no un accidente.

> Pendiente de confirmar: si la distinción se hizo por semántica HTTP a secas o
> porque algún consumidor necesita diferenciar los dos casos. No hay razón registrada,
> así que la decisión queda `proposed`.

# Decisión

`resolve` no colapsa "vencido" en "no existe": devuelve el flag de expiración y el
handler responde 410 para el link vencido, 404 para el inexistente.

# Consecuencias

- Un 410 **confirma que ese código existió**, lo que sumado a que los códigos son
  [enumerables](0002-codigos-derivados-del-id.md) permite mapear qué códigos se
  emitieron. Es el costo de la distinción.
- Las filas vencidas **no se borran**: siguen ocupando su id y su lugar en la tabla.
  No hay proceso de limpieza; si alguna vez se agrega, tiene que respetar que borrar
  la fila convierte el 410 en 404.
- Un link vencido **no cuenta hit**: el `count_hit` está después del early-return del
  410.
