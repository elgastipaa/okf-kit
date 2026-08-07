---
type: Decision
title: "Descriptivo vs normativo: la autoridad frente al código corre según el tipo de documento"
description: "Los conceptos descriptivos pierden contra el código; los normativos (decisiones aceptadas, convenciones, rumbo, cambios activos) obligan al código, y una violación se reporta en vez de emparejarse."
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*define la regla canónica de autoridad"
tags: [source-of-truth, future-work, spec-driven]
timestamp: 2026-07-26T00:00:00Z
---

# Contexto

La regla **"gana el código"** se escribió (v0.5.0) cuando el bundle solo tenía documentos
**descriptivos**: si un concepto contradice el código, el concepto miente y se arregla.
Enunciada sin tipos, esa regla tiene dos agujeros que aparecieron juntos:

1. Con la [capa de futuro](0011-future-work-layer.md) entró un documento que **promete** en
   vez de describir: el *Resultado esperado* de un cambio activo. Bajo "gana el código", un
   agente al que el código no le cumple lo prometido podía "resolver" la discrepancia
   **bajando la vara** en vez de terminar el trabajo.
2. El agujero más grande estaba desde antes y afectaba al corazón del bundle: una
   **decisión aceptada** también prescribe. Bajo "gana el código", código que viola un ADR
   convertía al ADR en el bug — es decir, el kit instruía a **borrar en silencio la razón
   por la que alguien decidió algo**. Para el usuario objetivo (proyectos desarrollados
   conversando con IAs) ese es el peor failure mode posible: "le dije hace tres sesiones que
   no hiciéramos X, y el código está lleno de X".

La comparación con OpenSpec ([interop](../../reference/spec-driven-interop.md)) hizo visible
la distinción: allá las specs son el contrato y el código que no las cumple es el bug — la
orientación inversa a la de OKF. Ninguna de las dos está mal: son **clases de documento
distintas**, y el error era tener una sola regla para las dos.

# Decisión

La dirección de la autoridad se **deduce del tipo de documento** (canónico:
`OKF-SPEC.md` §3.5; mapeo de `type`: `reference/profiles.md`; override opcional por
frontmatter `authority:`):

- **Descriptivo (default, la mayoría del bundle):** arquitectura, schema, dominio,
  runbooks, references, glosario, `_generated/`. Si difiere del código, **gana el código** y
  el documento es un bug. Sin cambios respecto de v0.5.0.
- **Normativo:** `Decision` con `status: accepted`, `Convention`, `Roadmap`, y el
  *resultado esperado* de un `Change` activo. Si el código difiere, **el código está en
  violación**.

Ante una violación hay **dos salidas legítimas y ninguna tercera**: arreglar el código, o
cambiar la decisión explícitamente (documento nuevo que la *supersede*). **Editar el
documento normativo para emparejarlo con el código, o seguir de largo, está prohibido** —
se reporta al usuario y decide él.

Dos límites impiden que esto reintroduzca el drift que "gana el código" venía a resolver:
un documento normativo **nunca** responde "¿qué hace el código hoy?" (para eso gana el
código, siempre), y la autoridad normativa de un trabajo en curso **caduca en el harvest**.

Se agrega un **Nivel 4 de verificación (Cumplimiento, opcional y periódico)**: auditar el
código contra lo normativo. Es auditoría con criterio, no script — por eso no va en CI.

# Consecuencias

- El kit ahora cubre las dos direcciones del drift: doc que envejece (niveles 1-3) y
  **código que se desvía de lo decidido** (nivel 4). Antes solo la primera.
- El template `_decision.md` invita a declarar **cómo verificar** la decisión (comando,
  grep, test). Una decisión chequeable es la que sobrevive; una vaga solo genera ruido.
- Costo: la regla dejó de ser una sola frase. Se mitiga con una fuente canónica (§3.5) y
  punteros desde el resto, más un assert del `okf_selfcheck` que exige que el contrato y
  `okf-update` sigan afirmando la rama normativa (es exactamente el tipo de regla que
  derivó históricamente en este kit).
- Riesgo asumido: un agente demasiado celoso podría reportar violaciones falsas de
  decisiones vagas. Por eso el Nivel 4 clasifica "ambigua" como hallazgo propio, cuyo fix
  es afilar el documento, no tocar el código.

# Verificación

Testeado adversarialmente (2026-07-26) con un **agente en frío** sobre un repo fixture con
tres trampas simultáneas, leyendo solo el contrato instalado. Resultado: **3/3**.
Clasificó el concepto `Architecture` desactualizado como bug del documento (y propuso
linkear el valor en vez de re-copiarlo); clasificó el código que violaba una decisión
`accepted` como bug del **código**, se negó a editar la decisión y llevó al usuario las dos
salidas legítimas; y **no** aplicó una decisión `superseded` contra el código —
el riesgo de sobre-aplicación no se materializó. El test también destapó que la sección de
la capa de futuro del `templates/AGENTS.md` deja links rotos si el repo no adoptó esa capa
(corregido con una instrucción de borrado en el template).
