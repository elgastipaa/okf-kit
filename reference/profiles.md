# Perfiles — cómo organizar el bundle para cualquier dominio

OKF es **agnóstico al dominio**: la mecánica (archivos markdown + frontmatter,
`index.md`, cross-links, progressive disclosure) es siempre la misma. Lo único que
cambia es **qué carpetas usás y qué ponés en `type:`**.

El kit trae tres perfiles sobre un eje —**código + concepto**—, y el eje no es la industria
sino qué estás documentando: **cómo funciona algo** (`codigo`) o **qué significa algo**
(`concepto`). Si es las dos cosas, `mixto`.

> **Nota de la 0.7.7:** el perfil `datos` se retiró y `wiki` se renombró a `concepto`
> (`--profile wiki` sigue andando como alias). Un repo de datos entra por `mixto`, con las
> carpetas `datasets/ tables/ references/metrics/ references/joins/ glossary/` — el
> vocabulario no se perdió, dejó de ser una rama propia. Ver
> [decisión 0026](../knowledge/decisions/0026-el-eje-es-codigo-mas-concepto.md).

Un **perfil** es un punto de partida: un layout de carpetas + un vocabulario de
`type`. Elegí el que más se parezca a tu proyecto, **combiná** dos si hace falta,
o **inventá** carpetas y tipos si ninguno encaja (OKF lo permite: `type` es libre
y la jerarquía es independiente del dominio). No es una camisa de fuerza.

---

## Núcleo universal (aplica a todos los perfiles)

Estos `type` sirven en cualquier proyecto. Un perfil agrega tipos propios encima.

| `type` | Para qué |
|---|---|
| `Concept` | Una unidad de conocimiento genérica cuando ningún tipo más específico encaja. |
| `Decision` | Una decisión y su *por qué* (estilo ADR). Lo más valioso: el código no lo cuenta. |
| `Reference` | Resumen de material externo (doc, API, paper, norma) que el proyecto usa. Con `# Citations`. |
| `Playbook` | Procedimiento operativo repetible (también llamado *Runbook*). El *cómo*. |
| `Glossary` | Definiciones cortas de términos del proyecto. |
| `Roadmap` | La intención vigente: visión, qué está en curso, qué sigue, no-goals. Uno solo, en la raíz del bundle (`roadmap.md`). Sin checkboxes. |

### Qué tipos son normativos (y qué implica)

La clase de autoridad de un concepto (`OKF-SPEC.md` §3.5) se deduce de su `type`. El default
es **descriptivo**: describe lo que existe, y si difiere del código, el documento es el bug.
Estos tipos son la **excepción normativa** — prescriben lo que debe cumplirse, así que un
código que los contradice está **en violación** (se reporta al usuario; no se edita el
documento para emparejarlo):

| `type` | Por qué es normativo |
|---|---|
| `Decision` (con `status: accepted`) | Alguien decidió esto por una razón; el código que lo ignora la está perdiendo. Una `proposed` todavía no obliga; una `superseded` dejó de obligar. |
| `Convention` | Es una regla de cómo se hacen las cosas acá, no una descripción de cómo están hechas. |
| `Roadmap` | Describe la intención, no el código: que el código todavía no la alcance es trabajo pendiente, no un bug del documento. |
| `Change` (activo, en `_changes/`) | Su *resultado esperado* define "hecho"; caduca al cerrarse el cambio. |

Si un `type` propio no encaja claro en ninguna de las dos clases, declaralo explícito en el
frontmatter con `authority: normative` o `authority: descriptive` (`OKF-SPEC.md` §3.1).

Reglas de nombres y `tags` (todos los perfiles):
- **Archivos:** `kebab-case` descriptivo, sin espacios (`request-flow.md`,
  `mana-regen.md`). Las decisiones se numeran: `0001-<slug>.md`. (Válido: letras,
  números, `_`, `-`, `.` — nunca espacios.)
- **Un concepto por archivo.** Si cubre dos cosas, partilo y linkealos.
- **`tags`:** 2-4 por concepto. Buenos ejes: subsistema (`auth`, `billing`),
  naturaleza (`security`, `performance`, `gotcha`), estado (`deprecated`, `wip`).
- **Frontmatter:** las claves (`type` requerido; `title`/`description`/`timestamp`/`tags`/
  `resource` recomendadas) están en `OKF-SPEC.md §3.1`. Entrecomillá valores con `:`.

**Hechos que viven en el código (cualquier perfil):** conteos, flags, rutas, nombres de
modelos, tunings — **no los transcribas a prosa** (un número a mano = drift). Linkealos
(`resource`) o, si los querés versionados, derivalos con un script propio a una carpeta
**`_generated/`** (el linter la ignora; vos la regenerás y un check de CI avisa si quedó
vieja). El bundle autorado captura el *por qué*; los hechos del código se derivan, no se copian.

**Trabajo futuro (cualquier perfil en desarrollo activo):** el rumbo es un concepto
(`roadmap.md`, type `Roadmap`); el plan/progreso de cada cambio concreto **no** es un
concepto — vive en **`_changes/`** (un doc numerado por cambio, con checkboxes; el linter
la ignora) y al cerrarse se **harvestea** al bundle y se borra. El ciclo completo está en
el skill `okf-plan` (template `_change.md`).

