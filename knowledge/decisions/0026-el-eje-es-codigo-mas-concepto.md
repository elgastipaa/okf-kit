---
type: Decision
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*ofrece codigo/concepto/mixto"
title: El kit sigue siendo multipropósito, pero sobre un eje — código + concepto
description: "Se retira el perfil datos y wiki se renombra a concepto: el eje no es la industria del repo sino si documentás cómo funciona algo o qué significa algo."
tags: [okf, perfiles, alcance, mercado]
timestamp: 2026-08-04T00:00:00Z
---

# Contexto

El kit ofrecía cuatro perfiles: `codigo`, `datos`, `wiki`, `mixto`. El análisis del ecosistema
mostró que **0 de las 131 entradas** de la lista de referencia del mercado son de datos o de
wikis, y propuso matar los dos perfiles para dejar solo repos de código — que es lo único que
el kit midió alguna vez.

Se evaluó y **se rechazó esa lectura**. Matar el multipropósito habría:

- roto el `--profile datos` de quien ya lo usó (contrato de CLI);
- dejado a la [0006](0006-dogfood-profile-choice.md) —normativa— describiendo el dogfood del
  propio kit con un vocabulario inexistente ("perfil Mixto, combinando Código y Wiki");
- achicado una promesa pública del README a partir de evidencia sobre **una** lista curada de
  herramientas de vibe-coding, que no es el universo de repos que existen.

El problema real de los cuatro perfiles no era ser demasiados: era estar cortados por la
**industria** del repo (datos, wiki) en vez de por lo que efectivamente cambia en el bundle.

# Decisión

El kit **sigue siendo multipropósito**, sobre un eje explícito: **código + concepto**.

- `codigo` — se documenta **cómo funciona algo**.
- `concepto` — se documenta **qué significa algo** (una base de conocimiento, un dominio, un
  método). Es el viejo `wiki`, renombrado a la unidad de OKF en vez de al nombre de una
  herramienta; **`--profile wiki` sigue funcionando como alias** y lo avisa.
- `mixto` — las dos cosas, o algo que no encaja. **Un repo de datos entra por acá**, con
  `datasets/ tables/ references/metrics/ references/joins/ glossary/` como base: el
  vocabulario del viejo perfil `datos` no se perdió, dejó de ser una rama propia.

# Consecuencias

- **La promesa se mantiene y se vuelve más honesta**: en vez de enumerar industrias
  ("código, datos/analytics, wikis"), nombra el eje que de verdad cambia el layout. Un repo
  de datos siempre fue `mixto` en la práctica; ahora lo dice.
- **Nada se rompe.** El alias cubre el rename y el vocabulario de datos está escrito en el
  perfil `mixto` y en `reference/profiles.md`.
- **La [0006](0006-dogfood-profile-choice.md) sigue vigente** sin editarse: el dogfood usa
  `mixto`, y lo que ahí se llama "Wiki" hoy se llama `concepto`.
- **Contra-argumento que queda anotado**, porque puede volver: la evidencia de mercado sigue
  diciendo que casi nadie usa esto para conceptos puros. Si algún día el perfil `concepto`
  tampoco se usa, la salida no es matarlo sino **medirlo** — igual que todo lo demás acá.
