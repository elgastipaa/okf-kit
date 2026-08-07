---
type: Decision
title: La capa de futuro — roadmap como concepto + _changes/ efímera con harvest
description: "El kit cubre el trabajo futuro con dos piezas: el rumbo vigente es un concepto (roadmap.md) y cada cambio no trivial es un doc efímero en _changes/ que muere en un harvest."
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*nombra las tres piezas de la capa de futuro"
tags: [future-work, spec-driven, roadmap]
timestamp: 2026-07-26T00:00:00Z
---

# Contexto

El objetivo del kit es ingeniería de contexto **completa**: ordenar el pasado
(`decisions/`, log), entender el presente (los conceptos) y facilitar el trabajo
futuro. Pero hasta la v0.5.0 el futuro estaba **excluido a propósito**: la
[spec](../references/okf-format.md) manda que los conceptos describen estado
presente, sin planes ni checkboxes, y el entrypoint declara los "planes viejos"
como [capa no-autoritativa](0008-declare-non-authoritative-layers.md). Eso dejaba
el nicho que herramientas como OpenSpec/spec-kit cubren con *spec-driven
development* (proposal → spec → tasks → implementar → archivar). El público
objetivo del kit —proyectos que se desarrollan conversando con IAs ("vibecoding")—
es justo el que más pierde el rumbo sin esa capa: scope creep, features a medias,
"¿en qué estábamos?" irrecuperable entre sesiones.

Alternativas: (a) delegar en OpenSpec (contradice
[vendor-neutral / sin apps](0004-vendor-neutral-no-external-apps.md) y duplicaría
entrypoints); (b) hacer de los planes conceptos del bundle (rompe "concepto =
estado presente" y fabrica la fuente de rot que 0008 combate); (c) una capa propia
liviana con ciclo de cierre.

# Decisión

Se adopta (c), con una separación en dos piezas que preserva la spec intacta:

- **El rumbo es estado presente** → `knowledge/roadmap.md` es un concepto normal
  (`type: Roadmap`): visión, "Ahora", "Después", no-goals. Se **edita** cuando la
  intención cambia; sin checkboxes.
- **El plan de un cambio concreto NO es un concepto** → vive en
  `knowledge/_changes/NNNN-<slug>.md` (el prefijo `_` ya existente lo deja fuera
  del bundle conforme): mini-spec (por qué, resultado esperado, fuera de alcance),
  tareas con checkboxes y decisiones staging. Nace antes de codear y **muere en un
  harvest** hacia el bundle (decisiones → `decisions/`, estado → conceptos, roadmap
  al día), tras lo cual el doc se borra (git guarda la historia).

El ciclo (abrir / retomar / cerrar) es el skill `okf-plan`; los templates son
`_roadmap.md` y `_change.md`. Es spec-driven development liviano, sin herramienta
nueva: markdown + git.

# Consecuencias

- `_changes/` es la **única capa de planes tolerada**, precisamente porque tiene
  ciclo de cierre; todo otro plan suelto sigue siendo no-autoritativo (0008).
- El riesgo nuevo es el **cambio zombie** (done sin harvest, o abandonado): lo
  mitigan las reglas de `okf-plan` (borrar tras harvest, máx. ~3 activos, roadmap
  de una pantalla) y la señal anti-rot en `reference/maintaining.md`.
- Los cambios nunca son fuente de estado del código — "gana el código" se mantiene.
- Pendiente (criterio [reactivo, no especulativo](0010-generated-volatile-facts.md)):
  validar la capa midiendo en los repos conejillo del eval antes de complejizarla. El
  trabajo abierto está en el [rumbo](../roadmap.md) — un doc permanente no linkea a
  `_changes/`, que es efímero por diseño.

# Verificación

**El disparo no depende de que el usuario nombre nada** — que era el riesgo de adopción más
serio, porque el público objetivo no va a recordar un procedimiento. Por eso los
disparadores viven en el `AGENTS.md` (que toda herramienta lee), no solo en el skill (que
solo existe en Claude Code).

Testeado (2026-07-26) con un **agente en frío** sobre un repo fixture con la capa instalada,
recibiendo un mensaje de usuario no técnico ("quiero un ranking… y que se guarde la
partida"), sin ninguna mención al kit ni a `okf-plan`. Resultado: leyó el contrato → índice →
rumbo → cambio activo → decisiones → código; **abrió con la línea de continuidad** ("venías
con los sonidos, falta cablear X"); **no escribió código**: negoció primero el criterio de
"listo" en lenguaje llano; detectó que el pedido **violaba una decisión aceptada** (ranking
vs. "sin backend") y ofreció las dos salidas legítimas en vez de implementar o de editar la
decisión; y **no usó una sola palabra de jerga OKF** con el usuario (dijo "se guarda en tu
navegador", nunca `localStorage` ni `_changes/`). También destapó un hueco de diseño que el
pedido no veía (sin fin de partida, la tabla de récords tendría una fila).
