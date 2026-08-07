---
type: Decision
title: "Material instalado y contenido del bundle envejecen distinto, y cada uno tiene su camino"
description: El bundle es del proyecto y lo mantiene okf-update; el contrato, skills y scripts son del kit y se reemplazan siguiendo reference/upgrading.md.
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*documenta cómo subir el material instalado"
resource: reference/upgrading.md
tags: [installation, lifecycle, kit-version]
timestamp: 2026-07-26T00:00:00Z
---

# Contexto

El kit tenía camino de **instalación** y no de **actualización**. Un repo con OKF contiene dos
cosas que envejecen distinto y se estaban tratando como una:

- **Contenido del bundle** — conceptos, decisiones, log: conocimiento **del proyecto**. Lo
  mantiene `okf-update`, que corre *dentro* del repo destino.
- **Material instalado** — `AGENTS.md`, skills, scripts: maquinaria **del kit**. `okf-update`
  **no puede** tocarlo: corre sin el kit en disco.

Consecuencia medida: dos repos conejillo corrían `kit_version: 0.5.0` sin nada de 0.6.x — ni
capa de futuro, ni la regla descriptivo/normativo, ni `okf_stale.py`, con contratos anteriores
al trabajo de presupuesto y marcadores. El kit mejoraba y sus usuarios quedaban atrás.

**El bug no era falta de documentación: era ruteo.** `okf-init` ya detectaba un `knowledge/`
existente y mandaba a `okf-update`, que no puede hacerlo. El desfase no estaba invisible;
estaba mal atendido.

# Decisión

**Se separan explícitamente, y cada uno tiene su procedimiento.** El de actualización vive en
`reference/upgrading.md` y `okf-init` rutea ahí cuando el `kit_version` del bundle es anterior
al `VERSION` del kit — sin cuarto skill: es el mismo momento de uso que el init, y agregar
superficie para eso sería peor.

Tres reglas del procedimiento, en orden de importancia:

1. **El contenido del bundle no se toca.** Es del proyecto. Confundirlo con lo otro pisaría
   conocimiento.
2. **Skills, scripts, CI y hook se reemplazan enteros**: no tienen estado del proyecto.
3. **El `AGENTS.md` es el único con contenido mezclado**, y por eso el único que no se
   reemplaza entero. Del proyecto (se conserva): título, stack, **reglas duras** y los
   `{{placeholders}}` completados. Del kit (se reemplaza): las secciones 1-3 y Procedimientos.
   Se le muestra al usuario qué se conserva y qué se reemplaza **antes** de escribir: acá es
   donde se pierde conocimiento si se hace en silencio.

La actualización **respeta el nivel de instalación**: a un repo en mínimo no se le mete la capa
de futuro por la ventana; si se quiere, se pregunta.

# Consecuencias

- **`kit_version` pasó de decorativa a disparador.** La
  [decisión 0003](0003-kit-version-vs-okf-version.md) la creó "para que el repo sepa de qué
  revisión nació" y **nada la consumía**. Es el tercer caso de una clave escrita con cuidado y
  nunca leída, después de `resource:` ([0015](0015-rankear-el-drift-antes-de-auditarlo.md)) y
  del `authority:` que sigue sin validarse. **Cuando el kit agrega una clave, hay que decir
  quién la lee** — si no, es ceremonia.
- El `CHANGELOG` entre dos revisiones deja de ser historia y pasa a ser la lista operativa de
  qué re-copiar.
- Probado subiendo un conejillo real de 0.5.0 a 0.6.1: **no se rompió nada**. El linter nuevo
  pasa limpio sobre el bundle viejo (el formato no rompió compatibilidad), el contrato quedó
  dentro del presupuesto, las reglas duras y capas no-autoritativas propias intactas, y la
  instalación mínima se respetó con cero huérfanos.

# Verificación

```
python3 scripts/okf_selfcheck.py   # existe el doc, okf-init rutea ahí, el GUIDE lo ofrece
```
Y a mano, la prueba que importa: subir un repo real de una revisión anterior y comprobar que el
bundle no se tocó, que el nivel de instalación se respetó y que su linter pasa limpio.
