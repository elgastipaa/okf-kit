---
type: Roadmap
title: Rumbo del kit OKF
description: "Hacia dónde va el kit hoy: ingeniería de contexto completa (pasado, presente y futuro) aplicable a cualquier repo sin tooling."
tags: [roadmap]
timestamp: 2026-07-30T00:00:00Z
---

# Visión

Que aplicar `okf-kit` a un repo cualquiera —especialmente uno desarrollado
conversando con IAs— deje **ingeniería de contexto completa**: el pasado ordenado
(`decisions/`), el presente reconocible en segundos (bundle + entrypoint) y el
trabajo futuro gestionado (rumbo + cambios con spec y harvest), todo en markdown +
git, sin apps externas.

# Ahora (en curso)

- **La regresión de acierto sigue abierta.** La medición dio **4 fallos contra 0** de no tener
  capa. El primer intento de fix (la 0022: obligar a verificar en la fuente) **se midió y se
  revirtió** — +28% de turnos sin alcanzar el acierto que su propio gate exigía
  ([0023](decisions/0023-verificar-siempre-no-paga.md)). Lo único con evidencia a favor es la
  **cláusula de ambigüedad** (premisas falsas 1→0), que es barata y hay que probar sola.
  Aprendido por la vía dura: **agregar prosa al contrato no mueve el acierto**.
- **[El instrumento puede arbitrar mejoras del kit](_changes/0005-el-instrumento-antes-que-el-kit.md)**
  — el harness corre n=1 contra un ruido medido de 3,3 turnos/pregunta, con un juez que corre
  ciego y un brazo `nokit` que nunca se ejecutó. Hasta que mida, ninguna mejora del kit se
  puede aceptar ni descartar. Sale de las cuatro revisiones en frío sobre v0.7.3 (anexos en
  `_changes/`).

# Después (próximo, en orden)

**Lo que dejaron las cuatro lentes sobre v0.7.3, gateado por el instrumento.**

- **Los bugs del camino libre** (no necesitan medición, son bugs): `okf-migrate` es un
  callejón sin salida —el repo con `AGENTS.md`/`CLAUDE.md` propio es ruteado ahí y queda sin
  linter, hook, CI ni ruta de upgrade—; los disparadores de `okf-init`/`okf-migrate` exigen
  conocer el kit ("OKF" en las dos frases) en vez de nombrar el síntoma; el README promete
  `/okf-init` cuando el plugin expone `/okf:okf-init`; "todo se revierte con `git checkout`"
  es falso (lo que instala es untracked, y el hook va a `.git/hooks/`); y `okf_install.py:250`
  copia el `CLAUDE.md` crudo, con su comentario `<!-- TEMPLATE … -->` adentro.
- **Nada verifica que el código ande.** "Verificar", en el contrato instalado, es pasar el
  linter del bundle: hook, CI y los cuatro niveles apuntan todos ahí. Y la única línea que
  pide probar el código vive en la capa opcional, así que `--minimal` la borra — justo para
  el perfil que dice "andá directo al código". Propuesta de la lente C: sembrar siempre
  `knowledge/runbooks/checks.md` ("este repo no tiene chequeos" también es información) y una
  frase en el contrato. Converge con el paper de ETH: las *non-obvious test configurations*
  son de lo poco que mide como ganancia real.
- **La dieta del contrato.** El always-on real son 8.382 chars y el presupuesto mide 6.684
  (un archivo de tres: falta el `CLAUDE.md` y las descripciones de los skills). §2
  —mantenimiento— es el 24% y no paga nada en turnos de lectura. Tensiona con la
  [0013](decisions/0013-installed-material-is-self-sufficient.md): si se recorta, se supersede
  o se acota, no se edita en silencio.
- **Mecanismo 5: "el code-of-record cierra la búsqueda"** — **CONGELADO (2026-08-02)** por la
  [0023](decisions/0023-verificar-siempre-no-paga.md). Proponía licenciar que el agente
  **deje de buscar** cuando el code-of-record no tiene el término, o sea más permiso para
  contestar sin verificar: exactamente el modo de falla que la medición encontró. Se revisa
  cuando el acierto vuelva a 0/18. Su evidencia original sigue en pie y por eso no se tira:
  `trap` es la categoría más cara medida (6,4 turnos, n=19) y es el 31% de las preguntas; es
  la mitad que falta de la [0008](decisions/0008-declare-non-authoritative-layers.md), que dice
  dónde mirar pero no cuándo parar.
- **`log.md` es peso muerto**: 0 citas en 61 corridas contra 13 ediciones. El contrato ya lo
  trata como opcional pero el instalador lo pone siempre y el keep-alive lo exige. El log real
  es `git log` + `decisions/`.
- **`templates/eval/` no se instala nunca**, así que el diferencial no llega al usuario.

**Posicionamiento: el kit tiene que contestar al paper que lo cuestiona.**

