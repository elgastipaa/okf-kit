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
origen: reconstruido              # dictado | reconstruido — ver abajo, importa mucho
supersedes: {{NNNN-slug-al-que-reemplaza — borrá esta línea si no aplica}}
resource: {{URL al PR/commit/archivo que la implementa — opcional}}
tags: [{{subsistema}}, {{tema}}]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Contexto
{{Qué problema o situación motivó la decisión. Qué alternativas había.}}

<!-- ¿DE DÓNDE SALE ESTE "POR QUÉ"?  Es la pregunta que decide si esta decisión vale.

     El template viene con `origen: reconstruido` A PROPÓSITO, y eso hace que copiarlo tal
     cual **rompa el linter**. No es un descuido: `dictado` es la única de las dos que nadie
     puede verificar después, así que no puede ser lo que te sale gratis por no pensar.
     Para que quede `dictado` tenés que escribirlo vos, sabiendo qué estás afirmando.

     `origen: dictado`       — te lo contó una persona. Puede ser normativa (`accepted`).
     `origen: reconstruido`  — lo dedujiste vos leyendo el código. **NO puede ser
                               `accepted`**: el linter lo rechaza. Va `proposed` hasta que
                               alguien que sabe la confirme.
     `origen: confirmado`    — alguien confirma que la decisión **se tomó**, pero **el porqué
                               no se recuperó**. Puede ser `accepted`: lo que falta es la
                               razón, no la decisión. **Obliga a dejar la pregunta abierta**
                               (`> Pendiente de confirmar: …`) y el linter lo exige — si no,
                               este valor sería el atajo para redactar un Contexto convincente
                               esquivando el ERROR de `reconstruido`.

     El tercero existe porque el estado es real y frecuente: midiendo un repo vibecodeado, su
     dueño **confirmó que había decidido** dos reglas y en la misma sesión **no supo decir por
     qué**. Con dos valores había que mentir en algún sentido.

     **Y SI NADIE SABE POR QUÉ, NO ESCRIBAS UNA DECISIÓN.** Esa es la trampa: el código
     muestra QUÉ se hizo, y es facilísimo redactar un Contexto convincente sobre por qué
     "se eligió" — cuando en realidad no lo eligió nadie, salió así. Eso queda como
     normativo y después el kit le dice a alguien que su código viola una decisión que
     nunca existió. Pasó de verdad y por eso está escrito acá.

     En su lugar, dejá la pregunta abierta donde corresponda:
         > Pendiente de confirmar: por qué {{X}} es así. No hay razón registrada.
     Y contásela al usuario cuando termines. Una pregunta abierta es información;
     un porqué inventado es daño. -->

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

