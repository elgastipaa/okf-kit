---
type: Decision
title: "El material instalado es autosuficiente y se recorta con marcadores, no con prosa"
description: "Lo que el kit copia a un repo destino no puede citar rutas del kit ni depender de instrucciones de borrado en prosa; ambas cosas las verifica el selfcheck."
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*no cita rutas que solo existen en el kit"
tags: [installation, source-of-truth, enforcement]
timestamp: 2026-07-26T00:00:00Z
---

# Contexto

El [cold-review de 4 lentes](../../DEVELOPING.md) sobre la v0.6.0 encontró 2 blockers y ~12
majors. Ninguno estaba en el diseño de la versión; casi todos eran instancias de **un mismo
defecto estructural**: el kit escribía el material instalado como si el lector fuera a tener
`okf-kit` en disco.

- El contrato instalado apuntaba a `reference/maintaining.md` e `install-per-tool.md`.
- `okf-plan` —el flujo central de la versión— mandaba crear el roadmap y los cambios "desde
  el template `templates/knowledge/_change.md`".
- `okf-verify` había **perdido** en ese mismo diff el hedge `(si está disponible)` con el que
  citaba el formato de su reporte.

El repo destino no recibe nada de eso: recibe `AGENTS.md`, el bundle, tres skills y dos
scripts. Un agente que trabaje ese repo tres meses después —que es exactamente el caso que el
kit existe para servir— no puede seguir un procedimiento que cita archivos inexistentes.

El segundo defecto era gemelo. La instalación **mínima** (sin capa de futuro) se explicaba en
prosa: *"borrá la sección 'Rumbo y trabajo en curso' y la línea de `okf-plan`"*. Enumeraba 2
lugares; la capa aparecía en 3, y la garantía "si el usuario pide ir directo al código, se
respeta" vivía **dentro** del bloque a borrar. Seguir la instrucción al pie de la letra
producía un contrato que manda hacer harvest de una carpeta inexistente. La
[decisión 0012](0012-descriptive-vs-normative.md) ya declaraba ese defecto *corregido*: la
corrección estaba incompleta, y por su propia regla el bug era el kit, no la decisión.

# Decisión

**1. El material que se instala es autosuficiente.** `templates/AGENTS.md` y los tres skills
que van al repo destino (`okf-update`, `okf-verify`, `okf-plan`) no pueden citar rutas que
solo existen en el kit. Lo que el procedimiento necesite —el esqueleto de un `_change.md`, el
formato del reporte de verificación— va **inlineado**. `okf-init` y `okf-migrate` quedan
exentos: corren en el momento del bootstrap, con el kit a mano.

Corolario aceptado: esto **duplica** texto entre `okf-kit` y lo instalado, en tensión con
"una verdad, un lugar". Se resuelve así porque un puntero a un archivo que no existe es peor
que una copia. La regla sigue valiendo *dentro* del kit.

**Toda duplicación que se acepte por esta decisión necesita su assert**, y el assert se
escribe **junto con** la copia, no después: la primera vuelta de este cambio duplicó el
formato del reporte de verificación sin assert, y las dos copias nacieron divergentes en el
mismo commit. Lo cazó la revisión adversarial, no el gate.

**2. Lo opcional se marca, no se describe.** Las partes del contrato que dependen de una capa
opcional van entre marcadores `<!-- OKF:future-layer:start -->` / `:end`. La instalación
mínima es "borrá lo que está entre los marcadores", un rango — no una lista en prosa que hay
que mantener sincronizada con el archivo que describe. Cualquier capa opcional futura usa el
mismo mecanismo.

# Consecuencias

- `okf-plan` creció (trae los dos esqueletos) y `okf-verify` también (trae su formato de
  reporte). Es el precio de que funcionen solos.
- El contrato se mantuvo en ~1600 tokens instalados pese a sumar marcadores y reglas: los
  marcadores no se cuentan (se borran siempre) y se recortaron los punteros muertos. **El
  número exacto no se transcribe a mano en ningún lado** — lo imprime `okf_selfcheck.py` en
  cada corrida (criterio de la [decisión 0010](0010-generated-volatile-facts.md): un hecho
  volátil copiado a mano driftea, y este ya driftó dos veces en este mismo cambio).
- La instalación mínima quedó medida y coherente: ~1300 tokens, conservando la garantía de
  "ir directo al código", que se movió fuera del bloque opcional.
- Asserts nuevos en `scripts/okf_selfcheck.py`: material instalado sin rutas del kit;
  marcadores balanceados **y alternados**; la versión mínima no puede mencionar la capa de
  futuro; y el formato del reporte tiene que coincidir entre sus dos copias. Cada uno
  encontró algo real apenas se escribió.
- **Los marcadores solo cubren el contrato.** Los otros archivos que se instalan en los dos
  niveles (`okf-update`, `okf-verify`) no pueden usarlos —no se recortan al instalar— así que
  ahí la capa de futuro se menciona **condicionada** ("si este repo lleva capa de futuro…").
  Es la variante que corresponde cuando el recorte no es posible.

# Verificación

```
python3 scripts/okf_selfcheck.py     # asserts "es autosuficiente" y "instalación mínima"
```
Y a mano, materializando el contrato mínimo (borrar los bloques entre marcadores) y
comprobando que no queda ninguna mención de la capa de futuro.
