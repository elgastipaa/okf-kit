# Conectar OKF a tu herramienta de IA (cualquiera)

OKF es **vendor-neutral**. Tres capas ya funcionan con cualquier herramienta, sin
adaptación:

- **El bundle `knowledge/`** — markdown plano; lo lee cualquier agente.
- **El git pre-commit hook + el CI** — enforcement a nivel git/server, no de un vendor.
- **El linter** `okf_lint.py` — Python stdlib.

Lo único que cambia por herramienta es **cómo te asegurás de que tu IA lea `AGENTS.md`**
(el contrato) y, opcionalmente, cómo hacés que los **procedimientos** (`okf-update`,
`okf-verify`, `okf-plan`…) se auto-disparen. **Los disparadores que importan ya viven en el
`AGENTS.md`** (cuándo leer el rumbo, cuándo abrir un cambio, cuándo cosechar), así que una
herramienta sin skills no pierde el comportamiento: pierde el detalle del *cómo*, que el
agente puede leer del markdown del procedimiento. El contenido de esos procedimientos es markdown
vendor-neutral: cualquier agente puede seguirlo aunque no tenga el mecanismo de "skills".

> **Regla de oro:** un solo source of truth (`AGENTS.md` + `knowledge/`). Los archivos
> por-herramienta son **punteros finos**, nunca copias — así no hay drift.

## Qué tan fuerte es cada garantía (independencia del vendor)

Ninguna herramienta se puede *obligar* a obedecer una instrucción. Por eso el sistema no
apuesta todo a eso: hay tres capas, y las dos duras no dependen del vendor.

| Capa | Qué la hace cumplir | ¿Depende del vendor? |
|---|---|---|
| **Instrucción** — `AGENTS.md` (+ el puntero nativo de la herramienta) | Que el agente lo lea y lo siga | **Sí** — es un default fuerte, no una garantía |
| **Git** — pre-commit hook + CI | Corren en `git commit`/`push`, sin importar quién escribió el código (o si lo escribió un humano) | **No** |
| **Auditoría** — `okf-verify` + cold test + Nivel 4 (cumplimiento) | Se corre cada tanto y detecta lo que se escapó | **No** |

Corolario práctico: **si te importa que algo no se pierda, no lo dejes solo en la capa de
instrucción.** El hook y el CI son los que hacen que el sistema sobreviva a una herramienta
que ignoró el contrato, o a un commit hecho a mano.

## Canario: ¿tu herramienta está leyendo el contrato?

Antes de confiar en una herramienta nueva, preguntale en una sesión limpia:

> *"Sin buscar en el código: ¿qué dice el contrato de este repo que tenés que hacer antes de
> cerrar una tarea, y dónde vive el contexto del proyecto?"*

Si contesta el linter/harvest y `knowledge/`, lo está leyendo. Si duda o generaliza, **no lo
está leyendo**: revisá el puntero nativo de esa herramienta (abajo). Repetilo cuando cambies
de herramienta o de versión — el soporte de `AGENTS.md` se mueve rápido.

---

## Por herramienta

### Cualquier agente que lea `AGENTS.md` (OpenAI Codex CLI, etc.)
Ya lo lee. Nada que hacer. Los procedimientos se siguen leyéndolos desde el repo cuando
hagan falta (el contrato los nombra).

### Claude Code
- `CLAUDE.md` = una línea: `@AGENTS.md` (shim, no dupliques).
- Procedimientos → `.claude/skills/okf-*/` (auto-disparo por `description`).
- Revisor → `.claude/agents/okf-reviewer.md`: audita el bundle con **contexto fresco**, para que
  los niveles que revisan trabajo propio no se auto-aprueben. Sin subagentes, el mismo archivo
  se sigue como procedimiento en un proceso/CLI nuevo (es markdown vendor-neutral).
- Enforcement → el **git hook** universal (recomendado), o un hook en `.claude/settings.json`.
- **Bootstrap**: el kit se distribuye como plugin —
  `/plugin marketplace add elgastipaa/okf-kit` + `/plugin install okf@okf-kit` — que shippea
  `/okf-init` y `/okf-migrate`. **Solo ese par**: los procedimientos de mantenimiento
  (`okf-update`, `okf-verify`, `okf-plan`) se **copian al repo**, no vienen del plugin, para
  que quien clone el repo sin el plugin los tenga igual.

### Cursor
- Cursor lee `AGENTS.md`. Para reforzar, creá `.cursor/rules/okf.mdc` (con `alwaysApply`)
  que diga: *"Seguí el contrato de `AGENTS.md`. El contexto del proyecto vive en
  `knowledge/`; mantenelo al día (ver `okf-update`)."*
- Procedimientos: referenciá los `SKILL.md` como docs desde la regla, o pegá el contrato.

### GitHub Copilot
- `.github/copilot-instructions.md` → *"Seguí `AGENTS.md`. El contexto vive en `knowledge/`;
  actualizalo ante decisiones/cambios de schema."*

### Gemini CLI
- `GEMINI.md` → apuntá o importá `AGENTS.md`: *"Seguí las reglas de `AGENTS.md` y el
  contexto en `knowledge/`."*

### Otras (Windsurf, Cline, Roo, Aider…)
- Mismo patrón: el archivo de reglas/instrucciones nativo de la herramienta → un **puntero
  a `AGENTS.md`** + "el contexto vive en `knowledge/`". El enforcement universal (git hook
  + CI) cubre el resto sin importar la herramienta.

---

## Lo que NO hay que hacer

- **No copiar** el contenido de `AGENTS.md` en cada archivo de herramienta → drift garantizado.
  Apuntá, no copies.
- **No depender** de los skills de Claude para el núcleo: el contrato (`AGENTS.md`) y el
  enforcement (git hook + CI) hacen que el sistema funcione aunque la herramienta no tenga
  skills.
