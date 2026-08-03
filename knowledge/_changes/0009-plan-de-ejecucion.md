---
type: Change
title: Cola de ejecución de las fases 1 a 4 del plan del ecosistema
description: "La cola ordenada de trabajo pendiente, con el criterio de hecho de cada ítem y qué puede hacerse solo y qué necesita al usuario."
status: active
timestamp: 2026-08-03T00:00:00Z
---

# Por qué

El análisis de seis herramientas del ecosistema produjo un plan de cuatro fases. La fase 0
está cerrada. Este doc es **la cola de las fases 1 a 4**, escrita para poder ejecutarse de a
un ítem por iteración, incluso por una sesión que no vio nada de la conversación original.

Existe porque el trabajo ya no entra en una sesión: son ~20 ítems, algunos dependen de otros,
algunos cuestan plata y algunos **no los puede decidir un agente**. Sin esta cola, cada sesión
nueva volvería a discutir el orden.

# Cómo se ejecuta una iteración

1. **Leé este archivo y elegí el primer ítem no tildado y no bloqueado**, en orden. El orden
   importa: los ítems de arriba desbloquean a los de abajo.
2. **Hacelo completo**: código + docs + `decisions/` si hay una decisión no trivial + gate.
3. **Todo assert nuevo va con su rotura probada** en la suite que corresponda. Un assert que
   nunca se probó rompiendo es decoración — la regla dura del repo.
4. **Verde obligatorio antes de commitear**: `python3 scripts/okf_selfcheck.py` y las tres
   suites (`okf_selfcheck_test.py`, `okf_lint_test.py`, `okf_stale_test.py`).
5. **Un commit por ítem**, tildá acá, y pará. No encadenes dos ítems en una iteración: si el
   segundo sale mal, el primero se pierde en el mismo revert.

## Reglas duras de la cola (violarlas es el fracaso, no el retraso)

- **No agregues prosa al contrato instalado sin medirlo.** Está medido que no mueve el
  acierto ([0023](../decisions/0023-verificar-siempre-no-paga.md)), y el presupuesto son 7000
  chars con ~88 libres. Si un ítem necesita lugar, **recortá primero** y mostrá el número.
- **No gastes plata sola.** Toda medición con `claude -p` cuesta y necesita autorización
  explícita del usuario, por ítem. Los ítems marcados 💰 **se preparan y se dejan listos**,
  no se corren.
- **No decidas por el usuario.** Los ítems marcados 🙋 se dejan escritos con la pregunta
  concreta y se saltean.
- **Si un ítem resulta más grande de lo que dice acá, partilo** y anotá la partición en vez
  de hacer medio ítem.
- **Si algo se contradice con lo que encontrás en el código, gana el código** y avisá: este
  doc es descriptivo, no normativo.

---

# Fase 1 — el producto (lo que el mercado pide)

## [x] 1.0 · Cosechar el cambio 0008 (fase 0)
Está terminado salvo el inventario de retirados, que se saltó a propósito. Cosechalo:
decisiones al bundle, `log.md`, roadmap, y borrar `0008-*.md`. **Hacelo primero**: el repo
tiene la regla de ≤1 cambio activo y ahora hay dos.

## [x] 1.1 · `okf-migrate` pasa al frente
**De dónde sale:** el análisis de mercado. Sobre 131 entradas de `awesome-vibe-coding`,
ninguna hace lo que hace OKF, y el mercado ya eligió AGENTS.md por default (60k repos, Linux
Foundation, *"usá los títulos que quieras"*). La ventana real no es "montá contexto de cero"
sino **"mi AGENTS.md se convirtió en un despelote"**. El usuario ya aceptó el cambio de
posicionamiento: **migrate es el producto, init el accesorio.**

**Hecho cuando:** el `README.md` y el `README.en.md` abren el camino de instalación por
migrate (init queda como el caso del repo limpio, no al revés); el orden en
`.claude-plugin/plugin.json` lo refleja; `GUIDE.md` presenta primero el brownfield. Sin
cambios de comportamiento en el instalador — es posicionamiento.

**Riesgo:** bajo. **Gate:** el de siempre; `reference/*` sigue resolviendo.

## [x] 1.2 · `--pack`: empaquetar el bundle sin depender de Repomix
**De dónde sale:** `resolve.js` de speccy. La decisión clave que copiamos es **externos se
inlinean, internos quedan como punteros**: un pack que inline todo copia el mismo concepto N
veces y fabrica la deriva que el kit combate.

**Hecho cuando:** `okf_lint.py --pack` (o un script nuevo) emite el bundle como un solo
markdown navegable, con visited-set contra ciclos, y `reference/optional-tools.md` deja de
recomendar Repomix —una dependencia de npm— para el caso "leé todo el bundle de una".

