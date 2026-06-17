# Open Knowledge Format (OKF) — especificación condensada

**Versión 0.1.** Esta es una versión condensada y self-contained de la spec
oficial de Google Cloud
([knowledge-catalog/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)),
con el foco puesto en usar OKF para **contexto de proyectos de software**. Las
reglas normativas (MUST/SHOULD) se mantienen fieles al original.

OKF representa *conocimiento* como **un directorio de archivos markdown con
frontmatter YAML**. Sin schema registry, sin autoridad central, sin tooling
obligatorio.

---

## 1. Terminología

- **Bundle** — colección jerárquica y autocontenida de documentos de conocimiento.
  La unidad de distribución (normalmente la carpeta `knowledge/` del repo).
- **Concepto** — una unidad de conocimiento = un archivo markdown. Puede describir
  algo tangible (una tabla, un módulo, un endpoint) o abstracto (una decisión, una
  convención, un concepto de dominio).
- **Concept ID** — el path del archivo dentro del bundle, sin el `.md`. Ej:
  `decisions/0001-orm.md` → concept id `decisions/0001-orm`.
- **Frontmatter** — bloque YAML delimitado por `---` al inicio del archivo.
- **Body** — todo lo que sigue al frontmatter.
- **Link** — link markdown estándar de un concepto a otro; expresa una relación.

---

## 2. Estructura del bundle

Un árbol de directorios de archivos `.md`. La estructura es **independiente del
dominio**: organizá los conceptos como tenga sentido.

```
knowledge/
├── index.md            # Opcional pero recomendado. Listado para progressive disclosure.
├── log.md              # Opcional. Historial cronológico de cambios.
├── <concepto>.md       # Un concepto en la raíz.
└── <subdir>/           # Subdirectorios agrupan conceptos.
    ├── index.md
    └── <concepto>.md
```

### Nombres reservados

| Archivo | Significado |
|---|---|
| `index.md` | Listado de directorio (§5). No es un concepto. |
| `log.md` | Historial de cambios (§6). No es un concepto. |

Cualquier otro `.md` es un concepto.

---

## 3. Documentos de concepto

Cada concepto es un markdown UTF-8 con dos partes: frontmatter YAML + body.

### 3.1 Frontmatter

```yaml
---
type: <Tipo>                       # REQUERIDO
title: <Nombre para mostrar>       # Recomendado
description: <Resumen de una línea> # Recomendado — se usa en index.md
resource: <URI canónica del activo> # Opcional (link al código, dashboard, etc.)
tags: [<tag>, <tag>]               # Opcional
timestamp: <ISO 8601>              # Opcional — última modificación significativa
# … cualquier otra clave que quieras
---
```

**Requerido:**
- `type` — string corto que identifica el tipo de concepto. Se usa para routing,
  filtrado y presentación. **No se registra centralmente.** Ver
  `reference/profiles.md` para los valores recomendados por dominio (código,
  datos, wiki).
  Los consumidores DEBEN tolerar `type` desconocidos.

**Recomendado (en orden de prioridad):**
- `title` — nombre legible. Si falta, se deriva del filename.
- `description` — **una sola frase**. Se usa verbatim en los `index.md` y snippets.
- `resource` — URI que identifica el activo subyacente (link al archivo de código,
  a un dashboard, a un ticket…). Ausente para conceptos abstractos.
- `tags` — lista YAML de strings cortos para categorización transversal.
- `timestamp` — datetime ISO 8601 del último cambio significativo.

> **Para *consumir*, solo `type` es obligatorio (§8 Conformidad).** Pero al
> *escribir*, autorá siempre `type` + `title` + `description` + `timestamp`: la
> implementación de referencia los exige y son los que hacen que los `index.md` y
> el progressive disclosure funcionen bien. Tratalos como el set por defecto.

**Extensiones:** podés agregar cualquier clave. Los consumidores DEBEN preservar
claves desconocidas y NO DEBEN rechazar documentos por campos no reconocidos.

**Gotcha YAML:** si un valor contiene `:` (p.ej. una `description` con dos puntos),
**entrecomillalo** (`description: "a: b"`) o el YAML lo parsea como un mapping y se rompe.

### 3.2 Body

Markdown estándar. Preferí estructura (headings, listas, tablas, bloques de código)
sobre prosa libre — ayuda a la lectura humana y a la recuperación por agentes.

Headings con significado **convencional** (usalos cuando apliquen):

| Heading | Para qué |
|---|---|
| `# Schema` | Descripción estructurada de campos/columnas de un activo. |
| `# Examples` | Ejemplos concretos de uso, normalmente en bloques de código. |
| `# Citations` | Fuentes externas que respaldan afirmaciones del body (§7). |

### 3.3 Ejemplo

(Este concepto vive en `decisions/`; por eso los cross-links suben con `../` para
llegar a `runbooks/` y `domain/` — siempre **relativos al archivo**, nunca con `/`.)

```markdown
---
type: Decision
title: Usamos cola de mensajes para los emails transaccionales
description: Los emails salen async vía cola; nunca en el request del usuario.
resource: https://github.com/acme/app/blob/main/src/email/queue.ts
tags: [email, async, reliability]
timestamp: 2026-06-16T00:00:00Z
---

# Contexto
Mandar emails en el request hacía timeouts cuando el proveedor estaba lento.

# Decisión
Todo email transaccional se encola y lo procesa un worker. Ver el
[worker de email](../runbooks/email-worker.md).

# Consecuencias
Hay latencia de hasta ~30s en la entrega. Aceptable para transaccionales.
No usar esto para OTPs de login (ver [auth](../domain/auth.md)).
```

