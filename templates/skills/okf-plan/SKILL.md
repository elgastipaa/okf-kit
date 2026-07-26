---
name: okf-plan
description: >
  Gestiona la capa de FUTURO del contexto OKF: el rumbo (knowledge/roadmap.md) y
  los cambios en curso (knowledge/_changes/). Usalo al empezar una sesión (para retomar
  el trabajo abierto), cuando el usuario pide un cambio/feature no trivial ("agreguemos
  X", "quiero que haga Y"), cuando pregunta "¿qué sigue?" o "¿en qué estábamos?", cuando
  un cambio se termina (harvest), o cuando aparece una idea buena que NO es la tarea
  actual.
---

El bundle OKF de este repo no solo documenta el pasado (`decisions/`) y el presente
(los conceptos): también lleva el **futuro**, en dos piezas con roles distintos:

- **`knowledge/roadmap.md`** — el **rumbo vigente**: visión, qué está en curso, qué
  sigue, y los no-goals. ES un concepto normal del bundle (estado presente *de la
  intención*); se edita, no acumula historial, y **no lleva checkboxes**.
- **`knowledge/_changes/NNNN-<slug>.md`** — un doc **efímero por cada cambio no
  trivial**: la mini-spec (por qué, resultado esperado, fuera de alcance), las
  tareas con checkboxes, y las decisiones que van apareciendo. NO son conceptos
  (el linter ignora `_changes/`); nacen antes de codear y **mueren en un harvest**.

Esto es una forma liviana de *spec-driven development*: cada cambio se especifica
antes de codearse y se cosecha al bundle al cerrarse. El objetivo es que el
proyecto **no pierda el rumbo** aunque el trabajo cruce sesiones, ventanas de
contexto o IAs distintas.

Es un **procedimiento vendor-neutral**: corre como skill de Claude Code *o* lo sigue
cualquier agente leyendo estas instrucciones. **Es autosuficiente**: todo lo que hace falta
para ejecutarlo está acá — no depende de que `okf-kit` siga en disco.

# Cuándo disparar (cinco momentos)

**Ninguno requiere que el usuario nombre este procedimiento.** El público de este sistema no
sabe qué es "okf-plan" ni tiene por qué saberlo: vos reconocés el momento y actuás.

0. **Primer mensaje de una sesión** → mirá `roadmap.md` y `_changes/`. Si hay un cambio
   activo, decilo en **una línea** antes de arrancar ("venías con X, quedó en la tarea Y —
   ¿seguimos?"). Es lo que evita que cada sesión empiece de cero. Si no hay nada activo, no
   digas nada: seguí con lo que te pidieron.
1. **El usuario pide un cambio no trivial** ("agreguemos X", "quiero que Y") →
   **abrí un cambio** (abajo) ANTES de codear. Umbral: un typo, un fix chico o un
   ajuste puntual no necesitan doc; si el trabajo tiene más de un paso, toca varios
   archivos o va a cruzar una sesión, sí.
2. **El usuario pregunta "¿qué sigue?" / "¿en qué estábamos?" / "retomemos"** →
   leé `roadmap.md` + los docs de `_changes/` y respondé desde ahí: qué está
   activo, en qué tarea quedó, qué viene después. Es la respuesta en segundos que
   esta capa existe para dar.
3. **Un cambio se terminó** (su "Resultado esperado" se verifica) → **harvest**
   (abajo). Nunca lo saltees: un cambio done sin harvest es contexto perdiéndose.
4. **Aparece una idea buena que NO es la tarea actual** → una línea en "Después"
   del `roadmap.md` (título + por qué). NO la implementes "de paso": eso es el
   scope creep que esta capa frena.

# Explorar antes de comprometer

Cuando el pedido es vago ("estaría bueno que haga X", "no sé si conviene A o B"), **no abras
un cambio todavía**: primero pensá el problema con el usuario — leé el código y el bundle,
proponé enfoques, mostrá qué implica cada uno. Explorar no crea archivos. Recién cuando hay
una intención concreta y acordada, se abre el cambio. Abrir un doc por cada idea suelta
llena `_changes/` de ceremonia muerta; las ideas sin compromiso van a "Después" del roadmap.

# Abrir un cambio

0. **Dimensionalo primero.** Un cambio sano tiene **una intención que se dice en una frase**
   ("agregar guardado de partida", "limitar los intentos de login"). Señales de que es
   demasiado grande y hay que partirlo: el alcance parece una lista de features sin relación;
   la mitad de las tareas podrían entregarse solas; revisarlo llevaría una tarde. Partir es
   barato; un cambio gigante que nunca cierra es el que se abandona.
1. **Si no existe `knowledge/roadmap.md`, creálo primero**, preguntándole al usuario la
   visión y los no-goals — no los inventes. Es un concepto normal del bundle (va linkeado
   en `knowledge/index.md`, bajo `# Roadmap`), con este esqueleto:
   ```markdown
   ---
   type: Roadmap
   title: Rumbo de <proyecto>
   description: <una frase: hacia dónde va el proyecto hoy>
   tags: [roadmap]
   timestamp: <ISO 8601>
   ---

   # Visión
   <2-4 frases: qué querés que sea cuando esté bien. No features: el resultado.>

   # Ahora (en curso)
   - [<título del cambio>](_changes/NNNN-<slug>.md) — <una línea de por qué>

   # Después (próximo, en orden)
   - <una línea por ítem; sin fechas y sin checkboxes>

   # No-goals (por ahora)
   - <lo que decidiste NO hacer, con el por qué en media línea>
   ```
2. Numerá secuencial dentro de `_changes/` y creá `knowledge/_changes/NNNN-<slug>.md` (el
   `_` va en la carpeta, el archivo no lo lleva). Esqueleto — las secciones son el
   procedimiento, no las recortes:
   ```markdown
   ---
   type: Change
   title: <el cambio como RESULTADO: "Los usuarios pueden guardar la partida">
   description: <una frase: qué va a ser distinto cuando esté hecho>
   status: active
   timestamp: <ISO 8601>
   ---

   # Por qué
   <1-3 frases: qué problema resuelve. Si no se puede escribir, quizá no vale la pena.>

   # Resultado esperado (la spec)
   - **CUANDO** <situación> → **ENTONCES** <lo observable>
   - **CUANDO** <el caso que falla> → **ENTONCES** <qué pasa en vez de romperse>

   # Fuera de alcance
   <lo tentador que NO entra; va a "Después" del roadmap>

   # Plan / Tareas
   - [ ] <paso concreto>

   # Decisiones y descubrimientos en el camino
   <staging: cada decisión/gotcha en una línea, en el momento>

   # Harvest (al cerrar — NO borres este archivo sin completarlo)
   - [ ] Verificado el "Resultado esperado" (probado de verdad, no asumido)
   - [ ] Decisiones/descubrimientos → `knowledge/decisions/` y `references/` (+ sus index)
   - [ ] Conceptos del bundle afectados actualizados
   - [ ] Carpeta nueva creada en el harvest → sumada al `# Subdirectories` del index raíz
   - [ ] Entrada en `log.md` (si el repo lo mantiene)
   - [ ] Roadmap al día: esto sale de "Ahora"; "Después" repriorizado
   - [ ] Ningún doc permanente quedó linkeando a este archivo (cortá ese link primero)
   - [ ] Borrar este archivo (git conserva la historia)
   ```
3. **Completá la mini-spec CON el usuario**: el *Resultado esperado* (observable y
   verificable — define "hecho") y el *Fuera de alcance* se acuerdan, no se asumen.
   El *Plan/Tareas* sí es tuyo: proponelo. Escribí el resultado como **escenarios**
   (`CUANDO … ENTONCES …`) y cubrí también el caso que falla (input vacío, sin permisos,
   doble click): ahí es donde viven los bugs, y es lo que después hace que "está hecho"
   sea chequeable en vez de opinable.
4. Linkeá el cambio desde "Ahora" del `roadmap.md`. Si "Ahora" ya tiene 3 cambios
   activos, **no abras otro**: proponé al usuario terminar o repriorizar uno antes.

# Mientras se trabaja

- Mantené las **tareas tildadas al día** — este doc es la memoria del trabajo entre
  sesiones; un agente que retoma en frío debe poder seguir desde la última tilde.
- Cada **decisión no trivial o gotcha** que aparezca: una línea en "Decisiones y
  descubrimientos en el camino", en el momento (después no te vas a acordar).
- **Nada que salga de "Fuera de alcance" entra al código.** Va a "Después" del
  roadmap y se sigue con lo especificado.

# Cerrar un cambio: el harvest

Cuando el "Resultado esperado" se cumple y verifica, seguí la sección
**`# Harvest`** del propio doc de cambio — su checklist es el procedimiento:
verificar el resultado de verdad, convertir las decisiones/descubrimientos
anotados en conceptos del bundle (la mecánica exacta de escribirlos —carpeta,
frontmatter, index, log— es la de **`okf-update`**), actualizar los conceptos
afectados, sacar el cambio de "Ahora" del roadmap (y repriorizar "Después"), y
recién entonces **borrar el doc** (git conserva la historia).

**Los docs permanentes nunca linkean a `_changes/`.** El roadmap sí (se edita en el harvest),
pero una decisión o un concepto que linkee a un cambio queda con un link roto el día que ese
cambio se cierra — que es exactamente cuando el sistema tiene que seguir funcionando. Si
necesitás referir al trabajo en curso desde un doc permanente, nombralo en prosa.

# Cómo hablarlo con el usuario (importante)

Este sistema lo usa gente que desarrolla conversando, no ingenieros: **la metodología tiene
que ser invisible**.

- **No anuncies el andamiaje.** Nada de "voy a correr okf-plan y crear un `_changes/`".
  Decí: *"antes de tocar código, dejame confirmar qué querés que pase exactamente"*, y
  escribí el doc vos, en silencio.
- **Preguntá en concreto, no en abstracto.** No "¿cuáles son los criterios de aceptación?"
  sino *"¿cómo te das cuenta de que quedó bien? ¿qué tendrías que ver en pantalla?"*.
- **Una o dos preguntas, no un cuestionario.** Lo que no sepas y no sea crítico, proponelo
  vos y pedí confirmación; es más fácil corregir una propuesta que responder en el vacío.
- **Si te pide ir directo, andá directo.** "No me preguntes, hacelo" se respeta: hacé el
  trabajo y registrá al menos la decisión que quedó. Insistir con el proceso es la forma más
  rápida de que el usuario deje de usarlo.
- **Mostrá el valor cuando aparece,** no antes: al retomar ("quedamos en X"), al frenar un
  scope creep ("esto que se te ocurrió lo anoto para después así terminamos lo de ahora").

# Reglas

- **Un cambio por doc.** Si el doc empieza a cubrir dos cosas, partilo.
- **Los cambios NO son fuente de estado del código.** Para "¿qué existe / cómo
  funciona HOY?" gana el código, siempre — aunque haya cambios abiertos.
- **Pero el resultado esperado SÍ manda sobre "¿está terminado?".** Un concepto es
  descriptivo (si difiere del código, el doc es el bug); el resultado esperado de un
  cambio **activo** es normativo: si el código no lo cumple, **el trabajo no está
  terminado**. Bajar la vara se hace **renegociando con el usuario** y editando el doc,
  nunca en silencio ni "interpretando" que ya está. Esa autoridad **caduca en el
  harvest**: cerrado el cambio, vuelve a mandar el código.
- Un doc de `_changes/` que el código nunca cumplió y que nadie está trabajando es un
  cambio **abandonado**: preguntale al usuario si retomarlo (actualizándolo) o borrarlo
  — no lo dejes ahí pudriéndose.
- **No planifiques lo que no vas a hacer.** Un cambio se abre para trabajo que arranca
  ahora; lo demás es **una línea** en "Después" del roadmap, no una spec. Specs de
  trabajo hipotético se pudren igual que la doc que nadie mantiene — nada las obliga a
  seguir la realidad.
- **`_changes/` es la ÚNICA capa de planes tolerada** — justamente porque tiene
  ciclo de cierre. Planes sueltos en `notes/`, TODOs viejos o roadmaps múltiples
  son las capas no-autoritativas que el entrypoint manda a ignorar.
- **El roadmap es de una pantalla.** Si "Después" crece sin que nada salga,
  repriorizá con el usuario y podá: un backlog infinito es otro tipo de rot.
- **No inventes** visión, prioridades ni criterios de "hecho": preguntá.
