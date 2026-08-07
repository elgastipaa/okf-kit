---
type: Decision
status: accepted
origen: dictado
verify: none
verify_note: "el dogfood del kit no tiene glosario — es un repo de tooling, no de dominio"
title: Glosario de dominio + code-of-record para abaratar preguntas a nivel término
description: El kit ofrece un template de glosario que rutea término→página canónica→archivo del valor, porque las preguntas de término eran las más caras en turnos.
tags: [okf, glossary, routing, efficiency, eval]
timestamp: 2026-06-18T00:00:00Z
---

# Contexto
Midiendo con `templates/eval/` (harness que corre `claude -p` en contexto fresco y registra
tokens/turnos/tiempo/acierto) sobre un repo real de juego, el bundle resultó **correcto pero
caro**: el agente siempre acertaba, pero las preguntas a nivel **término/stat** ("¿para qué
sirve ATK/DEF?", "¿qué es el Vigor?", "¿cuáles son las clases?") costaban 4–12 turnos porque
**no había un mapa término→página**: el agente faneaba al código a reconstruir un dato que ya
estaba documentado en prosa. Las preguntas que matcheaban un renglón del índice salían en 1–2
turnos. El cuello era **routing**, no falta de contenido.

# Decisión
El kit ofrece un **glosario de dominio** (`templates/knowledge/_glossary.md`) como concepto
opcional pero recomendado para repos con jerga/stats. Cada término mapea a tres cosas:
una **respuesta en una línea**, su **página canónica** (el *por qué*) y su **code-of-record**
(el archivo donde vive el *valor* exacto — p.ej. una tabla de tuning). El entrypoint
(`templates/AGENTS.md`) y el `index.md` **rutean** las preguntas de término hacia él antes de
grepear. Es **puntero, no fuente de verdad**: no se copia el valor, se linkea.

Enforcement **liviano**, coherente con [consumo permisivo](0002-permissive-consumption.md):
el kit lo propone (template + guía en `GUIDE.md`), no lo obliga ni lo exige el linter.

# Consecuencias
- Validado en the-conclave (spike, 2026-06-18): glosario + code-of-record bajó las preguntas
  de término **~−62% en turnos y −66% en latencia**, con la correctitud intacta (el agente
  saltó directo al archivo del valor en vez de grepear ~8). Evidencia kit-local en `eval/`.
- El propio kit **no necesita glosario**: sus términos (bundle, concepto, perfil, progressive
  disclosure) ya *son* sus conceptos en `concepts/` — un glosario sería duplicación.
- Es un mecanismo de **routing**, complementa pero no reemplaza `index.md`; suma una tercera
  columna (code-of-record) que extiende la idea de "el valor exacto vive en la fuente, linkealo".
