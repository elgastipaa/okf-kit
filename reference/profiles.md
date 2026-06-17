# Perfiles — cómo organizar el bundle para cualquier dominio

OKF es **agnóstico al dominio**: la mecánica (archivos markdown + frontmatter,
`index.md`, `log.md`, cross-links, progressive disclosure) es siempre la misma.
Lo único que cambia entre un proyecto de datos, uno de código y una wiki es **qué
carpetas usás y qué ponés en `type:`**.

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

Reglas de nombres y `tags` (todos los perfiles):
- **Archivos:** `kebab-case` descriptivo, sin espacios (`request-flow.md`,
  `mana-regen.md`). Las decisiones se numeran: `0001-<slug>.md`. (Válido: letras,
  números, `_`, `-`, `.` — nunca espacios.)
- **Un concepto por archivo.** Si cubre dos cosas, partilo y linkealos.
- **`tags`:** 2-4 por concepto. Buenos ejes: subsistema (`auth`, `billing`),
  naturaleza (`security`, `performance`, `gotcha`), estado (`deprecated`, `wip`).
- **Frontmatter:** las claves (`type` requerido; `title`/`description`/`timestamp`/`tags`/
  `resource` recomendadas) están en `OKF-SPEC.md §3.1`. Entrecomillá valores con `:`.

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
2. **¿Es principalmente código, datos o contenido?** Elegí ese perfil como base.
3. **¿Mezcla?** Combiná: un repo de código con un dataset documentado usa el perfil
   Código + una carpeta `datasets/`/`tables/` del perfil Datos.
4. **¿Nada encaja?** Inventá una carpeta y un `type` descriptivo y self-explanatory.
   Los consumidores OKF toleran `type` desconocidos por diseño.

La regla no cambia nunca: **capturá el *por qué* que la fuente no dice, una verdad
por archivo, cross-linkeada, en markdown plano.**
