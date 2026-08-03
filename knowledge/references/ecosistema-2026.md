---
type: Reference
title: El ecosistema de herramientas de contexto, agosto 2026
description: "Qué hacen seis herramientas del ecosistema con el problema de instalar y actualizar material en repos ajenos, y qué de eso no hay que copiar."
tags: [ecosistema, competencia, upgrade]
timestamp: 2026-08-03T00:00:00Z
---

Resumen del análisis de seis repos hecho en agosto de 2026. Existe para no volver a
investigarlo, y sobre todo **para no reintroducir por intuición cosas que ya vimos fallar**.

# El problema del update: nadie lo resuelve bien

Los dos que instalan material en repos ajenos usan la misma estrategia —regenerar y pisar— y
ninguno mergea:

- **OpenSpec** sella con la versión y decide por ahí. Editás el cuerpo, dejás el frontmatter,
  y se pisa en silencio al próximo bump. Protege lo del usuario **poniéndolo en archivos
  aparte que nunca escribe**, que es una idea buena y distinta de la nuestra.
- **rulebook-ai** no tiene update: `sync` borra y regenera. `--assistant claude-code` hace
  `unlink()` del `CLAUDE.md` del usuario; `--assistant cursor`, `rmtree('.cursor')`.

**Lo que sí robamos:** la clasificación de tres desenlaces antes de reemplazar
([0025](../decisions/0025-el-material-instalado-se-sella-con-hash.md)), y el eje correcto de
una migración — **no es automático vs manual, es separable vs entrelazado**. OpenSpec
automatiza lo separable y solo pide intervención en lo que no lo es; nosotros nos plantábamos
en todo. Sus tres cubetas coinciden con las nuestras por evolución convergente, lo que es
buena señal del diseño de la [0024](../decisions/0024-el-contrato-se-actualiza-por-secciones.md).

# Marcadores en el archivo del usuario: probado y abandonado

Era el candidato natural para actualizar un archivo compartido. **OpenSpec los tuvo y se
arrepintió**: hoy sus `OPENSPEC_MARKERS` solo sirven para detectar material legacy y sacarlo.
La evidencia física es que el `AGENTS.md` de la raíz de su propio repo pesa **0 bytes**,
sedimento de esa migración. No los reintroduzcas.

# Externalizar reglas a datos no salva de la deriva

**speccy** declara sus reglas de lint en YAML, con herencia y override — buen diseño, y por eso
un usuario puede agregar una regla sin forkear. Pero además mantiene **una segunda copia a
mano para documentarlas**, y esa copia ya divergió: le faltan campos y reglas enteras.

La lección no es "no externalices": es que **la deriva la causa duplicar, no el formato**. Por
eso los ids de regla del linter viven en el código y no en un YAML paralelo.

# Lo que capturan ellos y el kit no capturaba

- **El comando que prueba que el código anda.** Los PRPs de `context-engineering-intro` traen
  *validation gates* ejecutables; nuestro doc de cambio pedía "probado de verdad" **sin decir
  con qué**. De ahí salió `knowledge/checks.md`.
- **Restricciones de tipo sobre el artefacto** (`mattpocock/skills`): un doc que tiene
  *prohibido* contener detalles de implementación no puede ser la respuesta. Es estructural en
  vez de exhortativo y cuesta cero contexto — el candidato más prometedor contra nuestra
  regresión de acierto, y todavía sin medir.
- **La navaja no-op**: borrás una frase, medís, y si no cambia nada la frase no estaba
  haciendo nada.

# El mercado

Sobre 131 entradas de `awesome-vibe-coding`, la relación generación:contexto es **7,5 a 1**, y
**ninguna** hace lo que hace OKF. No es mercado virgen: Kilo Code deprecó su Memory Bank *"en
favor de AGENTS.md"*, y AGENTS.md tiene 60k repos y formato libre. **OKF no compite con nadie
de la lista — compite con "meto todo en el AGENTS.md"**, y la ventana es *"mi AGENTS.md se
convirtió en un despelote"*.

Y **"nadie mide" es falso**: [CCPM](https://github.com/automazeio/ccpm) publica un badge
`eval_score 100%` y una tabla de 100% contra 27,7%. Lo defendible no es *que* medimos sino
**cómo**, y que publicamos también cuando da negativo.

# Citations

- `Fission-AI/OpenSpec` · `botingw/rulebook-ai` · `wework/speccy` ·
  `coleam00/context-engineering-intro` · `mattpocock/skills` ·
  `filipecalegario/awesome-vibe-coding` (clonados en agosto de 2026)
- [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) — Gloaguen, Mündler, Müller, Raychev,
  Vechev (SRI Lab, ETH Zürich): los context files no mejoran el acierto y cuestan >20% más.
- [CCPM](https://github.com/automazeio/ccpm) — el único competidor que publica una medición.
