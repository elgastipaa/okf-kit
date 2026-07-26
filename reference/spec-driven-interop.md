# OKF y el spec-driven development (OpenSpec, Spec Kit, Kiro…)

Existe una familia de herramientas de **spec-driven development (SDD)** —
[OpenSpec](https://github.com/Fission-AI/OpenSpec), GitHub Spec Kit, AWS Kiro— que
resuelven un problema **vecino pero distinto** al de OKF. Este documento explica la
diferencia y cómo conviven, para que no montes dos sistemas que se pisan.

> **El kit no depende de ninguna de ellas.** OKF sigue siendo markdown + git
> ([decisión 0004](../knowledge/decisions/0004-vendor-neutral-no-external-apps.md)). Esto
> es interop, no una dependencia.

---

## La diferencia en una línea

**OKF gestiona conocimiento; SDD gestiona cambios.** OKF responde *"¿qué es esto y por
qué es así?"*; SDD responde *"¿qué vamos a construir y ya estuvimos de acuerdo?"*.

| | **OKF (este kit)** | **SDD (OpenSpec y similares)** |
|---|---|---|
| Unidad | Concepto (`.md` + frontmatter) | Requirement + scenario, dentro de una *change* |
| Eje temporal | Pasado (`decisions/`) y presente (conceptos) — y futuro liviano (`roadmap.md` + `_changes/`) | Futuro: la próxima unidad de trabajo |
| Qué captura | El **por qué** que el código no dice | El **qué** observable, acordado *antes* de codear |
| Frente al código | **Depende del tipo**: los conceptos descriptivos pierden contra el código; los normativos (decisión aceptada, convención, rumbo, cambio activo) lo obligan | La spec archivada es el contrato de comportamiento; el código que no la cumple es el bug |
| Instalación | Ninguna (markdown + git) | CLI (`npm i -g`), comandos slash, estructura propia |

Esa fila de "frente al código" **era** la divergencia real, y resolverla mejoró el kit: no
es una contradicción sino **dos clases de documento** (`OKF-SPEC.md` §3.5, y la
[decisión 0012](../knowledge/decisions/0012-descriptive-vs-normative.md)). Un documento
**descriptivo** describe lo que ya existe → si difiere del código, el doc miente. Uno
**normativo** prescribe lo que debe cumplirse → si difiere, el **código está en violación**.
OpenSpec trabaja casi entero en el registro normativo; OKF usa los dos: sus conceptos son
descriptivos, pero las **decisiones aceptadas**, las convenciones, el rumbo y el "Resultado
esperado" de un cambio activo obligan al código igual que una spec de OpenSpec.

---

## Qué toma el kit de esa filosofía (ya incorporado)

De la comparación con OpenSpec se adoptaron cinco ideas, sin adoptar la herramienta:

1. **Acordar el resultado antes de codear.** El doc de `_changes/` define un "Resultado
   esperado" observable y verificable, escrito **con el usuario**, antes de tocar código.
   De ahí también el formato de escenarios (`CUANDO … ENTONCES …`), que hace que "hecho"
   sea chequeable en vez de opinable.
2. **No documentar de más: escribí lo que algo mantenga vivo.** OpenSpec desaconseja
   explícitamente back-fillear specs de código que no vas a tocar, *"porque nada las obliga
   a seguir la realidad"*. El equivalente en OKF: capturá el **por qué** (que no caduca) y
   **no transcribas** lo que se deduce del código (que sí) — ver `OKF-SPEC.md` §3.4.
3. **Fluido, no waterfall.** Los artefactos de un cambio son habilitadores, no compuertas:
   se editan a medida que se aprende implementando. `okf-plan` no exige llenar todo antes
   de empezar; exige el *por qué*, el resultado esperado y el fuera de alcance.
4. **Explorar antes de comprometer.** Primero se piensa el problema con el usuario (sin
   crear nada); recién cuando hay intención se abre el cambio.
5. **El código no puede contradecir lo decidido.** La idea central del SDD, aplicada a lo
   que OKF ya tenía: una decisión aceptada obliga: si el código la viola, se reporta y se
   elige entre arreglarlo o superseder la decisión — nunca se edita el documento en
   silencio. Se audita con el Nivel 4 de `verification.md`.

## Qué NO toma, y por qué

- **Deltas `ADDED`/`MODIFIED`/`REMOVED` sobre specs vivas.** Sirven para que dos cambios
  paralelos no colisionen en el mismo archivo: es un problema de equipo grande, no del
  usuario típico del kit. Agregaría ceremonia sin pagar.
- **Un archivo de cambios cerrados (`changes/archive/`).** En OKF el valor del cambio se
  **cosecha** al bundle (decisiones → `decisions/`, estado → conceptos) y el doc se borra;
  git guarda la historia. Conservar la carpeta crearía justo la capa de planes viejos que
  el entrypoint manda a ignorar ([decisión 0008](../knowledge/decisions/0008-declare-non-authoritative-layers.md)).
- **Specs vivas por capability como fuente de verdad del comportamiento.** El kit apuesta a
  que el comportamiento se lee del código y lo que hay que escribir es el *por qué*.

---

## Si ya usás OpenSpec (o querés usarlo) en el mismo repo

Conviven bien porque cubren cosas distintas; la regla es **no duplicar el ciclo de cambio**:

1. **Elegí un solo dueño del trabajo en curso.** Si usás OpenSpec, sus `changes/` reemplazan
   a `knowledge/_changes/` y a la sección "Ahora" del roadmap. **No mantengas los dos** —
   sería la deriva clásica de dos fuentes para lo mismo.
2. **El bundle `knowledge/` se queda con lo suyo:** el por qué (`decisions/`), la
   arquitectura, el dominio, los runbooks, el glosario. OpenSpec no cubre nada de eso.
3. **El archive de OpenSpec es tu disparador de harvest.** Cuando un cambio se archiva, esa
   es la señal para correr `okf-update`: las decisiones no triviales que aparecieron van a
   `knowledge/decisions/`, y los conceptos afectados se actualizan.
4. **Declará la relación en `AGENTS.md`**: dónde vive cada cosa, y que `openspec/` es la
   capa de trabajo futuro mientras `knowledge/` es la de conocimiento. Sin eso, un agente
   nuevo no sabe cuál leer.

Si **no** usás ninguna herramienta SDD, la capa nativa del kit (`roadmap.md` + `_changes/`
+ `okf-plan`) te da la parte que importa sin instalar nada.