---

## Perfil: Código / Software

Para repos de aplicaciones, librerías, servicios.

```
knowledge/
├── architecture/    # cómo está armado y cómo fluye
├── decisions/       # ADRs numerados — el por qué
├── domain/          # conceptos del negocio que el código asume
├── schema/          # modelo de datos (si aplica)
├── runbooks/        # build, test, deploy, tareas locales
└── references/      # quirks de frameworks, APIs externas
```

| `type` | Carpeta | `resource` → |
|---|---|---|
| `Architecture` | `architecture/` | diagrama opcional |
| `Component` | `architecture/` | el módulo/paquete |
| `Decision` | `decisions/` | el PR/commit que la implementa |
| `Domain Concept` | `domain/` | — |
| `Convention` | `domain/` o `conventions/` | — |
| `Data Model` | `schema/` | el archivo de schema (Prisma, SQL…) |
| `Runbook` | `runbooks/` | el script, si existe |
| `Reference` | `references/` | URL canónica |
| `Integration` | `integrations/` | el cliente/config de la integración |

---

## Perfil: Datos / Analytics

Para datasets, warehouses, pipelines, modelos semánticos. **Este es el caso
original de OKF**, así que el layout espeja los bundles de referencia (GA4,
Stack Overflow).

```
knowledge/
├── datasets/                 # un doc por dataset/schema
├── tables/                   # un doc por tabla (con # Schema en el body)
├── references/
│   ├── metrics/              # definiciones de métricas (SQL)
│   └── joins/                # relaciones/joins entre tablas
└── glossary/                 # términos de negocio (o un solo glossary.md)
```

| `type` | Carpeta | Body típico |
|---|---|---|
| `Dataset` | `datasets/` | qué contiene, grano, frescura, owner |
| `Table` | `tables/` | `# Schema` (columnas), `# Common query patterns` (SQL) |
| `Metric` | `references/metrics/` | la definición + el SQL de cálculo |
| `Join` | `references/joins/` | las claves y el SQL del join |
| `Reference` | `references/` | enums, códigos, docs externas |
| `Glossary` | `glossary/` | término → definición |

> Para tablas, el body sigue la convención: prosa corta (grano: "una fila por X",
> rango temporal, caveats), luego `# Schema`, luego `# Common query patterns`
> (SQL), luego `# Citations`. Linkeá tabla→dataset y tabla→tabla por sus joins.

---

## Perfil: Wiki / Base de conocimiento

Para documentación, manuales, knowledge bases, notas — proyectos donde el
contenido **es** el producto, no metadata sobre otra cosa.

```
knowledge/
├── <tema-1>/        # organizá por tema, no por tipo
│   ├── index.md
│   └── <articulo>.md
├── <tema-2>/
├── playbooks/       # procedimientos paso a paso
└── glossary.md      # o una carpeta glossary/
```

| `type` | Para qué |
|---|---|
| `Article` | Una página/entrada de contenido principal. |
| `Note` | Una nota corta, no estructurada como artículo. |
| `Concept` | Una idea/definición central referenciada por otros docs. |
| `Playbook` | Un procedimiento paso a paso. |
| `Reference` | Material externo resumido. |
| `Glossary` | Términos. |

> En wikis organizá **por tema** (la jerarquía de carpetas refleja la taxonomía
> del contenido), no por tipo. El grafo de cross-links es lo que conecta temas
> entre sí, más allá del árbol.

---

## Perfil: Genérico / Mixto

Cuando el proyecto no encaja limpio en ninguno, o mezcla varios (ej: un repo de
código que también documenta su dataset). Empezá mínimo y dejá que crezca:

```
knowledge/
├── index.md
├── log.md
├── decisions/       # casi siempre útil
├── references/      # casi siempre útil
└── <lo que el proyecto pida>/
```

Usá el núcleo universal (`Concept`, `Decision`, `Reference`, `Playbook`,
`Glossary`) y agregá carpetas/tipos a medida que aparezca la necesidad. **No crees
carpetas vacías "por las dudas".**

---

## Cómo elegir / combinar / inventar

1. **Mirá qué es el repo** (manifiestos, README, estructura — ver `GUIDE.md` §3).
2. **¿Documentás cómo funciona algo, o qué significa algo?** Lo primero es `codigo`, lo
   segundo `concepto`. Ese es el eje.
3. **¿Las dos?** `mixto`: combiná las carpetas que hagan falta. Un repo de código con un
   dataset documentado es `codigo` + `datasets/`/`tables/`; un repo de datos es `mixto` con
   ese vocabulario como base.
4. **¿Nada encaja?** Inventá una carpeta y un `type` descriptivo y self-explanatory.
   Los consumidores OKF toleran `type` desconocidos por diseño.

La regla no cambia nunca: **capturá el *por qué* que la fuente no dice, una verdad
por archivo, cross-linkeada, en markdown plano.**