---

## 4. Cross-linking

Los conceptos SE LINKEAN entre sí con links markdown estándar. Dos formas:

### 4.1 Relativos al archivo — **recomendado (default)**
Paths markdown relativos al directorio del documento actual.
```markdown
Ver el [concepto vecino](./other.md), el [padre](../index.md),
o una [tabla](../schema/users.md).
```
**Por qué es el default:** funcionan sin ninguna herramienta — renderizan como
links vivos en GitHub, en la preview de cualquier editor y en cualquier visor de
markdown plano. Un agente los resuelve con aritmética de paths normal. Esta es la
convención que usa el propio código de referencia de OKF (su generador de índices
emite links relativos al archivo, justamente por compatibilidad con GitHub).

### 4.2 Absolutos (relativos al bundle) — solo con un consumidor que los resuelva
Empiezan con `/`, interpretados desde la raíz del bundle.
```markdown
Ver la [tabla de usuarios](/schema/users.md).
```
Son estables ante movimientos de archivos, **pero NO funcionan en GitHub ni en
visores planos** (GitHub interpreta `/` como la raíz del repo, no del bundle).
Solo usalos si vas a consumir el bundle con una herramienta que reescriba esos
links. Para un sistema sin herramientas, **preferí siempre 4.1**.

> Nota de fidelidad: la spec original de OKF "recomienda" la forma absoluta, pero
> su propia implementación de referencia genera links relativos al archivo. Esta
> guía sigue la implementación, que es lo que de verdad funciona sin tooling.

### 4.3 Semántica
Un link de A a B afirma *una relación*; el tipo de relación lo dice la prosa
alrededor, no el link. Los consumidores DEBEN tolerar links rotos: un link a algo
que todavía no existe representa conocimiento no escrito aún, no un error.

---

## 5. Archivos `index.md`

Pueden aparecer en cualquier directorio. Enumeran el contenido para **progressive
disclosure** — dejar que un humano o agente vea qué hay antes de abrir cada doc.

Los `index.md` **no llevan frontmatter** (excepto, opcionalmente, el de la raíz del
bundle, que puede declarar `okf_version` y otras claves del productor como `kit_version`
— ver §9). Cada entrada es un link **relativo al archivo**
+ la `description` del frontmatter del concepto linkeado.

**Convención que usa la implementación de referencia** (seguila para que un humano
y un agente lean lo mismo):

- **Conceptos**, agrupados bajo un heading por su `type`:
  ```markdown
  # Decision

  * [Usamos cola para emails](0007-email-queue.md) - Los emails salen async vía cola.
  * [DB solo local](0002-db-local.md) - Migraciones y seeds van por CLI local.

  # Reference

  * [useActionState encoding](useactionstate.md) - Los forms mandan FormData, no JSON.
  ```
- **Subdirectorios**, bajo un heading `# Subdirectories`, linkeando a su `index.md`:
  ```markdown
  # Subdirectories

  * [decisions](decisions/index.md) - Decisiones de diseño y su por qué.
  * [runbooks](runbooks/index.md) - Comandos operativos del proyecto.
  ```

El `index.md` de la **raíz** del bundle típicamente solo lista subdirectorios
(`# Subdirectories`); los `index.md` de las hojas agrupan los conceptos por `type`.
Se pueden escribir a mano o generar automáticamente — la forma es la misma. Como
todo en OKF, son opcionales: un consumidor puede sintetizar uno al vuelo si falta.

---

## 6. Archivos `log.md` (opcional)

Registran el historial de cambios de su scope. Lista de entradas agrupadas por
fecha, más nuevas primero:

```markdown
# Update Log

## 2026-06-16
* **Update**: Agregada la [decisión de cola de emails](decisions/0007-email-queue.md).
* **Creation**: Creado el bundle inicial.

## 2026-06-10
* **Initialization**: Estructura de directorios base.
```

Las fechas DEBEN ser ISO 8601 `YYYY-MM-DD`. La palabra en negrita inicial
(`**Update**`, `**Creation**`, `**Deprecation**`…) es convención, no requisito.

---

## 7. Citations

Cuando un concepto hace afirmaciones tomadas de material externo, listalas bajo
`# Citations` al final, numeradas:

```markdown
# Citations
[1] [Next.js cache components](https://nextjs.org/docs/...)
[2] [Runbook interno de deploy](../runbooks/deploy.md)
```

Pueden ser URLs absolutas, paths relativos al bundle, o paths a `references/`.

---

## 8. Conformidad

Un bundle es **conforme** con OKF v0.1 si:

1. Todo `.md` no reservado tiene un bloque de frontmatter YAML parseable.
2. Todo frontmatter tiene un `type` no vacío.
3. Los archivos reservados (`index.md`, `log.md`) siguen la estructura de §5 y §6.

Los consumidores DEBEN tratar todo lo demás como guía blanda. En particular, NO
DEBEN rechazar un bundle por: campos opcionales faltantes, `type` desconocidos,
claves extra, links rotos, o `index.md` ausentes. Este consumo permisivo es
intencional: OKF tiene que seguir siendo útil mientras los bundles crecen, se
refactorizan y se generan parcialmente con agentes.

---

## 9. Versionado

Esta es la versión **0.1**. Un bundle PUEDE declarar la versión que targetea
incluyendo `okf_version: "0.1"` en el frontmatter del `index.md` raíz (el único
`index.md` que lleva frontmatter). Ese bloque PUEDE incluir además **otras claves del
productor** (p.ej. `kit_version`, la revisión de la herramienta que generó el bundle),
igual que cualquier concepto (§3.1, Extensiones).
