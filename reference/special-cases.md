# Casos especiales — monorepos, migración y escala

Los perfiles (`profiles.md`) cubren el caso típico: un repo, un bundle. Acá están
los casos de proyecto real que requieren decisiones extra.

---

## Monorepos: ¿un bundle o varios?

Depende de cuán independientes sean los paquetes.

**Un bundle raíz** (`knowledge/` en la raíz del monorepo) cuando los paquetes
comparten dominio, decisiones y vocabulario, y el contexto interesante es
transversal. Organizá por subsistema dentro del bundle:
```
knowledge/
├── architecture/overview.md        # cómo encajan los paquetes
├── decisions/                      # ADRs que afectan a todo el repo
├── packages/
│   ├── web/index.md
│   └── api/index.md
└── ...
```

**Un bundle por paquete** (`packages/<x>/knowledge/`) cuando los paquetes se
desarrollan, versionan o despliegan por separado y casi no comparten contexto.
Cada uno con su `AGENTS.md` local. Sumá un bundle raíz **chico** solo para lo
verdaderamente global (la arquitectura del monorepo, decisiones cross-cutting).

**Regla:** un agente que trabaja el paquete `api` debería encontrar su contexto sin
leer el de `web`. Si separar logra eso, separá. Si el contexto valioso es
transversal, centralizá. Evitá duplicar la misma verdad en dos bundles —linkeá.

**Entrypoint en monorepo:** un `AGENTS.md` en la raíz que apunta al bundle global y
lista dónde está el bundle de cada paquete; opcionalmente un `AGENTS.md` por paquete.

---

## Migrar desde un `AGENTS.md` / `CLAUDE.md` / ADRs existentes

Muchos repos ya tienen contexto disperso. No lo dupliques: **moverlo, no copiarlo.**
El skill **`okf-migrate`** (en `templates/skills/okf-migrate/`) automatiza este
procedimiento; lo de abajo es el detalle que ese skill ejecuta.

1. **Inventariá** lo que hay: `AGENTS.md`/`CLAUDE.md`/`.cursorrules`, `/docs`, ADRs,
   comentarios "tribales" en el README.
2. **Clasificá cada pieza** por dónde corresponde:
   - Reglas duras / "siempre/nunca" → se quedan en `AGENTS.md` (el índice).
   - Decisiones y su *por qué* → `knowledge/decisions/` (ADRs existentes se mueven
     casi tal cual; renombralos `NNNN-<slug>.md`).
   - Explicaciones de dominio, schema, procesos → la carpeta del perfil que toque.
   - Procedimientos operativos → `knowledge/runbooks/`.
3. **Reemplazá el original por un puntero.** Tras mover el contenido a `knowledge/`,
   dejá en el `AGENTS.md`/`CLAUDE.md` solo el índice + "el contexto vive en
   `knowledge/`". `CLAUDE.md` queda como shim `@AGENTS.md`.
4. **Regla anti-duplicación:** una verdad, un lugar. Si algo quedó en dos lados,
   borralo de uno y linkeá. Corré el linter para detectar links rotos tras mover.

> El objetivo no es agregar una capa más, es **consolidar** el contexto disperso en
> un solo lugar versionado y navegable.

---

## Escala: cuándo partir un bundle que creció

Síntomas de que un bundle pide refactor:
- Un `index.md` con **más de ~15-20 entradas** en una sola sección → agrupá en
  subcarpetas con sus propios `index.md`.
- Una carpeta `decisions/` con decenas de ADRs → sub-agrupá por subsistema
  (`decisions/auth/`, `decisions/billing/`).
- Un concepto que creció a varias pantallas y cubre varias ideas → partilo en
  conceptos enlazados (uno por idea).
- `AGENTS.md` que dejó de ser un índice y se volvió enciclopedia → mové el detalle a
  `knowledge/` y dejá el índice.

Para medir tamaños en tokens de forma objetiva (opcional, necesita Node), ver el
token-sizer en `reference/optional-tools.md`.

**No optimices de más.** Partí cuando duele (cuesta encontrar algo o el índice no
entra de un vistazo), no antes. El progressive disclosure existe para que el tamaño
total no importe mientras cada `index.md` siga siendo chico y navegable.

---

## Idioma (i18n)

Elegí **un** idioma para la prosa del bundle y sé consistente. Los `type` y los
headings convencionales (`# Schema`, `# Examples`, `# Citations`) se mantienen como
en la spec aunque la prosa esté en otro idioma — son palabras clave que los
consumidores reconocen. No mezcles idiomas dentro de un mismo bundle.
