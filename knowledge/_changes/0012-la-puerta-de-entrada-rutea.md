---
type: Change
status: in-progress
title: La puerta de entrada del bundle pasa a rutear por necesidad, no a listar por tipo
description: "El index.md gana una tabla necesidad → 1-3 archivos → fuente de verdad arriba del listado, que es la única diferencia estructural que explica los tres brazos medidos."
tags: [okf, index, eval, economia-de-contexto]
timestamp: 2026-08-06T00:00:00Z
---

# El problema

Tres brazos medidos sobre `the-conclave` ([0011](0011-formato-contra-autor.md)) dejaron una
sola hipótesis viva:

| | qué es | qué provoca |
|---|---|---|
| `docs/wiki/index.md` (humano, **4.92 turnos**) | tabla de **ruteo por necesidad**: *"Si necesitás X → leé estos 1-3 archivos → fuente de verdad"* | el agente **salta** |
| `knowledge/index.md` (kit, **7.33 / 8.75**) | índice por **`type`**: Roadmap, Glossary, Runbook, Subdirectories | el agente **navega**: index → index de carpeta → concepto |

Explica los tres a la vez: navegar cuesta aproximadamente lo mismo que grepear, que es por qué
el bundle del kit quedó indistinguible de no tener capa. **El índice del kit está organizado
por la taxonomía del kit, no por las preguntas del que llega.**

Ya se descartaron dos causas más caras: no era la calidad de la prosa (K′) ni la falta de la
capa generada (K″, que compró acierto pero no velocidad).

# No hace falta superseder nada

`OKF-SPEC.md` §5 llama a los headings por `type` **"convención que usa la implementación de
referencia"**, no requisito. Lo duro es que los `index.md` no lleven frontmatter y que cada
entrada sea link relativo + `description`. Así que la tabla se **suma arriba** y el listado
queda intacto: el linter sigue verificando `concept-unlinked` / `index-desc-drift` /
`subdir-unlisted`, y **los bundles ya instalados siguen siendo válidos**.

# Diseño

1. **`okf_install.py`** siembra el bloque `# Por dónde empezar` arriba de todo, con las filas
   que el instalador **sabe** (los chequeos siempre; el rumbo si va la capa de futuro) y la
   consigna para que el agente agregue las del repo.
2. **`okf-init`** completa la tabla con **las preguntas que el repo recibe de verdad**, no con
   las categorías del kit. Una fila = una pregunta en las palabras del que pregunta.
3. La tabla apunta a **1-3 archivos**, no a una carpeta. Mandar a `decisions/` es volver a
   hacer navegar.

<!-- GATE ESCRITO ANTES DE MIRAR EL RESULTADO (0028). No editar después. -->

# Gate

Cuarta instalación ciega sobre el mismo commit de `the-conclave`, mismas 4 preguntas, n=3.
Se compara contra **K″ = 8.75 (sd 5.67), 11/12** y **W = 4.92 (sd 1.44), 11/12**.

**Cumplimiento, antes de medir**: si el `index.md` resultante no tiene la tabla con filas
propias del repo, el brazo no mide la función — mide que el agente se salteó el paso.

**Validación**: 12/12, 0 fallidas, 0 mutaciones.

**Lectura pre-registrada**:

1. **Era la puerta** — `K‴ < K″` por más de 2·EE **y** acierto ≥ 11/12. Se publica, y se
   revisa antes por qué no puede ser cierto.
2. **Ayuda pero no alcanza** — mejora sobre K″ mayor a 2·EE, todavía peor que W. Se publica la
   fracción recuperada sin redondear.
3. **Tampoco era** — `|K‴ − K″| < 2·EE`. Entonces se agotaron las hipótesis estructurales
   baratas, y la conclusión honesta es que **la brecha es de autoría** y el kit tiene que
   decirlo en su README: `okf-init` entrega un punto de partida correcto, no una capa que
   compita con una escrita por alguien que conoce el repo. En ese caso el cambio **se
   revierte** salvo que se sostenga solo (ver anti-autoengaño).

**Anti-autoengaño** (0028 §3): si bajan los turnos pero el acierto cae de 11/12, se rechaza.

**Presupuesto**: es la cuarta instalación ciega de esta línea. Si esta lectura da 3, **se para
de gastar** en este eje y se publica lo aprendido.

# Tareas

- [ ] Gate escrito antes de codear
- [ ] `okf_install.py` siembra la tabla
- [ ] `okf-init` la completa con las preguntas del repo
- [ ] Asserts + roturas probadas
- [ ] Instalación ciega + brazo K‴
- [ ] Leer contra el gate y publicar, salga lo que salga
