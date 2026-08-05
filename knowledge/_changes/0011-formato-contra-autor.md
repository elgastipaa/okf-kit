---
type: Change
status: in-progress
title: Separar el formato del autor — ¿el kit recupera solo lo que un humano escribió a mano?
description: "Tercer brazo sobre the-conclave: un bundle generado por okf-init a ciegas, contra la wiki que escribió el dueño del repo y contra no tener nada."
tags: [okf, eval, alcance]
timestamp: 2026-08-05T00:00:00Z
---

# El problema

El mejor número del kit —**−34% de turnos y 14/15 de acierto contra 10/15**— se midió sobre
`the-conclave` con **la capa que escribió el dueño del repo a mano**. Eso deja la pregunta
importante sin contestar:

> ¿Ganó **el formato OKF**, o ganó **que Gasti sabe su repo y escribió una wiki buenísima**?

Si fue lo segundo, el kit no está vendiendo lo que cree: `okf-init` sobre un repo ajeno no
produciría nada parecido, y la promesa honesta sería "te damos un formato para escribir vos",
no "corré esto y tenés la capa".

# Diseño

Tres brazos, **mismo repo, mismas 5 preguntas, n=3**:

| brazo | estado del repo | quién escribió la capa | estado |
|---|---|---|---|
| **N** | sin front door (`docs/wiki`, `AGENTS.md`, `CLAUDE.md` apartados) | nadie | medido: 7.73 turnos, 10/15 |
| **W** | front door humano presente | el dueño, a mano | medido: 5.07 turnos, 14/15 |
| **K** | sin front door **+ bundle de `okf-init`** | el kit, a ciegas | **este cambio** |

`K − N` = lo que agrega el kit solo. `W − N` = lo que agrega el autor humano. `K` contra `W`
es la respuesta.

**La instalación es ciega de verdad**: corre en un proceso `claude -p` fresco que no vio la
golden set, con la instrucción explícita de no abrir `eval/`. Yo sí conozco las preguntas, así
que no toco el bundle ni contesto las preguntas abiertas que deje el init — el brazo mide
*instalar y soltar*, que es lo que haría un usuario sin nadie al lado.

Rama `okf-bundle` de `the-conclave`, sacada del mismo commit que los otros dos brazos.

<!-- GATE ESCRITO ANTES DE MIRAR EL RESULTADO (decisión 0028). No editar después. -->

# Gate

**Ruido de referencia**: la dispersión intra-condición en este repo es de ~3.5 turnos (sd del
brazo N), o sea un error estándar de la media de **~0.9 turnos** con n=15. Una diferencia de
medias **menor a 1.0 turno se informa como indistinguible**, no como mejora.

**Validación previa a leer** (si algo de esto falla, el scorecard no se lee):
- 15/15 corridas completas, **0 fallidas**.
- `mutated_repo` en falso en las 15.
- El bundle en disco al terminar la medición es byte-idéntico al commiteado.

**Lectura pre-registrada** — cuál de las tres se cumpla es el resultado:

1. **El formato carga el peso**: `|K − W| < 1.0` turno **y** el acierto de K está a lo sumo una
   celda de W (≥13/15). Es el resultado más fuerte posible y por eso el que más hay que
   desconfiar: si sale, se re-lee el bundle buscando por qué no puede ser cierto antes de
   publicarlo.
2. **El kit captura una parte**: K queda entre N y W. Se publica la fracción recuperada
   (`(N−K)/(N−W)`) sin redondearla para arriba.
3. **El valor era el autor**: `K ≥ N − 1.0` turno, o acierto de K ≤ N (10/15). Es un resultado
   **negativo y se publica igual** (0028 §4), y obliga a cambiar lo que el kit promete: pasa a
   ser un formato para que escribas vos, con routing, no una capa que se genera sola.

**Regla anti-autoengaño** (0028 §3): si K baja turnos pero mete errores nuevos —cualquier
`incorrecta`/`inventada`, o más `parcial` que W— **el brazo se rechaza** por más lindo que sea
el promedio. Una respuesta rápida y equivocada es peor que una lenta y correcta.

**Se cuenta aparte, y no como acierto**: cuántas preguntas abiertas dejó el init y si alguna
apunta a algo que la golden set pregunta. Eso mide la **elicitación** —el valor que ya se vio
en `forgeidle`— y es una promesa distinta a la de recuperar hechos.

# Tareas

- [x] Rama `okf-bundle` con el front door humano apartado
- [x] Gate escrito antes de mirar
- [ ] Instalación ciega de `okf-init` (corriendo)
- [ ] Brazo K: `--repeat 3 --grade` sobre las mismas 5 preguntas
- [ ] Leer contra el gate y publicar, salga lo que salga
- [ ] Cosechar: decisión sobre el alcance del kit + roadmap
