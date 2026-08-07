---
type: Decision
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*el CI del repo destino corre okf_refs"
title: El bundle chequea solo que sus referencias sigan vivas
description: "Un chequeo determinista de paths y símbolos citados, que solo reporta cuando el documento afirma la referencia como viva."
tags: [okf, drift, tooling]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

Entre las herramientas del kit quedaba un hueco: `okf_lint.py` valida **estructura**,
`okf_stale.py` **rankea** por antigüedad del sello —una prioridad, no un hecho— y
`okf_coldtest.py` le pregunta a un modelo, con lo que cuesta. **Ninguna chequeaba si el bundle
dice la verdad.**

El drift más común y más barato de detectar es el de **renombres y borrados**: el bundle
nombra un archivo que ya no existe y eso convierte un `code-of-record` en una mentira sin que
nadie se entere. Está medido que duele: en un repo de prueba, seguir un puntero equivocado
costó **11 turnos**.

La idea no es del kit: sale de un `okf-refs.mjs` que el dueño de un repo escribió por su
cuenta sobre su propio bundle. **Que un usuario haya tenido que escribirlo es la evidencia de
que faltaba.**

# Decisión

Se instala **`okf_refs.py`**: determinista, stdlib pura, cero tokens, y **va al CI** porque no
ejecuta nada. Chequea `resource:`, paths entre backticks (con `*`, `**` y `{a,b}`) y —opt-in
con `--symbols`— símbolos.

Y la regla que lo hace usable, que salió de validarlo contra cinco bundles reales:

> **Una referencia muerta solo es un problema si el documento la afirma como viva.**

Nombrar algo muerto **a propósito** es un uso legítimo y frecuente: un triage de docs viejos,
una capa declarada no-autoritativa, un runbook que avisa "este reporte lista archivos que ya
no existen". Si el contexto de ±1 línea dice que algo no existe, no se reporta.

# Consecuencias

- **La validación importó más que la implementación.** La herramienta falló su propio criterio
  **tres veces**: los `{{placeholders}}` de un doc que enseña un formato no son referencias;
  `Path.glob` lee `[sessionId]` como clase de caracteres; y la regla de arriba. Sin esas tres
  pasadas habría shippeado con 8 falsos positivos sobre 8 hallazgos.
- **Un chequeo que grita en falso se apaga a la semana**, y queda peor que no tenerlo. Por eso
  el criterio de aceptación era la **tasa de falsos positivos**, no la de hallazgos.
- **Encontró errores del propio kit**: los dos hallazgos genuinos están en un bundle que generó
  `okf-init` **a ciegas** — un glosario apuntando a `conclave-yield.ts` cuando el archivo es
  `conclave-yield-service.ts`.
- **Y destapó que el kit no dogfoodeaba su propio `checks.md`**: lo instala en todo repo ajeno,
  su gate se lo exige a los demás, y no lo tenía.
