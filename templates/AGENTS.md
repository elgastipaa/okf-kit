<!--
  TEMPLATE — copiá esto a la RAÍZ del repo destino como AGENTS.md, completá los
  {{placeholders}} y borrá este comentario.

  MANTENELO CHICO. Es lo ÚNICO que se carga en cada turno de cada sesión: cada línea de
  más se paga siempre, y un contrato largo se skimea (pierde obediencia). El detalle vive
  en knowledge/ y en los procedimientos, que se cargan bajo demanda. Si crece, mové el
  detalle a un concepto y dejá acá el puntero. Techo: 7000 caracteres instalado
  (~1750 tokens); el gate del kit lo verifica.

  BORRÁ lo que no instalaste (si no, mandás al agente a archivos que no existen). El
  andamiaje son las 8 líneas de comentario marcadas `OKF:future-layer:start` y
  `OKF:future-layer:end` (4 pares: dos en §1, uno en §3 y uno en Procedimientos):
  - SIEMPRE: borrá esas 8 líneas de marcadores — son instrucciones de instalación, no
    contrato, y se pagan en cada turno.
  - Si NO instalaste la capa de futuro (la del rumbo + los cambios en curso): borrá además
    TODO lo que quede ENTRE cada par. No hay nada más que tocar — el resto del contrato no
    la nombra.
  - Si no instalaste scripts/okf_lint.py: ajustá la línea del linter en §3.

  UNIVERSAL: AGENTS.md es el estándar cross-vendor — toda IA lo lee, o se la apunta acá
  (ver reference/install-per-tool.md). Las secciones 1-3 son iguales para todo repo.
-->

# {{PROJECT_NAME}} — Contrato para agentes

