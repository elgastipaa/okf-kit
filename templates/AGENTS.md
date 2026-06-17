<!--
  TEMPLATE — copiá esto a la RAÍZ del repo destino como AGENTS.md y completá los
  {{placeholders}}. Borrá este comentario. Mantenelo CHICO: es el contrato + un índice,
  no una enciclopedia. El detalle vive en knowledge/, que se carga bajo demanda.

  UNIVERSAL: AGENTS.md es el estándar cross-vendor. Cualquier IA (Claude, Cursor,
  Copilot, Gemini…) lo lee o se la apunta acá. Las secciones 1-3 son el contrato y son
  iguales para todo repo; completá solo el nombre, las reglas duras y los procedimientos.
  Cómo conectar tu herramienta: reference/install-per-tool.md.
-->

# {{PROJECT_NAME}} — Contrato para agentes

{{Una o dos frases: qué es el proyecto y su stack. Ej: "Web game por turnos.
Next.js 16 + Prisma 7 + Supabase (Postgres)."}}

## Reglas duras

{{Lo que un agente DEBE o NO DEBE hacer, en bullets cortos, linkeando al concepto que
lo explica. Ejemplos:}}
- {{El trabajo de DB corre localmente, no desde la nube — ver knowledge/decisions/0002-db-work-runs-locally.md}}
- {{Antes de tocar el modelo de datos, leé knowledge/schema/}}

## 1. Antes de actuar — leé el contexto

El "qué" y el "por qué" de este proyecto viven en **`knowledge/`** (formato OKF:
markdown + frontmatter). **Empezá por [`knowledge/index.md`](knowledge/index.md)** y bajá
solo a los conceptos que necesites — no cargues todo. Si una decisión o convención no
está clara, leé el concepto o **preguntale al usuario**; no asumas.

## 2. Mientras trabajás — mantené el contexto vivo (el trato)

**Cuándo:** si tomás/descubrís una **decisión** no trivial, cambia la **arquitectura o el
schema**, aparece un **gotcha**, cambia un **procedimiento operativo**, o te explican algo
que "ya deberías saber" → registralo en `knowledge/` (no lo dejes solo en el chat ni en una
memoria privada de la herramienta).

**Cómo (cualquier IA puede hacerlo sin más contexto que esto):**
1. **Elegí la carpeta según el tipo:** decisión → `knowledge/decisions/NNNN-<slug>.md`
   (numerada); gotcha o doc externa → `references/`; build/deploy/DB → `runbooks/`; modelo
   de datos → `schema/`; concepto de dominio → `domain/`. (Si ninguna encaja, creá una.)
2. **Escribí el archivo** con frontmatter: `type` (requerido) + `title` + `description`
   (una sola frase) + `timestamp` (ISO 8601) + `tags`; `resource` si apunta a un activo real.
   (Si un valor lleva `:`, **entrecomillalo** o rompe el YAML.) Debajo, el cuerpo en
   markdown (para decisiones: Contexto / Decisión / Consecuencias).
3. **Actualizá los índices:** agregá la entrada al `index.md` de esa carpeta — en una
   **hoja** va bajo un heading `# {type}`, en la **raíz** bajo `# Subdirectories`
   (`* [Título](archivo.md) - <description>`) — y una línea a `knowledge/log.md` bajo la
   fecha de hoy (`## YYYY-MM-DD`). Si fuera una regla dura nueva, sumala también acá arriba.

**Guardrails:** capturá el **por qué**, no el qué (lo que se deduce del código, **linkealo**,
no lo copies); **no dupliques** (una verdad, un archivo); **cross-links relativos**
(`../dir/x.md`, nunca con `/`); **un concepto por archivo**.

Edge-cases y más detalle: el procedimiento `okf-update` (skill de Claude Code o markdown que
cualquier agente sigue) y `reference/maintaining.md`.

## 3. Antes de cerrar la tarea — verificá

Corré **`python3 scripts/okf_lint.py knowledge`** (o, si no hay Python, seguí el checklist
de verificación). Actualizá `knowledge/` si tu cambio lo amerita. El **pre-commit hook**
(si está instalado) lo chequea igual, en cualquier herramienta.

## Procedimientos

- **Mantener** el contexto: `okf-update` · **Testear** el bundle: `okf-verify`.
- (Arranque: `okf-init` · Migrar contexto existente: `okf-migrate`.)

Son **procedimientos vendor-neutral**: funcionan como skills de Claude Code *o* se siguen
directamente desde cualquier agente. Para conectar tu herramienta (Cursor, Copilot,
Gemini…), ver `reference/install-per-tool.md`.
