# Ejemplos: mini-bundles OKF bien hechos

OKF sirve igual para **código**, **datos** y **wikis**. Acá hay un ejemplo de cada
uno. Copiá el **estilo** — el *por qué* capturado, una verdad por archivo,
cross-links relativos al archivo, `description` de una frase — no el contenido.

---

## Ejemplo 1 — Código (software)

Contexto para un web game tipo Next.js + Prisma + Supabase. Perfil **Código**.

```
knowledge/
├── index.md
├── log.md
├── architecture/overview.md
├── domain/mana-regen.md
├── decisions/0001-prisma7-ts-only.md
├── decisions/0002-db-work-runs-locally.md
├── runbooks/smoke-test.md
└── references/useactionstate-encoding.md
```

### `knowledge/index.md` (raíz → subdirectorios)
```markdown
---
okf_version: "0.1"
kit_version: "{{KIT_VERSION}}"   # okf-init lo estampa desde coding/OKF/VERSION
---

# Subdirectories

* [architecture](architecture/index.md) - Cómo está armado el sistema y el flujo de un turno.
* [domain](domain/index.md) - Reglas del juego: maná, el cónclave, turnos.
* [decisions](decisions/index.md) - Decisiones de diseño y su por qué.
* [runbooks](runbooks/index.md) - Comandos operativos: smoke test, DB, deploy.
* [references](references/index.md) - Quirks de frameworks y APIs externas.
```

### `knowledge/decisions/0002-db-work-runs-locally.md`
```markdown
---
type: Decision
title: El trabajo de DB corre localmente, no desde sesiones cloud
description: Las sesiones cloud no alcanzan Postgres; migraciones y seeds van por CLI local.
tags: [db, prisma, supabase, gotcha]
timestamp: 2026-06-16T00:00:00Z
---

# Contexto
El Postgres de Supabase no es accesible desde sesiones de IA en la nube.

# Decisión
Todo lo que toque la DB (migraciones Prisma, seeds, el smoke test) corre por
**CLI local**. Ver el [smoke runbook](../runbooks/smoke-test.md).

# Consecuencias
Un agente en la nube NO debe intentar conectarse a Postgres: debe pedirle al
usuario que corra el comando localmente y esperar el output.
```

### `knowledge/references/useactionstate-encoding.md`
```markdown
---
type: Reference
title: useActionState codifica los forms distinto
description: Los forms con useActionState mandan FormData; parsear distinto que JSON.
resource: https://react.dev/reference/react/useActionState
tags: [next, forms, gotcha]
timestamp: 2026-06-16T00:00:00Z
---

Cuando un form usa `useActionState`, el server action recibe `FormData`, no JSON.
Leé los campos con `formData.get(...)`. Olvidarlo da `undefined` silencioso.

# Citations
[1] https://react.dev/reference/react/useActionState
```

---

## Ejemplo 2 — Datos / Analytics

Contexto para un dataset de e-commerce. Perfil **Datos** (espeja los bundles de
referencia de OKF: GA4, Stack Overflow).

```
knowledge/
├── index.md
├── datasets/ecommerce.md
├── tables/orders.md
├── references/metrics/avg_order_value.md
└── references/joins/orders___customers.md
```

### `knowledge/tables/index.md` (hoja → agrupado por `type`)
```markdown
# Table

* [Orders](orders.md) - Una fila por orden completada; grano diario; PII obfuscada.
```

### `knowledge/tables/orders.md`
```markdown
---
type: Table
title: Orders
description: Una fila por orden de cliente completada, en todos los canales.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders, revenue]
timestamp: 2026-06-16T00:00:00Z
---

Una fila por **orden completada**. Cubre 2019→hoy. Las órdenes canceladas no
aparecen (ver [estados de orden](../references/order_states.md)).

# Schema
| Columna       | Tipo      | Descripción |
|---------------|-----------|-------------|
| `order_id`    | STRING    | Id único de orden. |
| `customer_id` | STRING    | FK a la tabla [customers](customers.md). |
| `total_usd`   | NUMERIC   | Total en USD. |
| `placed_at`   | TIMESTAMP | Cuándo se hizo la orden. |

# Common query patterns
```sql
SELECT DATE(placed_at) AS d, SUM(total_usd) AS revenue
FROM `acme.sales.orders` GROUP BY d ORDER BY d;
```

# Citations
[1] [Esquema de la tabla](https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders)
```

### `knowledge/references/metrics/avg_order_value.md`
```markdown
---
type: Metric
title: Average Order Value (AOV)
description: Ingreso total dividido por cantidad de órdenes, en un período.
tags: [metric, revenue]
timestamp: 2026-06-16T00:00:00Z
---

AOV = ingreso total / número de órdenes. Se calcula sobre [orders](../../tables/orders.md).

```sql
SELECT SUM(total_usd) / COUNT(*) AS aov FROM `acme.sales.orders`;
```
```

---

## Ejemplo 3 — Wiki / Base de conocimiento

Una base de conocimiento de un equipo. Perfil **Wiki**: organizada **por tema**,
no por tipo. El contenido *es* el producto.

```
knowledge/
├── index.md
├── onboarding/
│   ├── index.md
│   └── primer-dia.md
├── procesos/
│   └── code-review.md
├── playbooks/incident-response.md
└── glossary.md
```

### `knowledge/onboarding/primer-dia.md`
```markdown
---
type: Article
title: Tu primer día
description: Qué configurar y a quién pedirle accesos el primer día.
tags: [onboarding, people]
timestamp: 2026-06-16T00:00:00Z
---

Bienvenido. Antes que nada pedí accesos (ver [code review](../procesos/code-review.md)
para entender cómo se mergea acá). Si algo se rompe en prod, seguí el
[playbook de incidentes](../playbooks/incident-response.md).

# Checklist
1. Configurar el entorno.
2. Pedir acceso a los repos.
3. Leer el [glosario](../glossary.md) del equipo.
```

### `knowledge/playbooks/incident-response.md`
```markdown
---
type: Playbook
title: Respuesta a incidentes
description: Pasos para triar y comunicar un incidente de producción.
tags: [oncall, incident]
timestamp: 2026-06-16T00:00:00Z
---

# Cuándo
Cuando un servicio crítico está caído o degradado.

# Pasos
1. Declarar el incidente en el canal #incidents.
2. Asignar un comandante de incidente.
3. ...
```

---

## Qué notar en los tres

- Cada concepto captura el **por qué / lo no obvio**, no re-explica lo que la
  fuente ya dice (lo linkea con `resource` o un cross-link).
- **Cross-links relativos al archivo** (`../runbooks/smoke-test.md`) — funcionan en
  GitHub sin herramientas.
- `type` sale del perfil correcto (`Decision`/`Reference` en código, `Table`/`Metric`
  en datos, `Article`/`Playbook` en wiki); `tags` cruzan carpetas.
- Las `description` son una frase, listas para los `index.md`.
- Mismo formato, mismas reglas, tres dominios. Eso es OKF.
```
