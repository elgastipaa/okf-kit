# Desarrollar el kit OKF (proceso interno)

Esto es para quien **desarrolla el kit** (no para quien lo usa). Existe porque el kit se
construyó iterando y los defectos aparecían **reactivamente**; estas redes los hacen
salir **proactivamente**, antes de cada release.

## Antes de bumpear `VERSION` — gate de release

> **Al bumpear `VERSION`:** re-estampá `kit_version` en el dogfood `knowledge/index.md` para
> que coincida con el nuevo valor (el `okf_selfcheck` lo exige y falla si no). El dogfood es el
> bundle que el kit mantiene *current*; los repos destino, en cambio, conservan su `kit_version`
> *born-at* hasta re-correr una actualización.

1. **Meta-linter del kit (obligatorio):**
   ```
   python3 scripts/okf_selfcheck.py
   ```
   Valida la consistencia *interna*: el linter pasa limpio sobre el bundle dogfood
   `knowledge/`, `kit_version` no se "cae" en ejemplos/skills, el keep-alive coincide
   entre `AGENTS.md` y `okf-update`, y toda referencia `reference/*.md` resuelve. Exit 0
   = OK. (Es kit-only: vive en `scripts/`, no en `templates/`, así que no se instala en
   repos destino.)

2. **Linter sobre el dogfood:**
   ```
   python3 templates/scripts/okf_lint.py knowledge --strict
   ```
   El bundle `knowledge/` documenta al propio kit en formato OKF (dogfood). Debe dar 0/0.
   Si falla, el init no es self-sufficient — arreglalo antes de release.

3. **Cold-review de 4 lentes (para cambios grandes):** lanzar subagentes en frío,
   independientes y restringidos a `okf-kit`, con estas lentes:
   - **A — Consistencia:** matriz regla×archivo; ¿el mismo procedimiento coincide en
     todos los lugares donde se afirma? (caza la deriva, p.ej. el bug del index/log).
   - **B — Completitud:** ¿toda referencia/artefacto/flag documentado existe y coincide?
   - **C — Correctness:** correr los scripts/hook contra fixtures buenos/malos.
   - **D — Dogfood + foolproofing:** seguir solo el `GUIDE` en frío y registrar cada
     trampa/ambigüedad firsthand.
   Después sintetizar (matriz de trazabilidad + findings por severidad). Es el proceso
   que produjo la v0.4.0; usalo como gate antes de un minor/major.

## Principio anti-deriva

Una **fuente canónica por regla/procedimiento**; el resto **apunta**, no re-escribe
(el mismo principio "una verdad, punteros" que el kit predica, aplicado a sí mismo):
- Keep-alive (cómo agregar/actualizar un concepto): canónico = `AGENTS.md §2` (se instala)
  y `templates/skills/okf-update/SKILL.md`. `GUIDE §5` y `reference/maintaining.md` son punteros.
- Frontmatter (claves req/recomendadas + gotcha del `:`): canónico = `OKF-SPEC.md §3.1`.
- Criterio de FAIL del linter: canónico = el código de `okf_lint.py` + `reference/verification.md`.
- Versión del kit: canónico = `VERSION`; los templates usan el placeholder `{{KIT_VERSION}}`.

Si agregás una regla nueva, definila en UN lugar y apuntá desde el resto. El
`okf_selfcheck.py` debería crecer con un assert por cada regla que pueda derivar.

## El bundle dogfood `knowledge/`

`knowledge/` es el kit documentándose a sí mismo en OKF. Es prueba viva de que
el init funciona y, de paso, contexto navegable del propio kit. Mantenelo al día con
`okf-update` cuando el kit cambie (igual que cualquier repo OKF).
