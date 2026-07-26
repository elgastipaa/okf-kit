<!--
  TEMPLATE de decisión (ADR). Va en decisions/ con nombre numerado:
  decisions/NNNN-<slug>.md (ej: 0003-use-message-queue.md). Una decisión por archivo.
  Esto es lo MÁS valioso del bundle: el por qué que el código no cuenta. Borrá este
  comentario.
-->
---
type: Decision
title: {{La decisión, en una frase afirmativa. Ej: "Usamos cola para emails"}}
description: {{Una frase que resume qué se decidió y el efecto principal.}}
status: accepted                  # proposed | accepted | "superseded by NNNN"
supersedes: {{NNNN-slug-al-que-reemplaza — borrá esta línea si no aplica}}
resource: {{URL al PR/commit/archivo que la implementa — opcional}}
tags: [{{subsistema}}, {{tema}}]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Contexto
{{Qué problema o situación motivó la decisión. Qué alternativas había.}}

# Decisión
{{Qué se decidió, concretamente. Linkeá al runbook/schema/concepto relacionado.}}

# Consecuencias
{{Qué implica esto — lo bueno y lo malo. Qué NO hacer por culpa de esta decisión.
Esto es lo que evita que alguien la rompa sin querer.}}

<!-- Una decisión con `status: accepted` es NORMATIVA: obliga al código. Si encontrás
     código que la viola, el bug es el código — no edites esta decisión para que
     "coincida" con lo que el código hace hoy. Avisale al usuario y ofrecé: arreglar el
     código, o superseder esta decisión explícitamente (ver abajo). -->

<!-- Cómo verificar que se cumple (opcional pero muy útil): {{el comando, test o
     grep que delata una violación — ej. "no debe haber imports de `nodemailer`
     fuera de `src/email/queue.ts`"}}. Una decisión chequeable es una decisión que
     sobrevive. -->


<!-- Deprecar/reemplazar: esta decisión NO se edita para "darla de baja". Creá una
     decisión NUEVA con `status: accepted` y `supersedes: NNNN`, y poné en ESTA
     `status: "superseded by MMMM"`. Si deprecás un concepto, **nombralo explícito**
     acá para que un `grep` futuro lo encuentre. -->

