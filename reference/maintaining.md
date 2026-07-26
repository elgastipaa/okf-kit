# Mantenimiento — el ciclo de vida de un repo ya "initeado" con OKF

`GUIDE.md` cubre el **init** (montar el bundle). Esto cubre **lo que viene después**:
cómo el contexto se mantiene vivo y no se pudre mientras el proyecto evoluciona, y cómo
eso vale para **cualquier IA** que trabaje el repo (no solo Claude Code).

---

## El contrato (vale para cualquier agente)

Está en `AGENTS.md` —el archivo que toda herramienta lee o al que se la apunta— en tres
reglas:

1. **Antes de actuar, leé el contexto** (`knowledge/`, empezando por `index.md`).
2. **Mientras trabajás, mantené el contexto vivo:** toda decisión no trivial, cambio de
   arquitectura/schema, gotcha, o cosa que "ya deberías saber" → un concepto OKF en
   `knowledge/`.
3. **Antes de cerrar, verificá:** corré el linter (o el checklist) y actualizá `knowledge/`
   si hizo falta.

---

## Cuándo actualizar el bundle

| Disparador | Dónde |
|---|---|
| Se toma/descubre una decisión no trivial | `knowledge/decisions/NNNN-*.md` |
| Cambia la arquitectura, el schema o el modelo de datos | editá el concepto afectado |
| Aparece un gotcha / quirk (framework, API, setup) | `knowledge/references/*.md` |
| Cambia un procedimiento operativo (build/test/deploy/DB) | `knowledge/runbooks/*.md` |
| Te explican algo que el código no dice y vas a re-necesitar | la carpeta del perfil que toque |

Lo que ya se deduce del código **no** se duplica: se linkea (un número a mano = drift).
El procedimiento detallado está en `okf-update` (ver abajo "Universalidad").

---

## Deprecar y reemplazar (no borres a las apuradas)

El conocimiento superado no se borra ni se edita "para darlo de baja" — eso deja agujeros.
En cambio:

- **Decisión reemplazada:** decisión **nueva** con `status: accepted` y `supersedes: NNNN`;
  la vieja pasa a `status: "superseded by MMMM"`. Queda el camino de migración.
- **Concepto deprecado:** movélo a `knowledge/archive/` o marcá arriba `SUPERSEDED → ver X`.
  **Nombrá el concepto viejo** (término, flag, clase) para que un `grep` futuro lo encuentre.
- **Gana el código (descriptivos):** si un concepto que *describe* algo ya no coincide con
  el código, el concepto es el bug — corregilo o deprecalo en el mismo cambio.
- **Al revés para los normativos:** si el código viola una **decisión aceptada**, una
  convención o el rumbo, el bug es el código. No se edita el documento para emparejarlo:
  se avisa al usuario y se elige entre arreglar el código o **superseder** la decisión
  (canónico: `OKF-SPEC.md` §3.5; mapeo de tipos: `reference/profiles.md`).

## El rumbo y los cambios en curso (la capa de futuro)

Si el repo usa la capa de futuro (recomendada en desarrollo activo): el rumbo vigente vive
en `knowledge/roadmap.md` (un concepto; se edita cuando cambia) y cada cambio no trivial
nace como doc en `knowledge/_changes/` y muere en un **harvest** hacia el bundle. El ciclo
completo (abrir / retomar / cerrar) es el skill **`okf-plan`**; la mecánica de escribir lo
cosechado es la de `okf-update`.

## Scratchpad (opcional, para tareas largas)

Para trabajo multi-sesión que tiene que sobrevivir a la compactación del contexto, podés
mantener un `knowledge/_scratchpad.md` efímero (razonamiento, progreso, dudas). El prefijo
`_` hace que el linter lo ignore — **no es parte del bundle permanente**; borralo al cerrar.

---

## Las capas de enforcement (de blanda a dura)

El mantenimiento no depende de la buena voluntad: hay varias redes, y ninguna es
obligatoria pero juntas hacen difícil que el contexto se pudra.

1. **El contrato en `AGENTS.md`** — lo lee toda IA al arrancar. Blando (instrucción).
2. **`okf-update`** (skill de Claude Code *o* procedimiento que cualquier agente sigue) —
   cuando la tarea matchea, guía la actualización.
3. **Pre-commit hook** (`templates/hooks/pre-commit`) — **universal, a nivel git**: bloquea
   el commit si el bundle no es conforme y **avisa** si cambió código pero `knowledge/` no.
   Corre con cualquier herramienta e IA.
4. **CI** (`templates/ci/okf.yml`) — corre el linter en cada push. Última red en el server.
5. **`okf-verify` periódico + cold test (Nivel 3)** — auditoría: ¿un agente en frío sigue
   entendiendo el proyecto solo con el bundle? Cada pregunta que falla = concepto faltante.

---

## Universalidad (no es solo para Claude Code)

Lo **universal** son las capas que no dependen de un vendor: `AGENTS.md` (el contrato), el
**git hook**, el **CI** y el **linter**. Los *skills* (`okf-update`/`okf-verify`/…) son una
**conveniencia** para Claude Code (auto-disparo); su contenido es markdown vendor-neutral
que cualquier agente puede seguir directamente. Para conectar Cursor, Copilot, Gemini u
otra herramienta, ver **`reference/install-per-tool.md`**.

---

## Anti-rot: señales de que el contexto envejeció

- Hubo decisiones/cambios recientes que **no** están en `knowledge/` (el hook #3 lo avisa).
- Hay docs en `_changes/` terminados sin harvest, abandonados, o un `roadmap.md` que ya no
  refleja lo que se está haciendo → harvest/poda pendiente (`okf-plan`).
- El **cold test** (Nivel 3) empieza a fallar preguntas sobre features nuevas.
- Los `index.md` no coinciden con los archivos (el linter lo marca).
- Un **concepto descriptivo contradice el código** → gana el código; el concepto es un bug.
- El **código viola una decisión aceptada** (drift al revés, el más caro: se pierde el
  *por qué*) → reportalo; arreglar el código o superseder la decisión, nunca editarla en
  silencio. Se caza con el chequeo de cumplimiento de `reference/verification.md`.
- El bundle creció y cuesta navegarlo → ver `special-cases.md` (cuándo partir).

Regla: el bundle vale **solo si se mantiene**. Una pieza de conocimiento por vez, como
efecto colateral del trabajo normal — no como un proyecto aparte.
