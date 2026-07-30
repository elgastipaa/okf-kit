---
type: Change
title: El instrumento puede arbitrar mejoras del kit
description: "El harness pasa de medir n=1 con un juez ciego a poder distinguir una mejora real del ruido, y a comparar el kit contra no tener nada."
status: active
timestamp: 2026-07-30T01:19:38Z
---

# Por qué

Cuatro revisiones en frío sobre v0.7.3 (lentes A/B/C/D, anexos en esta misma carpeta)
llegaron por caminos independientes al mismo problema: **el kit no puede probar hoy lo que
promete, y su instrumento de medición es a la vez su único diferencial de mercado.**

- **Desde adentro (lente B):** el harness corre **n=1** y el ruido intra-condición medido es
  de **3,29 turnos por pregunta**. El `−31%` que publica `eval/COMPARISON.md` está
  concentrado en **una sola pregunta** (q7, una consulta *meta* de auditoría); sacándola, el
  efecto medio es **2,72 turnos con signo mixto** — por debajo del ruido. Además el juez
  corre **sin `cwd=repo`**, así que no puede verificar nada contra el código, y el brazo
  `nokit` **nunca se ejecutó** (61/61 corridas son `mode=kit`) y está contaminado por diseño.
- **Desde afuera (lente D):** [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) (Gloaguen,
  Mündler, Müller, Raychev, Vechev — SRI Lab, ETH Zürich; feb 2026, rev. jun 2026) mide que
  los context files **no mejoran el success rate y cuestan >20% más**. Lo único que dio
  positivo (+4%) es el contenido **escrito por humanos** que el código no puede decir; los
  *repository overviews* explícitamente no ayudan. Es la tesis de OKF confirmada por un
  tercero — y a la vez la primera objeción seria que el kit va a recibir.
- **La consecuencia práctica:** ninguna de las otras propuestas que dejaron las cuatro lentes
  (mecanismo 5, dieta del contrato, `runbooks/checks.md`) se puede aceptar ni rechazar con el
  instrumento actual, porque todas valen menos que 3,3 turnos. Y nadie en el mercado mide
  (verificado sobre Spec Kit 124.499★, OpenSpec 63.087★, Conductor 3.673★, cc-sdd): el único
  que midió es el paper, y su veredicto es negativo para el estado del arte.

Arreglar el instrumento es, entonces, la única tarea que **desbloquea** a las demás y **es**
el diferencial. Va primero. Ver [roadmap](../roadmap.md).

# Resultado esperado (la spec)

- **CUANDO** se corre el harness con `--repeat 3` → **ENTONCES** el scorecard reporta
  **mediana y spread** por pregunta, no un número único, y el reporte final distingue
  explícitamente "efecto por encima del ruido" de "indistinguible del ruido".
- **CUANDO** el juez evalúa una respuesta → **ENTONCES** corre **con `cwd=repo`** y verifica
  contra el código antes de dictaminar, y su costo (turnos y dólares) **se suma** al total
  reportado en vez de descartarse.
- **CUANDO** el juez recibe una respuesta que acepta una **premisa falsa** de la pregunta
  → **ENTONCES** la marca, aunque contenga todos los hechos del `expect` (hoy es invisible:
  es el falso positivo que ya documentó la [0014](../decisions/0014-future-layer-measured.md)).
- **CUANDO** se corre el brazo `nokit` → **ENTONCES** la capa de contexto **no está en el
  disco** durante la corrida (no se le pide al agente que la ignore), y queda registrado en
  el scorecard qué se movió.
- **CUANDO** se corre el brazo nuevo `--mode agentsmd` → **ENTONCES** se mide la condición
  "solo un AGENTS.md convencional, sin bundle", que es la comparación que exige el paper y la
  objeción del 90% de los usuarios.
- **CUANDO** se re-mide idlerpg con el instrumento arreglado → **ENTONCES** existe un número
  publicable con su intervalo, y `eval/COMPARISON.md` deja de afirmar `−31%` sin calificarlo.

