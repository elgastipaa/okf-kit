<!--
  TEMPLATE de cambio (la spec liviana de un trabajo por hacer). Va en
  knowledge/_changes/ con nombre numerado: _changes/NNNN-<slug>.md — el `_` va en
  la CARPETA; el archivo no lo lleva. NO es un concepto del bundle (el linter
  ignora _changes/): es un documento de TRABAJO, efímero — acá SÍ van checkboxes.
  Nace ANTES de codear un cambio no trivial, guía la implementación (aunque cruce
  sesiones o IAs distintas) y, al terminar, se HARVESTEA al bundle y se BORRA (git
  guarda la historia). El ciclo completo: skill okf-plan. Borrá este comentario.
-->
---
type: Change
title: {{El cambio, como resultado. Ej: "Los usuarios pueden guardar la partida"}}
description: "{{Una frase: qué va a ser distinto cuando esté hecho.}}"
status: active                    # active | done (done = falta solo el harvest)
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Por qué

{{1-3 frases: qué problema resuelve o qué habilita. Linkeá el rumbo si aplica
([roadmap](../roadmap.md)). Si esto no se puede escribir, el cambio quizá no vale
la pena.}}

# Resultado esperado (la spec)

{{Qué va a ser observable y verificable cuando esté terminado — escrito ANTES de
codear y acordado con el usuario. Esto define "hecho": si no se puede verificar, no
está hecho. Escribilo como escenarios concretos, incluyendo el que falla (ahí viven
los bugs). Ej:}}

- **CUANDO** {{un usuario logueado toca "Guardar"}} → **ENTONCES** {{se guarda la partida y aparece la confirmación}}
- **CUANDO** {{recarga el navegador}} → **ENTONCES** {{la partida sigue donde estaba}}
- **CUANDO** {{no hay espacio para guardar}} → **ENTONCES** {{se avisa el error y no se pierde la partida en curso}}

{{Mientras este cambio esté activo, esto MANDA sobre "¿está terminado?": si el código
no lo cumple, el trabajo no está hecho. Bajar la vara se renegocia con el usuario
editando esta sección — nunca en silencio. (Para "¿qué existe hoy?" gana el código.)}}

# Fuera de alcance

{{Qué NO entra en este cambio aunque sea tentador. La red contra el scope creep:
lo bueno-pero-no-esencial que aparezca en el camino va a "Después" del
[roadmap](../roadmap.md), no al código.}}

# Plan / Tareas

{{Pasos concretos, tildados a medida que avanzan (acá SÍ van checkboxes — este
archivo es la memoria del trabajo entre sesiones):}}
- [ ] {{...}}
- [ ] {{...}}

# Decisiones y descubrimientos en el camino

{{Staging area: cada decisión no trivial, gotcha o cosa aprendida mientras se
trabaja, en una línea con su por qué. En el harvest se convierten en `decisions/`
y `references/` del bundle — anotalas acá en el momento para no perderlas.}}

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" de arriba corriendo los chequeos de
      `knowledge/checks.md` — **pegá el comando y su salida**, no alcanza con "probado"
- [ ] Decisiones/descubrimientos de arriba → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados (arquitectura / schema / runbooks…)
- [ ] Si el harvest creó una **carpeta** nueva, sumala al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md` (si el repo lo mantiene)
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado
- [ ] Borrar este archivo (git conserva la historia). **Ningún doc permanente puede quedar
      linkeando a `_changes/`** — si una decisión o un concepto linkeó a este cambio, cortá
      ese link primero (el único que linkea acá es el roadmap, que se edita en este mismo paso).