- [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) (SRI Lab, ETH Zürich) mide que los
  context files **no mejoran el success rate y cuestan >20% más**; lo único positivo (+4%) es
  el contenido humano que el código no puede decir, y los *repository overviews* no ayudan.
  Es simultáneamente la validación de la tesis de OKF y la objeción que el kit va a recibir:
  hay que citarlo primero, y el README tiene que abrir por ahí en vez de por la abstracción.
- **Subir a OKF 0.2.** El upstream de Google Cloud ya estandarizó `status`, `stale_after`,
  `verified` y `generated` — los mismos campos que el kit reinventó por su cuenta. Adoptarlos
  convierte el ítem "estado WIP machine-readable" de trabajo propio en conformidad con la spec.
- **Conductor** (`gemini-cli-extensions/conductor`, 3.673★) es el competidor más cercano
  —markdown + git, sin CLI de npm, respaldo de Google, plugin portable a Claude Code— y
  `reference/spec-driven-interop.md` no lo menciona.

**Adopción: lo que falta para que el kit se pueda usar sin conocer al autor.**

- **Un repo de ejemplo clonable** (antes/después de un init real, con el diff visible). Hoy la
  única prueba navegable es el dogfood `knowledge/`, que está enterrado, y los mini-bundles de
  `reference/examples.md`. Es lo que convierte a un desconocido.
- Mueblería de adopción: badges, topics de GitHub, `CONTRIBUTING.md`, un asciinema de 30s del
  init. Barato y hoy no existe nada.
- Publicar la medición del harness de eval (turnos/tokens/acierto en los tres conejillos).
  **Es el diferencial que ningún competidor tiene** —verificado: ni Spec Kit (124k★), ni
  OpenSpec (63k★), ni Conductor, ni cc-sdd miden nada— y hoy `/eval/` está gitignoreado.
  Depende del cambio 0005: hasta que el instrumento no arbitre, no hay número publicable.

**De la comparación con `harness-sdd`** (el revisor con contexto fresco ya se cerró en la
[0021](decisions/0021-la-auditoria-no-se-auto-aprueba.md); los otros tres roles son no-goal):

- ~~**Estado de sesión en vivo**~~ — **descartado (lente D, 2026-07-30).** Es lo que los
  harnesses ya resuelven nativo y siguen mejorando (Claude Code tiene memoria automática,
  `MEMORY.md` y `/memory`; Anthropic publica ~84% de ahorro con memory tool + context
  editing). Construirlo en markdown sería competirle a la plataforma en su propio terreno,
  que es justo lo que el kit decidió no hacer. Lo que la plataforma **no** puede absorber
  —el porqué revisable en un PR, el registro normativo, el drift sin tokens— sigue siendo del kit.
- **Estado WIP machine-readable**: el roadmap es prosa, así que "≤1 cosa en curso" no lo puede
  enforcear ni el linter ni el hook. **Ya no es trabajo propio**: OKF 0.2 upstream trae
  `status` y `stale_after` estándar — subir de versión y usarlos.

**Cerrar lo que quedó escrito y sin medir.**

- Los dos escenarios que la [0015](decisions/0015-rankear-el-drift-antes-de-auditarlo.md) dejó
  sin verificar con un agente: que la auditoría reporte un ítem de "Ahora" ya terminado, y que
  el hallazgo llegue al usuario clasificado sin resolverse solo.
- Si el doc de `_changes/` se saltea sistemáticamente cuando el agente cree que termina en una
  corrida, y si el umbral debería ser "¿podría no terminar en esta sesión?" en vez de "¿es no
  trivial?" ([0014](decisions/0014-future-layer-measured.md)).

**Deudas del tooling.**

- El juez `--grade` del harness de medición no sirve para preguntas de comportamiento: puntuó
  bien una respuesta con premisa falsa. (La métrica de contexto ya se arregló en 0.7.1.)
  **En curso** — es parte del cambio
  [0005](_changes/0005-el-instrumento-antes-que-el-kit.md), junto con la causa mayor que
  nadie había visto: el juez corre sin `cwd=repo`, o sea que no puede verificar nada.
- El pre-commit hook del kit valida el working tree en vez de lo staged, al revés que el que
  el kit shippea a otros repos. CI ataja el escape, por eso no es urgente.
- Higiene de `_changes/` (cambios zombie) en el linter — **solo si** la medición muestra que
  pasa seguido.

# No-goals (por ahora)

- **Los otros tres roles de `harness-sdd`** (leader / spec_author / implementer): ceremonia de
  equipo grande, sin evidencia de que paguen para un usuario solo. El único que pagaba era el
  revisor, y ya está ([0021](decisions/0021-la-auditoria-no-se-auto-aprueba.md)).
- **Un harvester con contexto fresco:** el harvest necesita recordar qué pasó, y eso lo tiene la
  sesión que hizo el trabajo. Contexto fresco sirve para auditar, no para recordar.

- Reimplementar spec-driven development completo (specs vivas por capability,
  estilo OpenSpec): el kit cubre el ciclo cambio→harvest; para más que eso, se
  documenta interop, no se compite.
- Tooling nuevo obligatorio para la capa de futuro: sigue siendo markdown + git
  (la [decisión 0004](decisions/0004-vendor-neutral-no-external-apps.md) manda).
