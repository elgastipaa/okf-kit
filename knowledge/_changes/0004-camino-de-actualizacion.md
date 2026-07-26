---
type: Change
title: Un repo con OKF viejo se puede subir a la revisión actual del kit
description: Hoy el bundle se mantiene fresco pero el material instalado (contrato, skills, scripts) se fosiliza en la versión con la que nació.
status: active
timestamp: 2026-07-26T00:00:00Z
---

# Por qué

El kit tiene camino de **instalación** y no de **actualización**. El bundle se mantiene
fresco —`okf-update` hace eso— pero el material instalado (el `AGENTS.md`, los skills, los
scripts) queda congelado en la revisión con la que el repo nació. Medido: `idlerpg` y
`forgeidle` corren `kit_version: 0.5.0` y no tienen **nada** de 0.6.x — ni capa de futuro, ni
la regla descriptivo/normativo, ni `okf_stale.py`, y sus contratos son anteriores al trabajo
de presupuesto y marcadores.

Tres huecos concretos:

- **No existe el procedimiento.** `grep` de "actualizar el kit" / "re-copiar" / "upgrade" en
  `reference/maintaining.md`, `okf-update` y `GUIDE.md` no devuelve nada.
- **`kit_version` no lo consume nadie.** La [decisión 0003](../decisions/0003-kit-version-vs-okf-version.md)
  la creó "para que el repo sepa de qué revisión del kit nació" y **nada la lee** para hacer
  algo. Mismo patrón que `resource:` antes del cambio 0003: una clave escrita con cuidado que
  nadie usa.
- **`okf-init` rutea mal.** Ante un `knowledge/` existente manda a `okf-update`, que mantiene
  *contenido* y no puede tocar el material instalado — no tiene el kit en disco.

# Resultado esperado (la spec)

- **CUANDO** se apunta un agente con el kit a un repo que ya tiene OKF de una revisión
  anterior → **ENTONCES** detecta el desfase leyendo el `kit_version` del bundle y dice qué
  cambió entre esa revisión y la actual, sin que el usuario tenga que saber que existe una.
- **CUANDO** se actualiza el material instalado → **ENTONCES** el contenido del bundle
  (conceptos, decisiones, log) **no se toca**: son cosas distintas y confundirlas pisaría
  conocimiento del proyecto.
- **CUANDO** el repo eligió la instalación **mínima** → **ENTONCES** la actualización la
  respeta y no le mete la capa de futuro por la ventana.
- **CUANDO** hay cambios locales en el material instalado (reglas duras propias del repo en su
  `AGENTS.md`) → **ENTONCES** no se pisan en silencio: se avisa qué se conserva y qué se
  reemplaza.
- **CUANDO** termina → **ENTONCES** el `kit_version` del bundle queda en la revisión nueva y
  el gate del repo (linter) pasa limpio.

# Fuera de alcance

- Migrar el **contenido** del bundle entre versiones del formato (`okf_version`): eso sería
  otra cosa y hoy el formato no rompió compatibilidad.
- Un cuarto skill. Se reutiliza el entrypoint que ya existe (`okf-init` detecta y rutea);
  agregar `okf-upgrade` sería más superficie para el mismo momento de uso.
- Automatizar el merge de un `AGENTS.md` con reglas duras propias. Se reporta y decide el
  usuario, como todo lo demás.

# Plan / Tareas

- [x] `reference/upgrading.md`: qué es material instalado vs contenido, y el procedimiento
- [x] `okf-init` detecta `kit_version` viejo y rutea a la actualización en vez de a `okf-update`
- [x] El `CHANGELOG` como fuente de "qué cambió entre tu revisión y la actual" (paso 1)
- [x] Probarlo de verdad: subir `idlerpg` de 0.5.0 a la actual — no se rompió nada
- [x] Asserts en `okf_selfcheck.py` (74) + caso en `okf_selfcheck_test.py` (20)

# Decisiones y descubrimientos en el camino

- **El bug era de ruteo, no de falta de doc.** `okf-init` ya detectaba un `knowledge/`
  existente, pero mandaba a `okf-update` — que mantiene *contenido* y **no puede** tocar el
  material instalado, porque corre sin el kit en disco. El desfase no era invisible: estaba
  mal atendido.
- **`kit_version` era la tercera clave escrita-y-nunca-leída** del kit, después de `resource:`
  (cambio 0003) y del `authority:` que sigue sin validarse. La [decisión 0003](../decisions/0003-kit-version-vs-okf-version.md)
  la creó "para que el repo sepa de qué revisión nació" y nada la consumía. Ahora es el
  disparador del camino de actualización.
- **El `AGENTS.md` es el único archivo con contenido mezclado**, y por eso el único que no se
  reemplaza entero: título/stack, reglas duras y placeholders completados son del proyecto;
  las secciones 1-3 y Procedimientos son del kit. Todo lo demás (skills, scripts, CI, hook) no
  tiene estado y se pisa sin pensar.
- **Probado de verdad sobre `idlerpg` 0.5.0 → 0.6.1: no se rompió nada.** El linter nuevo pasa
  limpio sobre el bundle viejo (el formato no rompió compatibilidad), el contrato quedó en
  6267 chars / ~1566 tokens, las 4 reglas duras y las capas no-autoritativas propias
  intactas, y la **instalación mínima se respetó** — cero huérfanos de la capa de futuro. El
  repo ganó la regla descriptivo/normativo, el guardrail del mapa, `status: accepted` en el
  keep-alive, `okf_stale.py` y el método del Nivel 2.
- **Trampa para quien re-valide esto:** si copiás el repo con `git init` + un commit, el
  historial se aplasta y `okf_stale` reporta churn=1 para todo lo que tenga `resource`. No son
  hallazgos: es el snapshot. Hay que clonar preservando historial.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" (probado de verdad, no asumido)
- [ ] Decisiones/descubrimientos → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Si el harvest creó una **carpeta** nueva, sumada al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado
- [ ] Borrar este archivo (git conserva la historia). **Ningún doc permanente puede quedar
      linkeando a `_changes/`** — cortá ese link primero (solo el roadmap linkea acá).
