# Conectar OKF a tu herramienta de IA (cualquiera)

OKF es **vendor-neutral**. Tres capas ya funcionan con cualquier herramienta, sin
adaptación:

- **El bundle `knowledge/`** — markdown plano; lo lee cualquier agente.
- **El git pre-commit hook + el CI** — enforcement a nivel git/server, no de un vendor.
- **El linter** `okf_lint.py` — Python stdlib.

Lo único que cambia por herramienta es **cómo te asegurás de que tu IA lea `AGENTS.md`**
(el contrato) y, opcionalmente, cómo hacés que los **procedimientos** (`okf-update`,
`okf-verify`…) se auto-disparen. El contenido de esos procedimientos es markdown
vendor-neutral: cualquier agente puede seguirlo aunque no tenga el mecanismo de "skills".

> **Regla de oro:** un solo source of truth (`AGENTS.md` + `knowledge/`). Los archivos
> por-herramienta son **punteros finos**, nunca copias — así no hay drift.

---

## Por herramienta

### Cualquier agente que lea `AGENTS.md` (OpenAI Codex CLI, etc.)
Ya lo lee. Nada que hacer. Los procedimientos se siguen leyéndolos desde el repo cuando
hagan falta (el contrato los nombra).

### Claude Code
- `CLAUDE.md` = una línea: `@AGENTS.md` (shim, no dupliques).
- Procedimientos → `.claude/skills/okf-*/` (auto-disparo por `description`).
- Enforcement → el **git hook** universal (recomendado), o un hook en `.claude/settings.json`.

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
