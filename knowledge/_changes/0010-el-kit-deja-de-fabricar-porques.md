---
type: Change
title: El kit deja de fabricar porqués que nadie tomó
description: "OKF no tiene forma de escribir \"no se sabe\", así que un agente al que le pedís el porqué lo inventa y queda como decisión normativa."
status: active
timestamp: 2026-08-04T00:00:00Z
---

# Por qué

Se midió el eje "por qué" con ground truth dictado por el dueño del repo. De seis preguntas,
**tres no las sabe nadie** (las decidió una IA sin dejar registro). Resultado: **los dos
brazos —con kit y sin capa— inventaron una explicación en 9 de 9 corridas.**

Pero al revisar *dónde* nacía la invención apareció algo peor, y es lo que motiva este cambio:

**La invención no ocurre al responder. Ocurre al escribir el bundle.**

El agente que aplicó el kit a idlerpg —a ciegas, leyendo el código— escribió:

- En `runbooks/dev-build.md`, sobre los scripts que llaman a `node vite.js`:
  *"**No es cosmético**: el repo se trabaja en entornos donde npm no deja el bit de ejecución…"*.
  El dueño: *"No sé por qué esto, lo hizo alguna IA codeando"*.
- Una **decisión entera** (`decisions/0004-save-sin-version-merge-tolerante.md`) con
  `status: accepted` —o sea **normativa** según nuestro propio contrato— y un "Contexto" que
  argumenta muy bien por qué se eligió el duck-check. El dueño: *"No lo sé"*.

Eso es peor que confabular al responder, por tres razones: es **consistente** (siempre la
misma reconstrucción), es **citable** (viene con `resource:` y todo), y el contrato la trata
como **normativa** — si mañana alguien cambia el save, el kit le va a decir que el código está
en violación de una decisión que **nadie tomó**.

**La causa raíz:** OKF no tiene forma de escribir *"no se sabe"*. El template de decisión pide
un Contexto; un agente al que le pedís el porqué tiene dos salidas —inventarlo u omitir el
concepto— y elige inventar. La instrucción *"preguntá lo que no puedas deducir"* existe en
`okf-init`, pero **es inaplicable cuando no hay usuario en sesión y no deja ningún rastro de
que se salteó**. El propio agente lo dijo del nivel de instalación (*"fue un default, no una
decisión informada"*) y con las otras seis reconstruyó en silencio.

# Resultado esperado (la spec)

- **CUANDO** un agente documenta algo cuyo porqué no puede deducir de la fuente ni preguntarle
  a nadie → **ENTONCES** lo escribe como **pregunta abierta**, no como razón. "No se sabe" es
  contenido válido, igual que `checks.md` acepta "este repo no tiene chequeos".
- **CUANDO** una decisión se **reconstruyó** del código en vez de dictarla una persona
  → **ENTONCES** lo declara (`origen: reconstruido`) y **no puede ser `status: accepted`**:
  una reconstrucción no manda sobre el código hasta que un humano la confirme.
- **CUANDO** el linter ve `origen: reconstruido` junto a `status: accepted` → **ENTONCES** es
  **ERROR**, no warning: es exactamente el estado que produjo esta fabricación.
- **CUANDO** termina un init o una migración → **ENTONCES** el agente le muestra al usuario
  **la lista de preguntas abiertas** que dejó, en vez de resolverlas en silencio.
- **CUANDO** se corre `okf_lint.py --questions` → **ENTONCES** salen todas las preguntas
  abiertas del bundle, para que se puedan revisar sin leerlo entero.
- **CUANDO** se re-mide el golden-set de "por qué" con estos cambios → **ENTONCES** las
  explicaciones inventadas **bajan**. Si no bajan, el cambio no sirvió y se revierte.

# Fuera de alcance

- **Agregar prosa al contrato instalado pidiendo "no inventes".** Está medido que no mueve el
  acierto ([0023](../decisions/0023-verificar-siempre-no-paga.md)) y además estaría en el lugar
  equivocado: el problema está en el camino de **escritura**, no en el de lectura.
- Arreglar la confabulación del modelo en general. No es nuestro problema y no lo podemos
  tocar; lo que sí podemos es dejar de **institucionalizarla**.
- Los ítems bloqueados de la cola [0009](0009-plan-de-ejecucion.md), que queda **aparcada**
  mientras dure este cambio.

# Plan / Tareas

- [x] **`origen:` en las decisiones** — vocabulario cerrado `dictado | reconstruido`, en el
      template `_decision.md` y en `OKF-SPEC.md`. Ausente = se asume dictado (no rompe bundles
      viejos).
- [x] **Regla del linter `origen-reconstruido-normativo`**: `origen: reconstruido` +
      `status: accepted` = **ERROR**, con su rotura probada y su caso legítimo
      (`reconstruido` + `proposed` pasa limpio).
- [x] **"No se sabe" como contenido válido** en `_decision.md` y `_concept.md`: instrucción
      explícita de escribir la pregunta abierta en vez de reconstruir una razón.
- [x] **`okf_lint.py --questions`**: lista los `> Pendiente de confirmar:` del bundle. Reusa
      la convención que ya existe en el template de roadmap en vez de inventar un artefacto.
- [x] **`okf-init` y `okf-migrate` terminan mostrando las preguntas abiertas** al usuario, con
      su assert en el gate.
- [x] **Decisión** que registre todo esto y su evidencia.
- [ ] **Arreglar el bundle de idlerpg**: las dos reconstrucciones pasan a preguntas abiertas.
      Es la demostración del cambio sobre el caso que lo originó.
- [ ] 💰 **Re-medir** el golden-set de "por qué" (~US$25, dos brazos) y comparar contra la
      línea de base: **con kit 11/18 inventadas, sin capa 14/18**. Necesita autorización.

# Decisiones y descubrimientos en el camino

- **La convención ya funcionaba donde el template la ofrecía.** `--questions` sobre idlerpg
  sacó **3 preguntas abiertas, todas en `roadmap.md`** — y una es exactamente la del
  onboarding (*"si se apagó a propósito y por cuánto tiempo"*). El roadmap era **el único
  template que las pedía**. El mismo agente, en el mismo repo, dejó preguntas donde se las
  pedían y fabricó donde le pedían un "Contexto". No es un problema de criterio del agente:
  es de qué le pide el template.

- La medición del brazo `kit` (11/18 inventadas) hay que **releerla** a la luz de esto: en q4 y
  q6 el agente probablemente no inventó al responder, sino que **leyó fielmente una invención
  del bundle**. El número no cambia, su interpretación sí.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" **con la medición**, no asumido
- [ ] Decisiones/descubrimientos → `knowledge/decisions/` (+ índice)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día; la cola [0009](0009-plan-de-ejecucion.md) se desaparca
- [ ] Borrar este archivo (git conserva la historia)
