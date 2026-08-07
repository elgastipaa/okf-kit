---
type: Decision
status: accepted
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*atado a declarar el hueco"
origen: dictado
title: Una decisión puede ser normativa sin porqué recuperable, y eso se declara
description: "origen: confirmado cubre el caso real de una decisión que alguien tomó y cuyo razonamiento se perdió; obliga a declarar el hueco en vez de redactarlo."
tags: [okf, decisiones, confabulacion]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

El vocabulario de la [0027](0027-una-razon-reconstruida-no-manda.md) tenía dos valores:
`dictado` (te lo contó una persona) y `reconstruido` (lo dedujiste del código). Midiendo
elicitación sobre un repo real apareció un tercer estado que no entra en ninguno, y lo mostró
el dueño **sin proponérselo**: en la misma sesión **confirmó que había decidido** dos reglas y
**no supo decir por qué**.

Con dos valores hay que mentir en algún sentido:

- `dictado` afirma un porqué que **nadie tiene** — es la falla que la 0027 existe para evitar.
- `reconstruido` degrada a `proposed` una decisión que **sí se tomó**, y le saca autoridad al
  código que la implementa.

Y no es un caso de borde: es el estado **normal** de un repo trabajado con IAs durante meses.

# Decisión

Se agrega **`origen: confirmado`**: alguien confirma que la decisión se tomó, pero el porqué no
se recuperó.

1. **Puede ser normativa** (`accepted`). Lo que falta es la razón, no la decisión.
2. **Obliga a declarar el hueco**: sin un `> Pendiente de confirmar: …` en el archivo, es
   **ERROR** del linter (`origen-confirmado-sin-pregunta`).
3. Ese error no es burocracia: `confirmado` es **exactamente el casillero que un agente usaría
   para escapar** del ERROR de `reconstruido` mientras redacta un Contexto que suene bien. Sin
   la obligación, el tercer valor sería un agujero más grande que el problema que resuelve.

# Consecuencias

- **El porqué perdido queda como deuda visible.** Esas decisiones entran solas en
  `okf_lint.py --questions`, así que el hueco viaja con el bundle y se le puede preguntar a
  alguien que quizás sí se acuerde.
- **Se puede decir "no sé" sin perder la regla.** Antes, admitir que no recordabas el porqué
  costaba degradar la decisión; ahora no.
- **Es aditivo**: ningún bundle existente deja de ser válido, y la clave ausente sigue
  significando `dictado`.
