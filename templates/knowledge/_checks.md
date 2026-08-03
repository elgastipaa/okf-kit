<!--
  TEMPLATE de chequeos. Va como `knowledge/checks.md` (en la RAÍZ del bundle, no en una
  carpeta). Lo siembra el instalador y lo completa el agente leyendo el repo. Es el único
  concepto que responde "¿cómo sé que lo que escribí anda?" — el resto del bundle dice qué
  hay y por qué, no cómo comprobarlo. Borrá este comentario.

  REGLA: acá van COMANDOS, no prosa. Un chequeo que no se puede copiar y pegar no sirve.
  Si el repo no tiene ninguno, decilo explícitamente: "este repo no tiene chequeos
  automáticos" es información valiosa y hoy invisible, y evita que un agente invente uno.
-->
---
type: Runbook
title: Cómo se comprueba que este repo anda
description: "Los comandos que prueban que el código funciona, y qué cubre cada uno."
tags: [checks, verificación]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Los comandos

{{Uno por línea, con qué cubre y cuánto tarda. Sacalos del `package.json` / `Makefile` /
`pyproject.toml` / el CI — no los inventes. Ej:}}

| comando | qué prueba | tarda |
|---|---|---|
| `{{npm test}}` | {{unit tests del engine}} | {{~30s}} |
| `{{npm run build}}` | {{que compila y no rompió imports}} | {{~1m}} |
| `{{npm run smoke}}` | {{el flujo principal end-to-end}} | {{~2m}} |

{{**Si este repo NO tiene chequeos automáticos, borrá la tabla y escribilo tal cual:**
"Este repo no tiene chequeos automáticos. Para saber si un cambio anda hay que {{cómo se
verifica a mano hoy}}." Decirlo es más útil que dejar una tabla vacía o inventar comandos.}}

# Qué NO cubren

{{Lo que estos comandos dejan pasar, que es lo que hace que alguien confíe de más: ej. "los
tests no tocan la UI", "el smoke usa datos fijos y no prueba el cálculo de balance", "no hay
nada que valide las migraciones". Si no sabés, preguntá — no lo adivines.}}

# Antes de decir "listo"

Corré lo de arriba y **mirá que pase**. Si algo falla y no lo vas a arreglar en este cambio,
decilo explícitamente en vez de omitirlo.
