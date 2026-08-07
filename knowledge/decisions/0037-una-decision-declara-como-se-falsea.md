---
type: Decision
status: accepted
origen: dictado
verify: 'python3 scripts/okf_lint_test.py 2>&1 | grep -q "sin decir por qué"'
title: Una decisión normativa declara cómo se sabría que alguien la rompió
description: "El campo verify ata cada decisión al comando que la falsea, se exige solo cuando el bundle adopta la convención, y su runner no va al CI."
tags: [okf, decisiones, drift]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

Una decisión `accepted` es **normativa**: obliga al código. Pero nada verificaba si el código
**dejó de cumplirla**. Es el drift más caro porque es silencioso — la decisión sigue ahí, con
su sello, y el código hace otra cosa desde hace meses.

La evidencia de que se puede sostener no es teórica: un repo real lleva meses con esta
convención y tiene **54 de 54** decisiones declarándola, **50 con un comando real**, y sus
**35 targets de archivo siguen resolviendo**. Cuando no había un test que la cubriera, apareció
un script chico con el nombre de la decisión.

# Decisión

Una decisión declara **`verify: <comando>`** —lo que falla si alguien la rompe— o
**`verify: none` + `verify_note`**.

1. **El valor está en escribirla, no en correrla.** La pregunta *"¿cómo sabría que alguien la
   rompió?"* se contesta cuando alguien todavía se acuerda de qué la protege.
2. **Se adopta por uso, no por configuración.** Si alguna decisión del bundle lo declara, las
   demás `accepted` que no lo hagan son WARN; si ninguna lo declara, la regla calla. Así ningún
   bundle existente deja de ser válido y no hace falta un flag que nadie enciende. Lo que la
   regla ataca es la **adopción a medias**, que es el único estado peligroso: las decisiones
   sin chequeo parecen chequeadas porque sus vecinas lo están.
3. **`verify: none` sin `verify_note` es ERROR.** Admitir que no se puede chequear es legítimo;
   hacerlo sin decir por qué es el atajo — misma lógica que
   [0034](0034-el-porque-perdido-tiene-su-propio-casillero.md).
4. **El runner NO se cablea al CI.** Ejecuta comandos escritos en markdown: en un PR desde un
   fork eso es **ejecución de código arbitrario** en el runner del usuario. El linter sí va,
   porque no ejecuta nada. Que el runner lo agregue el usuario a conciencia.

# Consecuencias

- **No es ceremonia, y se midió en el caso difícil.** Adoptándola en el propio kit —prosa y
  tooling, no código de producto— **26 de 34** decisiones quedaron con un comando real (76%),
  contra 93% en el repo de producto. Los 8 `none` son el método de medición, el piso del
  instrumento y lo que el kit promete: cosas que ningún comando puede falsear, y **saber cuáles
  son es justamente el producto de la convención**.
- **Corre en la dirección contraria al resto del kit.** Un hallazgo no significa "el documento
  quedó viejo": significa que **el código está en violación**. Editar la decisión para que
  coincida con el código de hoy es el modo de falla que esto existe para cazar.
- **`verify:` NO compara la prosa con el código.** Ejecuta un comando y mira su exit code, así
  que la regla queda escrita **dos veces** —una en el documento, otra en el comando— y nada
  garantiza que digan lo mismo. Comparar prosa contra código es semántico: eso es el Nivel 3
  (`okf_coldtest.py`), y cuesta tokens. Lo que sí se puede detectar gratis es **la sospecha**:
  si el documento se editó después de fijar su `verify:`, el chequeo puede estar custodiando la
  regla vieja **y pasando igual**. Esa señal vive en `okf_stale.py` —que rankea, no
  gatea— y está medida: sobre 50 decisiones reales dispara en **2 (4%)**, y las dos eran
  legítimas (una quedó superseded en parte, la otra revirtió una cláusula el mismo día).
- **Empujó a que el kit se hiciera chequeable.** Varias decisiones sin assert propio ahora
  apuntan a uno; escribir el `verify` obligó a mirar si existía.
