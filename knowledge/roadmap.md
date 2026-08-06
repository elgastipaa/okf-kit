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

- **El −34% no era del kit: era del autor (2026-08-06).** Ese número se midió con la capa que
  escribió **a mano el dueño del repo**. Instalando el kit **a ciegas** sobre el mismo repo y
  las mismas preguntas, el bundle quedó **indistinguible de no tener capa** en recuperación de
  hechos. Se probaron las dos hipótesis caras —capa generada y puerta que rutea— y ninguna
  separó por encima del ruido del instrumento. La promesa se corrigió en la
  [0033](decisions/0033-el-kit-preserva-porques-no-acelera-hechos.md): el kit **preserva
  porqués y produce preguntas**; no acelera la recuperación de hechos por sí solo.

- **El eje de medición "prosa contra prosa" está cerrado, y por qué**
  ([0032](decisions/0032-el-instrumento-tiene-un-piso-de-resolucion.md)). Con el n que se puede
  pagar, el instrumento no resuelve efectos menores a ~20-40%. Lo que sigue midiéndose es la
  **elicitación**, que es barata y no depende de este instrumento.


# Después (próximo, en orden)

**La cola de ejecución (0009) se cerró (2026-08-06).** Lo que sobrevive ya vive abajo, en
"Adopción". **Dados de baja por la
[0032](decisions/0032-el-instrumento-tiene-un-piso-de-resolucion.md):** `fuente primaria` como
palabra líder, la restricción de tipo sobre el artefacto y la dieta del contrato con la navaja
no-op. Los tres eran cambios de prosa del contrato que **solo se podían justificar
midiéndolos**, en el eje que el instrumento no resuelve. No están descartados por malos: están
**fuera del alcance de lo que se puede saber** con lo que cuesta medir. Si algún día hay un
instrumento más fino, vuelven.

**La hipótesis que puede redefinir el kit: elicitación, no documentación.**

El diferencial no es guardar contexto —eso está medido que no paga en recuperación de hechos,
y los harnesses lo están absorbiendo con memoria nativa—. Lo que apareció midiendo el eje
"por qué" es otra cosa: **el kit puede producir las preguntas que solo una persona puede
contestar**, y eso ninguna plataforma lo da porque requiere no tener la respuesta.

La evidencia de que es diseñable: el mismo agente, en el mismo repo, **preguntó donde el
template pedía `> Pendiente de confirmar:` y fabricó donde pedía un "Contexto"**. El artefacto
determina la conducta.

**Cómo se mide** (barato, y no lo hicimos nunca): aplicar el kit a un repo **con el dueño
disponible**, y contar **cuántas preguntas produce y cuántas contesta**. Si de diez preguntas
seis merecen respuesta, eso es conocimiento que no existía en ningún lado — el único tipo de
valor que no se puede obtener de otra forma.

Si da bien, el pitch pasa de *"guardá el contexto de tu repo"* a **"descubrí lo que tu
proyecto no sabe de sí mismo"**.


**Lo que dejaron las cuatro lentes sobre v0.7.3, gateado por el instrumento.**

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
- Publicar la medición del harness de eval. Ni Spec Kit (124k★), ni OpenSpec (63k★), ni
  Conductor, ni cc-sdd miden nada — pero **"nadie mide" es falso y hay que dejar de decirlo**:
  [CCPM](https://github.com/automazeio/ccpm) (8,3k★) publica un badge `eval_score 100%` y una
  tabla de 100% contra 27,7% de baseline. El terreno narrativo ya está ocupado por un número
  peor que el nuestro. Lo defendible no es "somos los únicos que medimos" sino **cómo**:
  n≥3 con dispersión reportada, brazo sin capa que aparta los archivos de verdad, juez que
  verifica contra el código, veredicto de premisa falsa, y **publicar también cuando da
  negativo** — que es lo que acabamos de hacer. Hoy `/eval/` está gitignoreado.

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

- ~~El juez `--grade` no sirve para preguntas de comportamiento~~ — **hecho.** La causa mayor
  era que corría **sin `cwd=repo`**, o sea que no podía abrir un archivo del repo que juzgaba.
  Además ganó el veredicto de premisa falsa y el de explicación inventada. Método en la
  [0028](decisions/0028-la-medicion-manda-y-el-gate-se-escribe-antes.md).
- El pre-commit hook del kit valida el working tree en vez de lo staged, al revés que el que
  el kit shippea a otros repos. CI ataja el escape, por eso no es urgente.
- Higiene de `_changes/` (cambios zombie) en el linter — **solo si** la medición muestra que
  pasa seguido.

# No-goals (por ahora)

- **Publicar en repos ajenos.** Nada de PRs a listas curadas (`awesome-vibe-coding` y
  similares) ni de promoción en repos de terceros: se trabaja en este repo y punto
  (decisión del usuario, 2026-08-04). Si algún día el kit se difunde, será porque alguien lo
  encontró útil, no porque lo empujamos.

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