**Riesgo:** medio (es código nuevo). **Gate:** su rotura + que el pack de un bundle con
ciclos termine.

---

# Fase 2 — lo que hay que medir antes de creerlo

> Todos estos ítems dependen del instrumento, que ya está arreglado (cambio 0005). Ninguno se
> da por bueno sin correr la medición, y **la medición cuesta plata**.

## [ ] 2.1 🙋 · El golden-set de "por qué"
**El hallazgo que lo motiva:** las 7 preguntas con las que medimos todo son de **recuperación
de hechos** ("¿cuántos?", "¿a qué nivel?", "¿cuál es el último?"). Ninguna pregunta *por qué*.
Y [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) dice exactamente eso: los overviews no
ayudan, y lo único que paga (+4%) es lo que un humano sabe y el código no puede decir.
**Medimos con precisión el eje donde ya se sabía que no se gana.**

**Bloqueado por una decisión del usuario:** el acierto de un "por qué" **no se puede verificar
contra el código** —el código no lo contiene—, así que el ground truth lo tiene que dar él, o
se valida contra las `decisions/` que escribió el agente ciego, que es circular. **La pregunta
concreta para Gasti:** *¿me dictás vos las respuestas correctas de 5-7 "por qué" sobre
idlerpg, o preferís que el brazo se mida solo por "¿admitió que no lo sabe?" en vez de por
acierto?*

**Hecho cuando:** existe `eval/idlerpg/golden-set.porque.md` con su ground truth declarado y
su origen, y `grade.md` dice cómo se juzga un "por qué".

## [ ] 2.2 💰 · `fuente primaria` como palabra líder
**De dónde sale:** `mattpocock/skills`. Es la versión **barata** de lo que la 0022 intentó y
falló: en vez de mandar a verificar siempre (+28% de turnos), dos tokens que anclan la
conducta. Reemplaza el bloque "MAPA no la respuesta" (444 chars → ~160) y **libera ~280**.

**Hecho cuando:** está escrito, el presupuesto lo muestra, y **está medido** con los tres
brazos. **Gate duro, escrito antes de mirar:** acierto ≥ el de la línea de base sin empeorar
turnos por encima del ruido. Si no, se revierte como la 0022.

## [ ] 2.3 💰 · Restricción de tipo sobre el artefacto
**De dónde sale:** `domain-modeling/SKILL.md` de Matt Pocock, que **prohíbe** que un doc
contenga detalles de implementación. Es lo único del análisis que ataca nuestro modo de falla
medido **sin agregar prosa al contrato**: es estructural, no exhortativo, y cuesta cero
contexto. La idea: que un tipo de concepto declare qué **no puede** contener, y que el linter
lo verifique.

**Hecho cuando:** existe la convención, el linter la chequea con su id de regla y su rotura,
y hay una hipótesis escrita de por qué debería mover el acierto. **Medir antes de venderlo.**

## [ ] 2.4 💰🙋 · La dieta del contrato con la navaja no-op
**De dónde sale:** Matt Pocock (borrás una frase, medís, y si no cambia nada la frase no
estaba haciendo nada) + la lente B (§2 del contrato es 24% del always-on y **no paga en
turnos de lectura**).

**Bloqueado:** recortar §2 tensiona con la
[0013](../decisions/0013-installed-material-is-self-sufficient.md), que exige que un agente
sin skills pueda mantener el bundle solo con el contrato. Eso se **supersede o se acota**, no
se edita — y es una decisión de producto, no una optimización.

**[x] Sub-ítem hecho (autónomo):** el gate ahora mide el always-on **real**. Números: contrato
6.912 + shim 11 + descripciones de skills 1.406 = **8.329 chars ≈ 2.082 tokens por turno**,
contra los 6.912 que medía — un punto ciego del 20%, y creciendo sin que nadie lo mirara.
`ALWAYS_ON_BUDGET = 8600` es un **cable trampa** sobre los canales invisibles, no un límite
negociado como el 7000 del contrato.

**Lo que sigue bloqueado** es recortar §2, que es la decisión de producto.

---

# Fase 3 — matar (el kit tiene que adelgazar, no solo crecer)

## [ ] 3.1 🙋 · Perfiles `datos` y `wiki`
**Evidencia a favor de matarlos:** 0 de 131 entradas del mercado son de datos o wikis.

**BLOQUEADO — la clasificación original de este ítem como autónomo estaba mal.** Al ir a
hacerlo apareció que no es una limpieza interna sino una decisión de producto:

1. La [0006](../decisions/0006-dogfood-profile-choice.md) es **normativa y `accepted`**: el kit
   se dogfoodea con perfil `mixto`, definido como *"combinando carpetas de Código y de Wiki"*.
   Matar `wiki` deja esa decisión hablando de un vocabulario inexistente — habría que
   supersederla.
