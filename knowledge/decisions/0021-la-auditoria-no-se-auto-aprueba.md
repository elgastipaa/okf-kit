---
type: Decision
title: La auditoría del bundle la corre un revisor que no vio el trabajo
description: "Los Niveles 2 y 4 de verificación se delegan a contexto fresco con un revisor que no puede editar, porque quien escribió un concepto o el código no puede auditarlo sin sesgo."
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*revisor con contexto fresco"
tags: [verificacion, roles, drift, cumplimiento]
timestamp: 2026-07-30T00:00:00Z
resource: ../../templates/agents/okf-reviewer.md
---

# Contexto

`okf-verify` tiene cuatro niveles. El **Nivel 3** (test de comportamiento) ya exigía contexto
fresco y lo decía explícitamente. Pero los **Niveles 2** (drift descriptivo) y **4**
(cumplimiento) los corría **la misma sesión que escribió los conceptos y el código** — y son
justo los dos donde el sesgo pesa más:

- El método del Nivel 2 es *"buscá la contradicción, no la confirmación"*. Quien redactó el
  concepto lo lee sabiendo lo que quiso decir; no puede refutarse a sí mismo.
- El Nivel 4 audita si el **código** viola lo normativo. Quien escribió ese código va a
  racionalizar: es conflicto de interés, no falta de método.

**No era una apuesta nueva.** El propio kit ya usa esta práctica para desarrollarse: el
cold-review de 4 lentes de `DEVELOPING.md`, al que su `log.md` le acredita 2 blockers y ~12
majors en una sola pasada sobre 0.6.0, y la v0.4.0 entera. Era una práctica **kit-only**: un repo
que recibía OKF no recibía nada equivalente.

La comparación con [`harness-sdd`](https://github.com/betta-tech/harness-sdd) puso el tema sobre
la mesa con sus cuatro roles (leader / spec_author / implementer / reviewer). De esos cuatro, el
único que paga para un usuario solo es el revisor: el resto es ceremonia de equipo grande, que el
kit ya había rechazado por la misma razón al no adoptar los deltas de OpenSpec.

# Decisión

El kit instala un **subagente revisor** (`okf-reviewer`) y `okf-verify` **delega** en él los
Niveles 2 y 4 **cuando la sesión que audita es la que hizo el trabajo**. Tres propiedades hacen
el mecanismo, y ninguna es opcional:

1. **Contexto fresco.** No vio el trabajo, y tiene prohibido pedir la intención de quien lo hizo:
   si le falta información para juzgar, *ese es el hallazgo*.
2. **No puede editar** (`disallowedTools`, y repetido en el cuerpo). Un revisor que arregla lo que
   encuentra vuelve a ser el autor. La asimetría **es** el mecanismo.
3. **Consigna refutatoria.** Y un reporte con la sección obligatoria *"lo que intenté refutar y
   no pude"*: sin eso, un reporte vacío no se distingue de una auditoría que no se hizo.

**Vendor-neutral:** sin subagentes, el mismo archivo se sigue como procedimiento en un proceso o
CLI nuevo — la misma salida que el Nivel 3 ya usaba. Y el revisor se **instala en el repo
destino** (no lo shippea el plugin), por la
[0013](0013-installed-material-is-self-sufficient.md) y la
[0018](0018-plugin-shippea-solo-el-bootstrap.md).

# Consecuencias

- **El contrato no creció ni un carácter**: está al 95% de su presupuesto, y esto es un detalle
  de implementación de `okf-verify`. Cualquier capa nueva del kit tiene que cumplir eso.
- El modelo sigue siendo de **tres capas**. No se agregó una capa de orquestación: se agregó un
  ejecutor para dos niveles de un procedimiento que ya existía.
- **Un harvester con contexto fresco sería peor, y queda como no-goal**: el harvest necesita
  saber qué pasó durante el trabajo, y eso lo tiene la sesión que lo hizo (para eso existe la
  sección de staging del doc de `_changes/`). Contexto fresco ayuda a *auditar*, no a *recordar*.
- El revisor no corre el Nivel 1 (determinista: no gana nada con ojos nuevos) ni el 3 (que ya
  tiene su propio agente aislado). Ampliar su alcance sería pagar tokens sin comprar nada.
