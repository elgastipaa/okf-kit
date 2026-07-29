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
   python3 scripts/okf_selfcheck.py        # el gate
   python3 scripts/okf_selfcheck_test.py   # ¿el gate falla cuando debe?
   ```
   Valida la consistencia *interna*: el linter pasa limpio sobre el bundle dogfood
   `knowledge/`, `kit_version` no se "cae" en ejemplos/skills, el keep-alive y la capa de
   futuro coinciden entre el contrato y los skills, la rama normativa no se cae, el
   contrato instalado entra en su presupuesto y **la instalación mínima no queda mencionando
   la capa de futuro**, el material instalado no cita rutas del kit, y toda referencia
   `reference/*.md` resuelve. Exit 0 = OK. (Es kit-only: vive en `scripts/`, no en
   `templates/`, así que no se instala en repos destino.)

   Además **instala de verdad** en un repo temporal (completa y mínima) y verifica la
   **salida**, no el template: que el linter la acepte en `--strict`, que no sobreviva
   ningún marcador ni `{{KIT_VERSION}}`, que `kit_version` == `VERSION`, y que la mínima no
   quede hablando de la capa de futuro. Y valida los manifiestos del plugin (versión ==
   `VERSION`, los `skills` resuelven, no ship**ea los procedimientos que van instalados).

2. **Manifiestos del plugin (si tenés el CLI a mano):**
   ```
   claude plugin validate .claude-plugin/marketplace.json --strict
   claude plugin validate .claude-plugin/plugin.json
   ```
   El segundo va **sin** `--strict` a propósito: avisa que el `CLAUDE.md` de la raíz no se
   carga como contexto del plugin, y ese archivo existe porque el kit se auto-aplica OKF
   (es su shim de entrypoint). Es un warning correcto para un plugin cualquiera y esperado
   para este. Lo estructural ya lo cubre el selfcheck, que corre sin el CLI.

3. **Linter sobre el dogfood:**
   ```
   python3 templates/scripts/okf_lint.py knowledge --strict
   ```
   El bundle `knowledge/` documenta al propio kit en formato OKF (dogfood). Debe dar 0/0.
   Si falla, el init no es self-sufficient — arreglalo antes de release.

4. **Cold-review de 4 lentes (para cambios grandes):** lanzar subagentes en frío,
   independientes y restringidos a `okf-kit`, con estas lentes:
   - **A — Consistencia:** matriz regla×archivo; ¿el mismo procedimiento coincide en
     todos los lugares donde se afirma? (caza la deriva, p.ej. el bug del index/log).
   - **B — Completitud:** ¿toda referencia/artefacto/flag documentado existe y coincide?
   - **C — Correctness:** correr los scripts/hook contra fixtures buenos/malos.
   - **D — Dogfood + foolproofing:** seguir solo el `GUIDE` en frío y registrar cada
     trampa/ambigüedad firsthand.
   Después sintetizar (matriz de trazabilidad + findings por severidad). Es el proceso
   que produjo la v0.4.0; usalo como gate antes de un minor/major.

## Enforcement automático (el kit se auto-aplica)

El gate de arriba no depende solo de la memoria del que desarrolla — está cableado:

- **CI** (`.github/workflows/selfcheck.yml`): corre `okf_selfcheck` en cada push y PR.
  Es la red en el server; habría cazado solas las regresiones que motivaron este doc.
- **Pre-commit hook** (`.githooks/pre-commit`): corre `okf_selfcheck` antes de cada commit
  local. Activalo una vez por clon con `git config core.hooksPath .githooks` (salteo de
  emergencia: `git commit --no-verify`).

Ambos corren el **gate propio del kit** (`selfcheck`), no el template genérico de `templates/`
(que asume el layout de un repo destino) — el kit se aplica a sí mismo con su propia herramienta,
igual que the-conclave usa su `wiki:check` y no un OKF importado.

## Principio anti-deriva

Una **fuente canónica por regla/procedimiento**; el resto **apunta**, no re-escribe
(el mismo principio "una verdad, punteros" que el kit predica, aplicado a sí mismo):
- Keep-alive (cómo agregar/actualizar un concepto): canónico = `AGENTS.md §2` (se instala)
  y `templates/skills/okf-update/SKILL.md`. `GUIDE §5` y `reference/maintaining.md` son punteros.
- Frontmatter (claves req/recomendadas + gotcha del `:`): canónico = `OKF-SPEC.md §3.1`.
- Criterio de FAIL del linter: canónico = el código de `okf_lint.py` + `reference/verification.md`.
- Versión del kit: canónico = `VERSION`; los templates usan el placeholder `{{KIT_VERSION}}`.
- Autoridad descriptivo/normativo: canónico = `OKF-SPEC.md §3.5` (+ el mapeo `type` → clase
  en `reference/profiles.md`). `GUIDE` y las `reference/` **apuntan**; el material que se
  instala (contrato, `okf-update`, `okf-verify`) la **enuncia**, a propósito — el repo destino
  no recibe la spec (ver [decisión 0013](knowledge/decisions/0013-installed-material-is-self-sufficient.md)).
  El selfcheck vigila que esas copias no pierdan la rama normativa.
- Capa de futuro (rumbo + `_changes/` + harvest): canónico = `templates/skills/okf-plan/SKILL.md`;
  el *cuándo* se dispara vive en `templates/AGENTS.md` (es lo que lee toda herramienta).
- Qué se borra del contrato en la instalación mínima: canónico = los **marcadores**
  `OKF:future-layer` del propio `templates/AGENTS.md` — el rango manda. Quien los **aplica**
  es `okf_install.py`; `GUIDE §4` explica el recorte a mano (para máquinas sin Python) y
  ninguno de los dos **enumera qué se borra**: eso lo dicen los marcadores. El selfcheck
  verifica que el resultado instalado no quede huérfano.
- **Procedimiento mecánico** de init/upgrade (qué archivo va a dónde, con qué nombre, con qué
  permisos, qué se sella): canónico = el código de `scripts/okf_install.py`. `okf-init` y
  `reference/upgrading.md` **delegan** — si vuelven a describirlo en prosa hay dos fuentes que
  derivan, y el selfcheck lo caza. Lo que esos docs **sí** dicen es lo que requiere criterio.

Si agregás una regla nueva, definila en UN lugar y apuntá desde el resto. El
`okf_selfcheck.py` debería crecer con un assert por cada regla que pueda derivar — y
**cada assert nuevo va con su caso en `okf_selfcheck_test.py`**: la rotura concreta que
debería cazar y, si puede dar falso positivo, la redacción legítima que NO debe romperlo.
Una revisión en frío encontró siete asserts que nunca fallaban (pasaban sobre archivos
borrados, se satisfacían desde comentarios que la instalación borra, o se contentaban con
dos substrings en un texto que negaba la regla). Un assert sin su rotura probada es
decoración.

## El bundle dogfood `knowledge/`

`knowledge/` es el kit documentándose a sí mismo en OKF. Es prueba viva de que
el init funciona y, de paso, contexto navegable del propio kit. Mantenelo al día con
`okf-update` cuando el kit cambie (igual que cualquier repo OKF).