2. El `README.md` promete **"agnóstico al dominio: código, datos/analytics y wikis"** y la
   visión del roadmap dice "aplicable a cualquier repo". Es una promesa pública.
3. `--profile datos` es contrato de CLI: rompe a quien ya lo usó.

**La pregunta para Gasti:** *¿achicamos el alcance declarado del kit a repos de código
—que es lo que el mercado pide y lo único que medimos—, o mantenemos la promesa
multi-dominio aunque nadie la use?* Si va lo primero, arrastra superseder la 0006 y reescribir
la promesa del README.

## [x] 3.2 · `log.md` pasa a opt-in
**Evidencia:** 0 citas en 61 corridas medidas, contra 13 ediciones en la historia del propio
kit. El contrato ya lo trata como opcional (*"si mantenés `log.md`"*) pero el instalador lo
pone siempre y el keep-alive lo exige. El log real es `git log` + `decisions/`.

**Hecho cuando:** el instalador no lo siembra salvo `--with-log`, sale de `KEEPALIVE_TOKENS`,
y el gate se ajusta con su rotura.

## [x] 3.3 · El linter y los 4 niveles dejan de ser pitch
**Evidencia:** 0 hits de demanda de "linter" o "conformidad" en 131 entradas, y ocupan tres
filas del README. **Se mantiene el mecanismo, se deja de vender.** Es edición de README y
GUIDE, no borrado de código.

## [x] 3.4 · `OKF-SPEC.md` deja de ser puerta de entrada
**Decidido:** se queda como base del formato —es el linaje de Google Cloud, la base de la
licencia Apache y el contrato del linter—, pero **el usuario nunca necesita aprender la
palabra "OKF"**: recibe una carpeta de markdown con frontmatter. La spec pasa a referencia
para quien implementa.

**Hecho cuando:** el README no abre por el formato, y la spec queda linkeada como referencia.
**Sub-ítem aparte:** declaramos OKF 0.1 y el upstream va por **0.2** — decidir si subimos o
si decimos explícitamente que condensamos 0.1.

---

# Fase 4 — que exista para alguien que no nos conoce

## [x] 4.1 · Paridad del `README.en.md`
**Evidencia:** el 100% de ese mercado escribe en inglés y el README inglés es **42% más
corto** que el castellano: al anglohablante le damos la versión degradada. Los disparadores
ya son bilingües (fase 0); falta la puerta.

## [ ] 4.2 🙋 · Publicar la medición
Hoy `/eval/` está gitignoreado, o sea que **el diferencial está oculto en el propio repo**. Y
"nadie mide" es falso: [CCPM](https://github.com/automazeio/ccpm) publica un badge y una tabla
100% vs 27,7%. Lo defendible no es *que* medimos sino **cómo**: n≥3 con dispersión, brazo sin
capa que aparta los archivos de verdad, juez que verifica contra el código, veredicto de
premisa falsa, y **publicar también cuando da negativo**.

**Decisión del usuario:** qué se publica. Los scorecards tienen respuestas completas sobre sus
repos privados.

## [ ] 4.3 · Un repo de ejemplo clonable
El antes/después de un init real con el diff visible. Hoy la única prueba navegable es el
dogfood, que está enterrado. Es lo que convierte a un desconocido.

## [~] 4.4 · Mueblería de adopción
**Hecha la parte autónoma:** `CONTRIBUTING.md` (con las tres reglas no negociables y el
método de medición) y los badges del README.

**Falta lo que va hacia afuera y necesita tu OK:** topics de GitHub, el asciinema de 30s del
init, y el PR a `awesome-vibe-coding` — publicar en el repo de otro no lo decide un agente.

---

# Lo que queda abierto y NO está en esta cola

- **La regresión de acierto sigue sin fix.** La medición dio 4 fallos contra 0 de no tener
  capa; el primer intento (0022) se revirtió. **Ninguna de estas fases la resuelve**, y es el
  problema más grande del kit. Los ítems 2.2 y 2.3 son los dos candidatos.
- **Medir `the-conclave`** (¿paga donde el routing es difícil?): arrastra aplicarle el kit a
  ciegas a un repo de 12 GB. Caro; después de la fase 2.
- **El inventario de archivos retirados**: se agrega el día que se retire el primer archivo
  instalado, con su rotura. Hoy sería una constante vacía, o sea decoración.

# Decisiones y descubrimientos en el camino

{{Anotá acá lo que aparezca mientras se ejecuta la cola: cada iteración que descubra algo no
trivial lo deja escrito antes de cerrar, y el harvest lo convierte en `decisions/`.}}

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado que cada ítem tildado tiene su commit y su gate en verde
- [ ] Decisiones/descubrimientos de arriba → `knowledge/decisions/` (+ índice)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: lo que quedó sin hacer vuelve a "Después" con su motivo
- [ ] Borrar este archivo (git conserva la historia)