{{Una o dos frases: qué es el proyecto y su stack. Ej: "Web game por turnos.
Next.js 16 + Prisma 7 + Supabase (Postgres)."}}

## Reglas duras

{{Lo que un agente DEBE o NO DEBE hacer, en bullets cortos, linkeando al concepto que lo
explica. Ejemplos:}}
- {{El trabajo de DB corre localmente, no desde la nube — ver knowledge/decisions/0002-db-work-runs-locally.md}}
- {{Antes de tocar el modelo de datos, leé knowledge/schema/}}

## 1. Antes de actuar — leé el contexto

El "qué" y el "por qué" de este proyecto viven en **`knowledge/`** (formato OKF: markdown +
frontmatter). **Empezá por [`knowledge/index.md`](knowledge/index.md)** y bajá solo a los
conceptos que necesites — no cargues todo. Si algo no está claro, leé el concepto o
**preguntale al usuario**; no asumas.

**Este archivo es un MAPA, no la respuesta.** No contestes una pregunta de dominio ("¿cómo
funciona X?", "¿cuál es la regla de Y?") citando las reglas o secciones de *este* contrato:
seguí el mapa hasta el concepto en `knowledge/` o hasta el código. Si una sección de acá
*parece* contestarla, es coincidencia — verificá en la fuente. **¿Pregunta a nivel
término/sigla?** Si el bundle tiene un `glossary.md`, abrilo **antes de grepear código**.

**Si el documento y el código no coinciden, quién gana depende del documento:**

- **Descriptivo** (arquitectura, schema, dominio, runbooks, references, glosario — casi todo
  el bundle): **gana el código**, el concepto es un bug — arreglalo. Lo que se deduce del
  código se **linkea**, no se copia (un número a mano = drift).
- **Normativo** (decisiones con `status: accepted`, convenciones): **el código está en
  violación**. **No edites el documento** para emparejarlo con lo que el código hace hoy, y
  **no sigas de largo**: avisale al usuario con las dos salidas legítimas — **arreglar el
  código**, o **superseder** la decisión con una nueva (mecánica: `okf-update`). Si estabas
  haciendo otra cosa, reportalo y seguí; no lo arregles de prepo.
<!-- OKF:future-layer:start -->
- También son normativos **el rumbo** y el *resultado esperado* de un cambio activo: que el
  código todavía no los alcance es **trabajo pendiente**, no un bug del documento.
<!-- OKF:future-layer:end -->

Para "¿qué existe / cómo funciona HOY?" gana el código **siempre**: lo normativo dice qué
*debe* pasar, nunca qué pasa.

<!-- OKF:future-layer:start -->
**Rumbo y trabajo en curso.** El rumbo vigente (visión, qué sigue, no-goals) está en
[`knowledge/roadmap.md`](knowledge/roadmap.md); el trabajo abierto, en `knowledge/_changes/`
(un doc por cambio: mini-spec + tareas). **Se dispara solo — el usuario no tiene que pedirlo
ni conocer estos archivos:**

- **Primer mensaje de la sesión** → si hay un cambio activo, decilo en una línea ("venías con
  X, quedó en la tarea Y — ¿seguimos con eso?"). No arranques de cero si había trabajo abierto.
- **Te piden algo no trivial** → **antes de codear**, acordá con el usuario qué tiene que
  pasar para considerarlo listo y qué queda afuera, y dejalo escrito en `_changes/`. Un typo
  o un ajuste chico no lleva doc.
- **"¿Qué sigue?" / "¿en qué estábamos?"** → respondé desde el roadmap y los cambios, no
  reconstruyendo del código.
- **Terminaste un cambio** → hacé su harvest (§3). **Aparece una idea que no es la tarea
  actual** → **chequeá primero si ya existe en el código**; si no existe, una línea en
  "Después" del roadmap. No la implementes de paso, y no anotes como pendiente algo ya hecho.

Detalle del procedimiento: **`okf-plan`**.
<!-- OKF:future-layer:end -->

**Hablale al usuario en su idioma, no en "OKF":** no le anuncies archivos, procedimientos ni
metodologías — preguntale *qué tiene que pasar para que esté listo* y escribí vos lo que haga
falta. Si te pide ir directo al código, **respetalo**: hacé el trabajo y registrá al menos la
decisión que haya quedado.

**Capas NO autoritativas — no reconcilies basura.** {{Listá los dirs/archivos scratch,
legacy, planes viejos o exploración que **NO reflejan el estado actual** — ej. `notes/`,
mockups, docs de refactors pasados. Si el repo no tiene ninguna, borrá esta sección.}} Para "¿qué existe / cuántos / a qué nivel HOY?" la
respuesta sale **del código**; si difieren, gana el código y estas capas se ignoran (no
gastes turnos reconciliándolas).

## 2. Mientras trabajás — mantené el contexto vivo (el trato)

**Cuándo:** una **decisión** no trivial, un cambio de **arquitectura o schema**, un
**gotcha**, un cambio de **procedimiento operativo**, o algo que te explican y "ya deberías
saber" → registralo en `knowledge/` (no lo dejes solo en el chat ni en una memoria privada
de la herramienta).

**Cómo (cualquier IA puede hacerlo sin más contexto que esto):**

1. **Elegí la carpeta según el tipo:** decisión → `knowledge/decisions/NNNN-<slug>.md`
   (numerada); gotcha o doc externa → `references/`; build/deploy/DB → `runbooks/`; modelo de
   datos → `schema/`; concepto de dominio → `domain/`. (Si ninguna encaja, creá una.)
2. **Escribí el archivo** con frontmatter: `type` (requerido) + `title` + `description` (una
   sola frase) + `timestamp` (ISO 8601); `tags` y `resource` si aplican. Si un valor lleva
   `:`, **entrecomillalo** o rompe el YAML. **Una decisión lleva además `status: accepted`**
   —sin eso no cuenta como normativa— y va Contexto / Decisión / Consecuencias.
3. **Actualizá los índices:** agregá la entrada al `index.md` de esa carpeta, bajo un heading
   `# {type}` (`* [Título](archivo.md) - <description>`); si creaste una **carpeta** nueva,
   sumala al `# Subdirectories` del index raíz — y, **si mantenés `log.md`**, una línea bajo la
   fecha de hoy (`## YYYY-MM-DD`); si no, el log es git + `decisions/`. Si fuera una regla
   dura nueva, sumala también arriba.

**Guardrails:** capturá el **por qué**, no el qué; **no dupliques** (una verdad, un archivo);
**cross-links relativos** (`../dir/x.md`, nunca con `/`); **un concepto por archivo**.
Edge-cases y más detalle: `okf-update`.

## 3. Antes de cerrar la tarea — verificá

Corré **`python3 scripts/okf_lint.py knowledge`** (o, si no hay Python, seguí el checklist de
verificación) y actualizá `knowledge/` si tu cambio lo amerita.
<!-- OKF:future-layer:start -->
Si terminaste un cambio de `_changes/`, hacé su **harvest** antes de cerrar (la sección
`# Harvest` del propio doc, vía `okf-plan`): decisiones al bundle, roadmap al día, y el doc
se borra.
<!-- OKF:future-layer:end -->
El **pre-commit hook**, si está instalado, lo chequea igual en cualquier herramienta.

## Procedimientos

- **Mantener** el contexto: `okf-update`
- **Testear** el bundle: `okf-verify`
<!-- OKF:future-layer:start -->
- **Planificar** trabajo futuro y cerrar cambios: `okf-plan`
<!-- OKF:future-layer:end -->

Son **vendor-neutral**: corren como skills de Claude Code *o* los sigue cualquier agente
leyendo su procedimiento (en `docs/okf/<nombre>.md` si no se usa Claude Code).