Mientras este cambio esté activo, esto MANDA sobre "¿está terminado?".

# Fuera de alcance

Todo lo demás que encontraron las cuatro lentes. No entra acá, va al
[roadmap](../roadmap.md) y se decide **después**, ya gateado por el instrumento:

- **Mecanismo 5** ("el code-of-record cierra la búsqueda", lente B §7) — riesgo medio-alto,
  es exactamente la forma del falso positivo de q5; sin gate no se toca.
- **Dieta del contrato** (§2 = 24% del always-on que no paga en turnos de lectura) y
  extender `BUDGET` a los tres archivos always-on, no uno. Tensiona con la
  [0013](../decisions/0013-installed-material-is-self-sufficient.md): si se hace, se
  supersede o se acota, no se edita.
- **`knowledge/runbooks/checks.md`** (lente C): hoy "verificar" en el contrato instalado
  significa pasar el linter del bundle, y nada pregunta nunca si el código anda.
- **Bugs del camino libre** (lente A + B1): `okf-migrate` sin salida, disparadores que exigen
  conocer el kit, `/okf-init` que en realidad es `/okf:okf-init`, el "se revierte con
  `git checkout`" que es falso, y el `CLAUDE.md` que se instala con su comentario TEMPLATE
  adentro. Son bugs baratos y no necesitan medición — cambio aparte, no este.
- **Subir a OKF 0.2** (upstream ya estandarizó `status`, `stale_after`, `verified`,
  `generated`) y reescribir el README alrededor del paper.

# Plan / Tareas

- [ ] `run-eval.py --repeat N`: N corridas por pregunta, mediana + spread en el scorecard.
- [ ] Reporte final: marcar por pregunta si el efecto supera el spread observado.
- [ ] Juez con `cwd=repo` y prompt que exija verificar contra el código.
- [ ] Contabilizar el costo del juez (hoy se tiran `total_cost_usd`/`usage`).
- [ ] Segundo veredicto del juez: ¿la respuesta acepta una premisa falsa?
- [ ] Brazo `nokit` real: mover los archivos fuera del repo durante la corrida.
- [ ] Brazo `--mode agentsmd`: solo contrato convencional, sin bundle.
- [ ] Re-medir idlerpg con n≥3 y hand-verify; actualizar `eval/COMPARISON.md` con el número
      calificado (y corregir la afirmación de `−31%`).
- [ ] Gate del propio kit en verde (`okf_selfcheck.py` + las tres suites).

# Decisiones y descubrimientos en el camino

- El ruido intra-condición (3,29 turnos/pregunta) sale de tratar blind2 vs blind3 como
  réplica: la [0010](../decisions/0010-generated-volatile-facts.md) ya probó que ninguna pregunta leyó
  el archivo generado que las diferencia, así que son la misma condición corrida dos veces.
- El brazo `nokit` no se puede implementar pidiéndole al agente que ignore el contrato:
  Claude Code lo auto-carga en el prefijo antes de que el agente decida. Medir "sin kit"
  exige mover archivos.
- Hacer el juez configurable por variable de entorno (hoy `"claude"` está hardcodeado) **no**
  viola la [0004](../decisions/0004-vendor-neutral-no-external-apps.md): el harness es
  tooling de desarrollo opt-in que no se instala en repos destino, y configurarlo es *menos*
  vendor-lock, no más.
- El paper de ETH es munición y amenaza a la vez: valida "capturá el porqué, no el qué" y
  ataca el volumen del contrato genérico. Cualquier cosa que se agregue al always-on de acá
  en adelante tiene que justificar su peso contra ese resultado.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" de arriba (probado de verdad, no asumido)
- [ ] Decisiones/descubrimientos de arriba → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados (el concepto del harness de medición)
- [ ] Si el harvest creó una **carpeta** nueva, sumala al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado con lo
      que dejaron las cuatro lentes (ver "Fuera de alcance")
- [ ] Borrar este archivo **y sus cuatro anexos** `0005-anexo-lente-*.md` (git conserva la
      historia)
