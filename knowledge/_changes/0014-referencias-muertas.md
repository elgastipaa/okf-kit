---
type: Change
status: in-progress
title: El kit detecta solo cuando el bundle nombra algo que ya no existe
description: "Un chequeo determinista de referencias vivas (paths, resource y símbolos) que caza el drift más común y más barato: el de renombres y borrados."
tags: [okf, drift, tooling]
timestamp: 2026-08-07T00:00:00Z
---

# El problema

El kit tiene tres herramientas y **ninguna chequea si el bundle dice la verdad**:

- `okf_lint.py` valida **estructura** (frontmatter, links entre docs, índices).
- `okf_stale.py` **rankea** dónde mirar por antigüedad del sello. Es una prioridad, no un hecho.
- `okf_coldtest.py` pregunta a un modelo, o sea que cuesta tokens y no es determinista.

Entre medio queda el drift **más común y más barato de detectar**: el bundle nombra un archivo
o un símbolo que **ya no existe** porque alguien renombró o borró. Eso convierte un
`code-of-record` del glosario en una mentira **sin que nadie se entere**, y hoy el kit solo lo
encuentra si un humano lee.

Está medido que este es un modo de falla real: en un repo de prueba, el glosario mandaba el
término "Clase base" a un archivo que **existía pero era otra cosa**, y le costó 11 turnos al
agente que lo siguió. Un chequeo de existencia no habría cazado *ese* caso —el archivo
existía—, pero sí caza toda la familia de renombres y borrados, que es la mayoría.

La idea **no es nuestra**: sale de `okf-refs.mjs`, que el dueño de un repo escribió por su
cuenta sobre su propio bundle OKF. Que un usuario haya tenido que escribirlo es la evidencia de
que faltaba.

# Diseño

`templates/scripts/okf_refs.py`, stdlib pura, cero deps, cero tokens, instalado como el resto.

Chequea dentro del bundle:

1. **`resource:` del frontmatter**, cuando apunta al repo y no a una URL.
2. **Paths entre backticks** (`` `src/lib/x.ts` ``), con soporte de `*` y `**`.
3. **Símbolos entre backticks** (`` `nombreDeFuncion()` ``) contra las definiciones del repo —
   **opt-in con `--symbols`**, porque es la parte con más falsos positivos.

**Lo que generaliza respecto del original** (que estaba cableado a un repo Next/TS):

- **Nada de lista blanca de carpetas.** Un path cuenta si su **primer segmento existe** en la
  raíz del repo. Se auto-adapta a cualquier layout sin configurar nada.
- **Símbolos multi-lenguaje** (JS/TS, Python, Go, Rust), y **apagados por default**.
- **Las excepciones no se editan adentro del script** —el material instalado no se toca
  ([0025](../decisions/0025-el-material-instalado-se-sella-con-hash.md))—: van por `--ignore`,
  repetible, igual que el `--skip` del linter.

# Criterio de aceptación, escrito antes de correrlo

No es una medición de comportamiento de agente, así que no aplica el instrumento de la
[0032](../decisions/0032-el-instrumento-tiene-un-piso-de-resolucion.md). Se valida por
**hallazgos verificables a mano**:

1. **Encuentra de verdad**: sobre al menos un bundle real y maduro que no sea el dogfood,
   reporta **≥1 referencia muerta** que se confirme abriendo el repo.
2. **No miente**: cada hallazgo de esa corrida se revisa **uno por uno**. Si la tasa de falsos
   positivos supera el **20%** en el modo por default, la herramienta no se shippea así — un
   chequeo que grita en falso se apaga a la semana y queda peor que no tenerlo.
3. **El dogfood queda limpio** (o sus hallazgos se arreglan, que también valida).
4. Assert + rotura probada, como todo lo demás.

# Resultado de la validación

Corrida contra **cinco bundles reales** (el dogfood del kit y cuatro repos ajenos), revisando
**cada hallazgo a mano**. La primera versión falló su propio criterio y hubo que arreglarla
tres veces:

| ronda | hallazgos | verdaderos | qué enseñó |
|---|---|---|---|
| 1 | 12 | 1 | Los `{{placeholders}}` y `NNNN-<slug>.md` de un doc que **enseña un formato** no son referencias. |
| 2 | 9 | 1 | `Path.glob` interpreta `[sessionId]` como **clase de caracteres**: una ruta dinámica de Next daba "no existe" con los archivos ahí. Se reemplazó por matcheo manual. |
| 3 | 8 | 2 | **La clase de falso positivo que importa**: nombrar algo muerto **a propósito** es un uso legítimo y frecuente (un triage de docs viejos, un runbook que avisa "este reporte lista archivos que ya no existen"). Una referencia muerta solo es un problema si el documento **la afirma como viva**. |
| final | 3 | **2** | — |

**Criterio 1 (encuentra de verdad): cumplido.** Los dos hallazgos genuinos están en un bundle
que generó **`okf-init` a ciegas**, o sea que la herramienta caza los errores que comete el
propio kit:

- El glosario apunta el término "Cónclave" a `src/lib/game/conclave-yield.ts`; el archivo real
  es `conclave-yield-service.ts`. **Es la misma falla que costó 11 turnos en la medición** —
  un `code-of-record` que miente por un renombre— cazada en un segundo y sin tokens.
- Un runbook manda a `prisma/seed.ts`, que no existe.

**Criterio 2 (no miente): cumplido.** Cero falsos positivos en los cinco bundles de la corrida
final. Fue lo que más trabajo costó, y con razón: **un chequeo que grita en falso se apaga a
la semana y queda peor que no tenerlo**.

**Criterio 3 (dogfood limpio): cumplido, y de paso destapó un agujero.** Tres hallazgos
iniciales sobre el bundle del kit eran referencias a `knowledge/checks.md` — y **el kit no
tenía el suyo**: instala ese archivo en todo repo ajeno, su gate se lo exige a los demás, y él
no lo dogfoodeaba. Ahora lo tiene.

# Tareas

- [ ] Criterio escrito antes de codear
- [ ] `okf_refs.py` con `--symbols` e `--ignore`
- [ ] Validar contra el dogfood y contra un bundle real ajeno al kit
- [ ] Instalarlo (instalador, CI, `checks.md`) y nombrarlo en `okf-verify`
- [ ] Asserts + roturas
- [ ] Decidir aparte si la **capa 2** (cada decisión declara cómo se la falsea) entra al kit
