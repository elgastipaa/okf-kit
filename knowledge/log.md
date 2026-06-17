# Update Log

## 2026-06-17
* **Update**: Auto-aplicado el enforcement del kit a sí mismo — CI (`.github/workflows/selfcheck.yml`) + pre-commit hook (`.githooks/`) que corren `okf_selfcheck`, y `CLAUDE.md` shim. Detalle en `DEVELOPING.md`.
* **Update**: v0.5.0 — cosechadas buenas prácticas de the-conclave: regla "gana el código", ciclo de deprecación (`status`/`supersedes`), patrón `_generated/`, header de frescura, `log.md` opcional, scratchpad; el linter ignora dirs con prefijo `_`.
* **Update**: Kit endurecido a v0.4.3 — revisión de 4 lentes + foolproofing; gate determinista (validador YAML stdlib, sin PyYAML); pre-commit hook seguro (sin `git stash`, no toca el working-tree); re-estampado `kit_version`.
* **Initialization**: Bundle OKF inicial creado con OKF kit v0.3.0 (de VERSION), dogfoodeando OKF sobre el propio kit.
* **Creation**: Sembrados los conceptos iniciales — `architecture/` (overview, modelo de tres capas), `concepts/` (bundle/concepto, progressive disclosure, perfiles, ciclo de vida), `decisions/` (0001 links relativos, 0002 consumo permisivo, 0003 kit_version vs okf_version, 0004 vendor-neutral, 0005 source of truth, 0006 perfil del dogfood), `runbooks/` (lint, cold test, bootstrap) y `references/` (formato OKF, Repomix).
