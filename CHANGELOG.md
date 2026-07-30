# Changelog del kit OKF

Revisiones de **este kit de templates** (`okf-kit`). Formato basado en
[Keep a Changelog](https://keepachangelog.com/); versionado semver.

> **`kit_version` ≠ `okf_version`.** `okf_version` (ej. `0.1`) es la versión del
> **formato** OKF, fijada por `OKF-SPEC.md`. `kit_version` (ej. `0.1.0`) es la
> revisión de **esta guía + templates + tooling**. `okf-init` estampa el
> `kit_version` con el que se inicializó un repo en el `index.md` raíz del bundle y
> en su `log.md`, para que el repo sepa de qué revisión nació. La fuente de verdad
> de la versión es el archivo `VERSION`.

## 0.7.3 — Cuatro lentes en frío: pérdida de datos y veredictos falsos

Corrido el cold-review de 4 lentes sobre las tres releases del día (vibecoder en frío,
consistencia, adversarial de tooling, y mercado). Esta entrada cubre **solo lo destructivo y
los veredictos falsos**; el resto de los hallazgos está en el rumbo.

### Arreglado — el instalador destruía trabajo del usuario (BLOCKER)
Verificado sobre un repo real: instalar sobre un repo con `AGENTS.md` escrito a mano (con la
ubicación de los secretos y el procedimiento de deploy), un `CLAUDE.md` propio y un
`pre-commit` con `lint-staged && npm test` **los sobreescribía los tres, exit 0, sin backup y
sin mención** — irrecuperable si no estaban commiteados.

- Ahora **aborta** (exit 2) si hay un `AGENTS.md`/`CLAUDE.md` que no es del kit, y rutea a
  `okf-migrate`, que existe justamente para ese repo. `--force` para reemplazarlo a propósito.
- El `pre-commit` ajeno **no se pisa nunca**, ni con `--force`: la guarda `_hook_is_ours()` ya
  existía y solo se consultaba en `--upgrade`. Pisarlo apaga los tests del usuario en silencio.
- La guarda anti-auto-instalación era igualdad exacta, así que `okf-kit/reference` era un
  destino válido: ahora rechaza cualquier anidamiento con el kit.

### Arreglado — `okf_coldtest.py --force` hacía `rm -rf` del repo (BLOCKER)
`--force` estaba documentado como "sobreescribe el destino" y ejecutaba `shutil.rmtree(dest)`
sin mirar qué era: apuntarlo al repo borraba el código y el **`.git`**, y después crasheaba, así
que el stacktrace hacía creer que no había pasado nada. Ahora se niega si el destino contiene al
bundle, está adentro del bundle, es el cwd, tiene un `.git/`, o tiene archivos que no puso él.

### Arreglado — el gate MENTÍA (BLOCKER)
- **Con `templates/scripts/okf_lint.py` vacío, el gate declaraba `104/104 OK`.** Solo miraba el
  returncode, y un linter vacío sale 0. Ahora corre el linter contra una **rotura conocida** y
  exige que la detecte: se prueba que funciona, no que calla.
- **Borrar material instalado bajaba el denominador** (104 → `102/102 OK`) porque `INSTALLED` se
  armaba con un glob de lo que existe. Ahora es un **inventario literal**, más un assert de que
  no quede en disco un template sin sus asserts. Viola la regla de diseño 1 del propio archivo:
  un archivo que falta tiene que FALLAR, no desaparecer del reporte.
- `AGENTS.md` §3 nombraba dos suites; el CI corre cuatro. Ahora dice las cuatro.

### Arreglado — el linter daba verde a bundles inválidos
- **`type:concept` (sin espacio) contaba como la clave `type`.** Para cualquier parser YAML ese
  frontmatter es **un solo escalar**: no tiene ninguna clave. El linter bendecía conceptos que
  GitHub u Obsidian leen sin metadata, y `type` es el único requisito duro de OKF.
- **Marcadores de conflicto de merge pasaban limpios** — por el linter, por `--strict` y por el
  hook. Es el estado más peligroso que puede tener un bundle: deja dos verdades contradictorias
  afirmadas como vigentes. Ahora es ERROR.
- **Un link absoluto indentado con 4 espacios era invisible** (se trataba como code-block, pero
  `    * item` es una lista anidada). El link absoluto es el único ERROR de links de la spec, y
  se esquivaba indentando.

### Arreglado — falsos positivos que habrían puesto en rojo la CI de los usuarios
- La `description` de una entrada de índice **envuelta en dos líneas** (envolver prosa a 90
  columnas es la norma, y los docs del kit lo hacen) se marcaba como divergente, mostrando los
  dos textos **idénticos** en el mensaje. Regresión del chequeo nuevo de 0.7.1.
- `authority: normative # comentario` se marcaba como fuera del vocabulario.

### Arreglado — dos herramientas del kit se contradecían
`okf_lint.py` acepta `timestamp: 2026-01-01` (sin offset) como ISO 8601 válido — la forma que un
humano escribe primero — y `okf_stale.py` **crasheaba con `TypeError`** al restarlo de un `now`
con timezone: un solo concepto se llevaba el reporte entero. Nunca salió en casa porque el
dogfood usa `Z` en el 100% de los conceptos.

### Arreglado — el hook se auto-desactivaba en silencio
Si `mktemp` fallaba (TMPDIR inválido, disco lleno, sandbox de CI), quedaba `tmp=""` y el
`--prefix="/"` intentaba escribir el bundle en la **raíz**; el chequeo bloqueante desaparecía sin
una línea de aviso, al revés que la rama sin python3, que sí avisa. Ahora avisa.

Gate: 104 → **108 asserts**, 47 → **52 roturas**, 15 → **20 casos del linter**, 8 → **9 del ranker**.

## 0.7.2 — La auditoría del bundle deja de auto-aprobarse

### Agregado — `okf-reviewer`: el revisor con contexto fresco
`okf-verify` tiene cuatro niveles. El **Nivel 3** ya exigía contexto fresco y lo decía. Pero los
**Niveles 2** (drift descriptivo) y **4** (cumplimiento) los corría **la misma sesión que escribió
los conceptos y el código** — los dos donde el sesgo pesa más: el método del Nivel 2 es *"buscá la
contradicción"*, y quien redactó el concepto lo lee sabiendo lo que quiso decir; el Nivel 4 audita
si el código viola lo normativo, y quien lo escribió racionaliza.

**No es una apuesta nueva: es la práctica que el kit ya usaba para desarrollarse y no le daba a
sus usuarios.** El cold-review de 4 lentes de `DEVELOPING.md` tiene acreditados 2 blockers y ~12
majors en una sola pasada, y era kit-only.

Tres propiedades hacen el mecanismo, y ninguna es opcional:
1. **Contexto fresco** — y prohibido pedir la intención del autor: si le falta info para juzgar,
   *ese* es el hallazgo.
2. **No puede editar** (`disallowedTools` + el cuerpo). Un revisor que arregla lo que encuentra
   vuelve a ser el autor: la asimetría **es** el mecanismo.
3. **Consigna refutatoria**, con una sección obligatoria *"lo que intenté refutar y no pude"*:
   sin eso, un reporte vacío no se distingue de una auditoría que no se hizo.

Vendor-neutral: sin subagentes, el mismo archivo se sigue en un proceso/CLI nuevo (la salida que
el Nivel 3 ya usaba). Se instala **en el repo destino**, no lo shippea el plugin
([0013](knowledge/decisions/0013-installed-material-is-self-sufficient.md) +
[0018](knowledge/decisions/0018-plugin-shippea-solo-el-bootstrap.md)).
Decisión [0021](knowledge/decisions/0021-la-auditoria-no-se-auto-aprueba.md).

**El contrato `AGENTS.md` no creció ni un carácter** — está al 95% de su presupuesto, y esto es un
detalle de implementación de `okf-verify`. El modelo sigue siendo de tres capas: no se agregó una
de orquestación, se agregó un *ejecutor* para dos niveles de un procedimiento que ya existía.

### Arreglado — un skill pedía a mano algo que el script ya hace
El Nivel 1 de `okf-verify` decía *"la raíz lista todos los subdirs (el script todavía no lo
valida — chequealo acá)"*. En 0.7.1 el linter empezó a validarlo: el skill instalado quedó
pidiendo trabajo pagado dos veces.

### No-goals nuevos (decididos, no pendientes)
- **Los otros tres roles de `harness-sdd`** (leader / spec_author / implementer): ceremonia de
  equipo grande, sin evidencia de que paguen para un usuario solo.
- **Un harvester con contexto fresco:** el harvest necesita *recordar* qué pasó, y eso lo tiene la
  sesión que hizo el trabajo (para eso existe el staging del doc de `_changes/`). Contexto fresco
  sirve para auditar, no para recordar — lo pensamos y da peor.

Gate: 97 → **104 asserts**, 41 → **47 roturas probadas**.

## 0.7.1 — Pasada de optimización, hecha con las propias herramientas del kit

Se corrió `okf_stale.py` sobre el dogfood, se midió el bloat en vez de estimarlo y se cerraron
los tres gaps del linter que el roadmap arrastraba desde el cold-review de 0.6.0.

### Agregado — el hook previene el sello podrido
`okf_stale.py` encontró **tres conceptos editados en 0.7.0 sin bumpear su `timestamp`**. No es
cosmético: el ranker calcula *todas* sus señales desde ese valor, así que un sello podrido
degrada la detección de drift del bundle entero — y la señal se deterioraba **sola** con el uso.
El hook instalado gana una tercera función: **avisa** (no bloquea) si un concepto staged cambió
con su `timestamp` igual al de `HEAD`. Se juzga lo staged, no el working tree.
Decisión [0020](knowledge/decisions/0020-el-sello-se-enforcea-en-el-commit.md).

### Agregado — los tres chequeos que el linter no hacía
- **`authority:` con vocabulario cerrado** (`normative | descriptive`). Hasta ahora
  `authority: banana` pasaba `--strict` en silencio: una clave que se escribe y nadie lee.
- **Subcarpeta ausente del `# Subdirectories` del padre.** Se podía agregar un subárbol entero
  **invisible** para quien navega desde el entrypoint.
- **Entrada de `index.md` que divergió de la `description` del concepto.** El índice es lo
  primero que lee un agente; si su resumen dice otra cosa, lo rutea mal. Encontró **tres
  divergencias reales en el dogfood** (una de ellas era una `description` que narraba el cambio
  en vez de describir el estado) y un **bug del instalador**: sembraba dos placeholders
  distintos para la misma frase, o sea divergencia por construcción.

### Agregado — `scripts/okf_lint_test.py` (15 casos)
El linter es la herramienta más usada del kit —CI, pre-commit hook y `okf-verify`— y era la
única sin test de roturas: el gate y el ranker ya tenían el suyo. Cada caso inyecta **una**
rotura y verifica que el reporte falle **por ese motivo** (no alcanza con que falle); los casos
limpios prueban que la redacción legítima no se marque. Corre en CI.

### Cambiado — el fallback manual sale del GUIDE
Los pasos mecánicos del init (estructura, `index.md`, `log.md`, entrypoint, tooling) se movieron
a **`reference/manual-install.md`**, que existe para un solo caso: la máquina no tiene Python.
El `GUIDE` baja de **27.4K a 21.3K chars (−1546 tokens en cada init)** y queda con lo que
requiere criterio: sembrar el bundle y verificar. Era el propio `GUIDE` violando la divulgación
progresiva que el kit predica.

### Arreglado — deriva de numeración, y el instrumento de medición
- **Tres referencias a "Paso N" del `GUIDE` apuntaban al paso equivocado** (numeración vieja:
  mandaban al Paso 3 para el entrypoint, que era el 5). La numeración frágil de §4 se eliminó:
  los dos pasos que quedan no se referencian por número.
- El corte "mecánico vs criterio" estaba enumerado en **tres** lugares, dos de ellos mal.
  Ahora se dice una sola vez.
- **`run-eval.py` reportaba `input_tokens`** (6–12: los tokens **no cacheados** del último
  turno, puro ruido) en vez de **`cache_read`** (85K–300K: el contexto realmente leído). El dato
  ya se capturaba; la tabla y el resumen miraban la columna equivocada. Es el instrumento con el
  que se decide si un cambio de contexto paga, así que medía mal toda comparación antes/después.
- Los tres sellos podridos del dogfood, y las tres entradas de índice divergentes.

### Medido — dónde está (y dónde no está) el bloat
- **Duplicación literal entre docs: 2 frases en todo el kit**, ambas intencionales (la
  [0013](knowledge/decisions/0013-installed-material-is-self-sufficient.md) obliga a que el
  material instalado se repita). El kit está bien factoreado en ese eje.
- **El contrato instalado está al 95% de su presupuesto** (6692/7000 chars ≈ 1673 tokens *por
  turno*), con **77 tokens de headroom**. Queda anotado como restricción de diseño: una mejora
  nueva tiene que costar cero en el contrato, o hay que recortar antes.

Gate: 96 → **97 asserts**, 39 → **41 roturas probadas**, más los 15 casos del linter.

## 0.7.0 — La plomería deja de gastar criterio, y el kit se distribuye

### Agregado — `scripts/okf_install.py`: el init mecánico en un comando
El kit resolvía bien el problema difícil (qué contexto capturar y por qué) y mal el fácil
(copiar archivos). `okf-init` le pedía a una IA ~40 operaciones de archivo, de las cuales
**una sola requiere inteligencia**: sembrar los conceptos. El resto —`mkdir`, `cp`, `chmod`,
sellar `{{KIT_VERSION}}`, borrar los bloques entre marcadores, renombrar los tres `SKILL.md`
que se llaman igual, dejarlos fuera de `knowledge/` para que el linter no los rechace— estaba
**explicado en prosa** porque no había código que lo garantizara: se pagaba en tokens en cada
init y se podía ejecutar mal.

- **Un comando:** `python3 scripts/okf_install.py <repo> --profile codigo --name "X"`.
  Flags: `--minimal`, `--no-claude`, `--no-ci`, `--no-hook`, `--upgrade`, `--dry-run`.
- **Verifica su propia salida** con el linter en `--strict` y **lista lo que falta**, que es
  exactamente lo que requiere criterio: sembrar conceptos y completar `{{placeholders}}`.
- **No pisa** un `knowledge/` existente: aborta y rutea a `--upgrade`.
- `--upgrade` **es** ahora el camino mecánico de `reference/upgrading.md` (pasos 3 y 5):
  reemplaza scripts/skills/CI/hook, detecta solo el nivel de instalación, re-estampa
  `kit_version`, deja la línea en `log.md`, y **no toca `AGENTS.md`** ni el contenido del
  bundle — el merge del contrato sigue siendo criterio del agente. Un `pre-commit` que no es
  del kit tampoco se pisa.
- **Una verdad, un lugar:** `okf-init` **delega** en el script en vez de re-statear la
  plomería, y un assert del gate verifica que no vuelva a describirla. Era el riesgo real de
  esta feature (dos fuentes del mismo procedimiento = la causa raíz de los bugs del kit).
- Sigue valiendo la [decisión 0004](knowledge/decisions/0004-vendor-neutral-no-external-apps.md):
  stdlib, sin `pip`, y el camino manual del `GUIDE` §4 sigue existiendo para máquinas sin Python.

### Agregado — distribución como plugin de Claude Code
`/plugin marketplace add elgastipaa/okf-kit` + `/plugin install okf@okf-kit` deja `/okf-init`
y `/okf-migrate` sin clonar nada a mano. El plugin **es este repo** (`"source": "./"`) y
apunta a `templates/skills/` con rutas custom: **no copia skills**, así que no hay dos copias.
Shippea **solo el par de bootstrap** — `okf-update`/`okf-verify`/`okf-plan` se siguen copiando
al repo destino, porque quien clone ese repo sin el plugin tiene que seguir teniéndolos
([decisión 0013](knowledge/decisions/0013-installed-material-is-self-sufficient.md)).

### Agregado — licencia (bloqueante de adopción) y puerta de entrada en inglés
- **`LICENSE` (Apache-2.0) + `NOTICE`.** No había ninguna: legalmente nadie en una empresa
  podía adoptarlo. Apache-2.0 y no MIT porque el `OKF-SPEC.md` es un derivado condensado del
  OKF de Google Cloud, que es Apache-2.0 — el `NOTICE` acredita el upstream y declara qué se
  cambió, como pide esa licencia.
- **`README.en.md`**: qué es, cómo se instala y el modelo mental, en inglés. La prosa del kit
  sigue en español a propósito; cualquier agente traduce el resto bajo demanda.

### Arreglado — dos bugs latentes que el instalador destapó
Los encontró el linter corriendo sobre la salida real del init, algo que hasta ahora nadie
hacía (todos los asserts medían el **template**):

- **`_roadmap.md` tenía un `description` con `:` sin comillas** → un `roadmap.md` sembrado
  desde el template daba **ERROR** de YAML en el linter. Igual en `_change.md`. Ahora van
  entrecomillados.
- **El ejemplo de "Ahora" del `_roadmap.md` linkeaba un `_changes/` inexistente** → link roto
  el día uno. El instalador lo reemplaza por `- (nada activo)`, que además es la verdad.

### Cambiado — el gate crece sobre la salida, no sobre el template
`okf_selfcheck.py`: 80 → **96 asserts**. Los nuevos **instalan de verdad** en un repo temporal
(completa y mínima) y verifican el resultado: linter en `--strict`, cero marcadores
sobrevivientes, cero `{{KIT_VERSION}}`, `kit_version` == `VERSION`, y que la instalación mínima
no quede nombrando la capa de futuro ni instalando `okf-plan`. Más los manifiestos del plugin
(versión == `VERSION`, los `skills` resuelven, no ship**ea lo que va instalado en el repo).
`okf_selfcheck_test.py`: 22 → **39 casos** de rotura probada.

### Arreglado — pasada en frío sobre el `GUIDE` (sin blockers, 5 majors)
Un agente sin contexto caminó la guía entera sobre un repo de juguete y llegó al final solo:
linter limpio a la primera, hook funcionando, Nivel 3 con 6/6 + trampa. Lo que trajo son
puntos donde **tuvo que adivinar**, que es lo que la verificación mecánica no puede ver:

- **El paso que dice "no interpretes prosa, es mecánico" mandaba a editar el kit.** El
  borrado del nivel mínimo decía "en `templates/AGENTS.md`…" — o sea los archivos que el
  Paso 0 prohíbe tocar en mayúsculas 90 líneas antes. Ahora dice explícitamente que se hace
  sobre **las copias ya en el repo destino**.
- **El criterio init-vs-migrate no cubría el caso más común**: un repo con `README`
  sustancioso y cero artefactos de IA no es "contexto disperso abundante" ni "limpio". Es la
  primera decisión irreversible del flujo y era la peor especificada. Ahora hay regla de
  corte: si lo único que hay es el `README`, es **init**.
- **El harness del Nivel 3 fabricaba un falso positivo.** `okf_coldtest.py` excluye `_*` a
  propósito (una spec activa es normativa sobre el futuro), así que el link obligatorio del
  roadmap queda colgado y el agente en frío lo reporta como defecto — y el `GUIDE` manda
  tratar cada hallazgo del Nivel 3 como concepto faltante. Ahora el script avisa qué excluyó.
- El bloque `cp … <repo>/docs/okf/…` no era ejecutable (faltaba `mkdir -p`), y la pregunta de
  "cuánto instalar" no decía qué hacer **si no hay usuario que conteste**.
- Menores: "todos los subdirectorios" incluía literalmente `_changes/`; el enumerado de "borrá
  lo que no instalaste" cubría 2 de 4 casos; el techo de 7000 chars decía "el gate lo verifica"
  cuando en el repo destino no hay tal gate; el `{{KIT_VERSION}}` del `log.md` solo se
  mencionaba en el skill; el hook imprimía el output del linter **en cada commit limpio**
  (ahora solo habla cuando algo falla).

## 0.6.2 — 2026-07-26

### Agregado — el drift se rankea antes de auditarlo
`okf-verify` ya tenía con qué cazar la divergencia bundle↔código (Nivel 2 descriptivo,
Nivel 4 de cumplimiento, con la regla de que **el usuario decide** si el bug es el código o
el documento), pero no se usaba — y no por ignorancia: **auditar el bundle entero es caro**,
el Nivel 2 no tenía método, y nada los dispara.

- **`templates/scripts/okf_stale.py`** (nuevo, se instala): convierte "revisá todo, alguna
  vez" en una lista corta y ordenada, con git + el frontmatter que el bundle ya tiene, **sin
  leer código ni gastar tokens**. Tres señales: `resource:` que ya no existe (drift
  confirmado), `timestamp` anterior al último commit del propio concepto con ≥2 commits (el
  sello de frescura está podrido), y churn de la fuente desde el timestamp. **No es un gate**:
  el linter dice "¿es OKF válido?", esto dice "¿por dónde empiezo?". `--rotate` mueve por
  semana la ventana de los conceptos sin `resource`, para que los más viejos no tapen al resto.
- **El Nivel 2 gana método**, espejando el del 4: rankear → buscar la **contradicción** y no
  la confirmación → clasificar → reportar sin resolver solo.
- **Del rumbo se audita solo "Ahora".** Visión, "Después" y no-goals son intención pura;
  auditarlos sería puro falso positivo. Pero "Ahora" afirma estado del código.
- Encontró drift real en su primera corrida sobre el propio kit: un runbook desalineado del
  `GUIDE` y 5 conceptos con el sello podrido. Decisión `0015`.

### Agregado — camino de ACTUALIZACIÓN (el material instalado dejaba de recibir mejoras)
El kit tenía camino de instalación y no de actualización: `okf-update` mantiene el
**contenido** del bundle pero no puede tocar el `AGENTS.md`, los skills ni los scripts —
corre sin el kit en disco. Dos repos reales corrían `kit_version: 0.5.0` sin nada de 0.6.x.
**El bug era de ruteo:** `okf-init` detectaba el bundle existente y mandaba a `okf-update`.

- **`reference/upgrading.md`** (nuevo): la distinción que faltaba —contenido del bundle (del
  proyecto, no se toca) vs material instalado (del kit, se reemplaza)— y el procedimiento. El
  `AGENTS.md` es el único con contenido mezclado y por eso el único que no se reemplaza entero.
- `okf-init` compara `kit_version` contra `VERSION` y rutea ahí; `GUIDE` Paso 0 gana el tercer
  camino (init / migrate / **upgrade**).
- **`kit_version` pasó de decorativa a disparador.** Tercera clave escrita-y-nunca-leída del
  kit, después de `resource:`. De ahí la regla: **cuando el kit agrega una clave, hay que
  decir quién la lee.** Queda `authority:`, en el rumbo. Decisión `0016`.
- Probado subiendo un conejillo real de 0.5.0 a 0.6.1: **no se rompió nada**.

### Cambiado — el gate: 74 → 80 asserts, y un test nuevo
- `scripts/okf_stale_test.py`: 8 casos que verifican las dos mitades — encuentra el drift
  sembrado, y **sobre un bundle limpio no inventa**. Corre en CI. Un detector con falsos
  positivos se deja de correr en dos semanas, que es cómo el Nivel 4 llegó a no correrse.
- El test de inyecciones volvió a pagar: encontró que un assert propio era **demasiado débil**
  (chequeaba la mitad de exclusión de una regla y no la de inclusión) y que `near()` fallaba
  con texto envuelto a 90 columnas, lo que afectaba a **todos** los asserts de texto.

## 0.6.1 — 2026-07-26

### Medido — la capa de futuro, con su condición y su resultado negativo
Primera medición real (dos repos conejillo, n=3 por pregunta, todas las respuestas leídas a
mano y sus afirmaciones verificadas contra el código). Decisión `0014`:

- **Paga, con una condición.** Con un roadmap **vigente y auto-contenido**, "¿qué sigue?" cae
  de **12.3 a 4.0 turnos** y de 337K a 93K de contexto; los rangos no se solapan y la variante
  con capa tiene dispersión **cero**. El **harvest se corre solo** y —lo más fuerte— **verifica
  en vez de creerle al usuario**: corrió los smokes antes de cerrar y renegoció explícitamente
  los puntos del spec que la realidad no cumplía.
- **Un roadmap desactualizado cuesta más que no tener roadmap** (resultado negativo). En el
  segundo conejillo el rumbo afirmaba trabajo en curso que la fuente daba por terminado: los
  agentes gastaron turnos corrigiéndolo (hasta 22 en una corrida) y la rama **sin** roadmap
  encontró mejor información. Un rumbo que solo **rutea** tampoco compra el ahorro: la mejora
  viene de que sea **una respuesta**, no un índice.
- El roadmap entra al ciclo de frescura como cualquier concepto, y la doc de interop deja de
  vender el ahorro de retrieval cuando el repo ya tiene su propia capa de planes.


### Cambiado — el disparador de scope creep chequea si la idea ya existe
Primera medición de la capa de futuro (cambio `0001`, conejillo `idlerpg`). El resultado
principal es positivo —las preguntas de rumbo bajan de 9→4 y 10→6 turnos, y el contexto
leído cae ~60%— pero destapó un modo de falla que solo aparece **con** la capa instalada:

- Ante "agregá logros" a mitad de otra tarea, el agente aplicó el disparador correctamente
  (no lo implementó, lo anotó en "Después") pero **nunca miró el código**: describió los
  logros como *feature nueva* en un repo con **52 ya implementados**, y escribió esa premisa
  falsa **dentro del roadmap**, donde queda como contexto de las sesiones siguientes. El
  mismo agente **sin** la capa había contestado bien. El disparador lleva a *anotar*, y
  anotar es escribir contexto: la capa puede **fabricar** contexto falso.
- Fix: el disparador exige **chequear si ya existe en el código** antes de anotar, en el
  contrato y en `okf-plan` (con la evidencia medida, porque la razón importa más que la
  regla). Re-medido 3/3: detecta los 52 logros, no los implementa, no los anota, y sigue
  reportando el cambio activo. No cuesta turnos.
- `okf_selfcheck.py`: assert nuevo (+ su caso de rotura en `okf_selfcheck_test.py`) para que
  la regla no se caiga.

### Arreglado — `run-eval.py` distinguía "midió 0" de "falló"
Devolvía `{}` ante cualquier fallo de `claude` y nunca miraba el `returncode`: una corrida
que fallaba entera producía un scorecard de ceros con exit 0. En un harness de medición ese
es el peor bug posible — emite números que parecen datos. Ahora el fallo se propaga, se ve
el error real, los promedios se calculan solo sobre las corridas que corrieron, y el script
sale con 1 avisando que el scorecard no es una medición válida.

## 0.6.0 — 2026-07-26

### Agregado — la capa de FUTURO (rumbo + cambios con harvest)
Hasta acá el kit ordenaba el pasado (`decisions/`, log) y el presente (los conceptos),
pero excluía el trabajo futuro — el nicho de spec-driven development (OpenSpec y
similares), y justo lo que un proyecto "vibecodeado" más necesita para no perder el
rumbo. Se incorpora una versión liviana y nativa, sin tooling nuevo:

- **`knowledge/roadmap.md`** (template `_roadmap.md`, `type: Roadmap` en el núcleo
  universal de `profiles.md`): la **intención vigente** — visión, "Ahora", "Después",
  no-goals. Es un concepto normal (estado presente *de la intención*); se edita, sin
  checkboxes.
- **`knowledge/_changes/NNNN-<slug>.md`** (template `_change.md`): un doc **efímero por
  cambio no trivial** — mini-spec (por qué, resultado esperado, fuera de alcance),
  tareas con checkboxes, decisiones staging. El linter lo ignora (prefijo `_` ya
  existente); nace antes de codear y **muere en un harvest** al bundle, tras lo cual se
  borra (git guarda la historia).
- **Skill `okf-plan`** (vendor-neutral, se instala en el repo destino): los cinco
  disparadores (primer mensaje de la sesión / pedido de cambio / "¿qué sigue?" / cierre con
  harvest / idea fuera de alcance → "Después"), el umbral de trivialidad, el límite de ~3
  cambios activos y las reglas anti-zombie.
- **Spec §3.4 aclarada** (resolvía una tensión previa): la intención vigente (roadmap)
  SÍ es estado presente y puede ser concepto; el plan/progreso de un cambio concreto NO
  — vive en `_changes/`. §2 suma `_changes/` a los ejemplos de prefijo `_`.
- Integrado en el resto del sistema: `GUIDE.md` (árbol, siembra del roadmap preguntando
  al usuario, tercer skill en el Paso 6), `templates/AGENTS.md` (rumbo/en-curso en §1,
  harvest en §3, `okf-plan` en Procedimientos), `okf-init`/`okf-migrate` (los TODOs y
  roadmaps existentes se triagean hacia la capa) /`okf-update` (puntero), `maintaining.md`
  (señal anti-rot: cambios zombie), README.
- **`okf_selfcheck.py`**: nuevos asserts de consistencia — contrato, skill `okf-plan` y
  template `_change.md` describen la misma capa (rumbo + `_changes/` + harvest), y el kit
  **se auto-aplica** la capa (su `AGENTS.md` rutea a `roadmap.md`/`_changes/` y el dogfood
  tiene su roadmap).
- Dogfood: decisión `0011-future-work-layer` + `knowledge/roadmap.md` + el primer cambio
  real del kit en `knowledge/_changes/` (validar la capa midiendo en los conejillos del
  eval — criterio reactivo de la 0010).

### Agregado — cosechado de la comparación con OpenSpec (spec-driven development)
Se revisó [OpenSpec](https://github.com/Fission-AI/OpenSpec) para ver qué de su filosofía
aplicaba. Se tomaron **cinco ideas** —enumeradas como tales en
`reference/spec-driven-interop.md`— sin tomar la herramienta ni su ceremonia. Lo que
cambiaron en el kit:

- **`reference/spec-driven-interop.md`** (nuevo): en qué difiere OKF de las herramientas
  SDD, qué se adoptó, qué se descartó a propósito (deltas `ADDED/MODIFIED/REMOVED`,
  `changes/archive/`, specs vivas por capability) y **cómo convivir** con OpenSpec en el
  mismo repo sin montar dos dueños del trabajo en curso.
- **Descriptivo vs normativo** (decisión `0012`, y el gap más importante que destapó la
  comparación): "gana el código" aplica a los conceptos; el *Resultado esperado* de un
  cambio **activo** es normativo — si el código no lo cumple, el trabajo no está terminado,
  y bajar la vara se renegocia con el usuario, no se asume. La autoridad caduca en el
  harvest. Reflejado en `OKF-SPEC.md` §3.5, `templates/AGENTS.md` y `okf-plan`.
- **Escenarios `CUANDO … ENTONCES …`** en el "Resultado esperado" del template `_change.md`
  (incluyendo el caso que falla), para que "hecho" sea chequeable en vez de opinable.
- **Explorar antes de comprometer** y **right-sizing** del cambio (una intención que se dice
  en una frase, + señales de cambio sobredimensionado) en `okf-plan`.
- **No planificar de más:** specs de trabajo hipotético se pudren porque nada las obliga a
  seguir la realidad — el trabajo no arrancado es *una línea* en "Después" del roadmap, no
  una spec (`okf-plan`, `GUIDE.md`).

### Cambiado — el disparo es automático: el usuario nunca nombra un procedimiento
El riesgo de adopción más serio de la capa de futuro era que dependiera de que el usuario
recordara pedir "okf-plan" — con el público objetivo (gente que desarrolla conversando, no
ingenieros), eso equivale a que no se use. Los **disparadores se movieron al `AGENTS.md`**,
que lee toda herramienta, en vez de vivir solo en el skill (que solo existe en Claude Code):

- El contrato ahora lista **cuándo actuar sin que se lo pidan**: primer mensaje de la sesión
  (continuidad: "venías con X, quedó en Y"), pedido no trivial (acordar el "listo" antes de
  codear), pregunta de rumbo, cierre con harvest, idea fuera de alcance → "Después".
- **Regla nueva "hablale al usuario en su idioma, no en OKF"** (contrato y `okf-plan`): no
  anunciar archivos ni metodologías, preguntar en concreto ("¿cómo te das cuenta de que
  quedó bien?"), una o dos preguntas y no un cuestionario, y **respetar** al usuario que
  pide ir directo al código. La metodología tiene que ser invisible.
- `okf-plan` suma el disparador 0 (primer mensaje de sesión) y una sección de cómo
  conversarlo; `GUIDE.md` e `install-per-tool.md` aclaran que **sin skills el sistema sigue
  funcionando** (el contrato trae el *cuándo*; el skill solo agrega el *cómo*).
- El template `AGENTS.md` avisa qué secciones borrar si no se instaló la capa de futuro o el
  linter (evita mandar al agente a archivos que no existen).

### Agregado — presupuesto del contrato y niveles de instalación
`AGENTS.md` es lo único que se carga en **cada turno de cada sesión**, así que su tamaño es
el costo permanente del sistema (y un contrato largo se skimea: pierde obediencia). Al medirlo
se detectó que las adiciones de esta versión lo habían inflado ~66%; se recortó sin perder
comportamiento y se cableó el límite:

- Contrato **instalado**: ~1600 tokens (era ~1178 antes de esta versión; llegó a ~2260 antes
  del recorte; el valor exacto lo imprime el `okf_selfcheck`, no se transcribe a mano). El
  delta paga la regla normativa, los disparadores del rumbo y la regla de hablarle al
  usuario en su idioma.
- **`okf_selfcheck.py`**: assert nuevo de **presupuesto** — el contrato instalado no puede
  superar los 7000 chars. "Mantenelo chico" pasó de consejo a chequeo.
- **Dos niveles de instalación** documentados en `GUIDE.md` §1: **completo** (~1600 tokens,
  con capa de futuro) y **mínimo** (~1300, sin ella — pasado + presente, sin ceremonia previa
  a codear), con instrucciones de qué borrar y cómo subir de uno a otro después.
- **`reference/install-per-tool.md`**: tabla de **qué tan fuerte es cada garantía** (instrucción =
  default fuerte y dependiente del vendor; git hook + CI y auditoría = independientes del
  vendor), con el corolario "si te importa que no se pierda, no lo dejes solo en la capa de
  instrucción"; más un **canario** de una pregunta para comprobar si una herramienta nueva
  está leyendo el contrato.

### Cambiado — la autoridad frente al código ahora depende del tipo de documento
El agujero que destapó la comparación era más grande que la capa de futuro y tocaba el
corazón del bundle: bajo "gana el código" sin tipos, **código que viola un ADR aceptado
convertía al ADR en el bug** — o sea, el kit instruía a borrar en silencio la razón por la
que alguien decidió algo. Corregido:

- **`OKF-SPEC.md` §3.5** (nueva, fuente canónica): dos clases de documento y en qué
  dirección corre la autoridad. **Descriptivo** (default: arquitectura, schema, dominio,
  runbooks, references, glosario) → gana el código. **Normativo** (`Decision` con
  `status: accepted`, `Convention`, `Roadmap`, `Change` activo) → el código que difiere está
  **en violación**. Ante una violación hay dos salidas y ninguna tercera: **arreglar el
  código** o **superseder** la decisión; editar el documento para emparejarlo está prohibido.
  Dos límites evitan reintroducir drift: lo normativo nunca responde "¿qué hace el código
  hoy?", y la autoridad de un trabajo en curso caduca en el harvest.
- **`authority: normative | descriptive`**: clave de frontmatter **opcional** (§3.1) para
  cuando el `type` no lo deja claro; el default se deduce del tipo
  (tabla nueva en `reference/profiles.md`).
- **Nivel 4 de verificación — Cumplimiento** (opcional, periódico) en
  `reference/verification.md` y `okf-verify`: auditar el **código contra lo normativo**
  (violación / decisión obsoleta / decisión ambigua). Es auditoría con criterio, no script:
  no va en CI. Hasta acá el kit solo cubría el drift del doc que envejece; ahora también el
  del **código que se desvía de lo decidido**.
- `templates/knowledge/_decision.md` invita a declarar **cómo verificar** la decisión
  (comando/grep/test) — una decisión chequeable es la que sobrevive.
- Propagado con **punteros** a §3.5 desde `reference/maintaining.md`,
  `reference/verification.md`, `reference/spec-driven-interop.md`, `reference/profiles.md`,
  `templates/knowledge/_decision.md`, `GUIDE.md` y el `AGENTS.md` del propio kit. El material
  que se **instala** (`templates/AGENTS.md`, `okf-update`, `okf-verify`) enuncia la regla en
  vez de apuntar, a propósito: el repo destino no recibe `OKF-SPEC.md`, y un puntero a un
  archivo inexistente es peor que una copia. El `okf_selfcheck` vigila que esas copias no
  pierdan la rama normativa.
- **`okf_selfcheck.py`**: assert nuevo — la rama normativa no puede caerse del contrato, de
  `okf-update` ni de `okf-verify`, y el `GUIDE` tiene que enseñar la regla (es el tipo de
  regla que ya derivó históricamente en este kit).
- Dogfood: la decisión `0012` se generalizó a la regla tipada completa.

### Arreglado — lo que encontró el cold-review de 4 lentes (gate de release)
Antes de publicar el minor corrió el gate de `DEVELOPING.md` §3: cuatro revisores en frío e
independientes (consistencia / completitud / correctness ejecutando el tooling / dogfood
siguiendo el `GUIDE` sobre un repo de juguete). Encontraron 2 blockers y ~12 majors, **ninguno
en el diseño**: todos en la capa de propagación e instalación. El patrón común es uno solo —
**el material instalado suponía que `okf-kit` seguía en disco**:

- **El camino "no uso Claude Code" rompía el linter.** El `GUIDE` mandaba copiar los tres
  `SKILL.md` a `knowledge/runbooks/`; traen frontmatter sin `type`, así que adentro del bundle
  son conceptos inválidos → 3 ERROR, hook bloqueando cada commit y CI en rojo, para la mayoría
  de los usuarios. Ahora van a `docs/okf/`, fuera del bundle.
- **La instalación mínima dejaba el contrato roto.** La instrucción "borrá lo que no
  instalaste" era prosa y enumeraba 2 lugares; la capa de futuro aparecía en 3, y la garantía
  "si te pide ir directo al código, respetalo" vivía **dentro** del bloque a borrar. Ahora el
  borrado es **mecánico**: 3 pares de marcadores `OKF:future-layer:start/end` en el template,
  y dos asserts nuevos (marcadores balanceados; la versión mínima no puede mencionar
  `_changes/`, `okf-plan` ni `roadmap.md`). Medido: completo ≈1590 tokens/turno, mínimo ≈1300.
- **Autosuficiencia del material instalado.** `okf-plan` mandaba crear el roadmap y los
  cambios "desde el template `templates/knowledge/_change.md`", `okf-verify` había perdido su
  hedge y citaba `reference/verification.md` para el formato del reporte, y el contrato
  apuntaba a `reference/maintaining.md` e `install-per-tool.md`. Todo eso se **inlineó** (los
  esqueletos de `_roadmap.md`/`_change.md` viven ahora en `okf-plan`; el formato del reporte,
  en `okf-verify`), y un assert nuevo prohíbe que el material instalado cite rutas del kit.
- **La regla del `index.md` raíz decía una cosa y el kit hacía otra.** Cinco archivos
  afirmaban "la raíz solo lista subdirectorios" mientras el template y el dogfood ponen
  `roadmap.md` ahí: todo repo que instalara la capa siguiendo el `GUIDE` arrancaba con un WARN.
  Corregido en el canónico (`OKF-SPEC.md` §5) y en las siete copias que la repetían.
- **El alcance de lo normativo tenía tres versiones.** §3.5 no incluía el `Roadmap`,
  `profiles.md` sí, y `verification.md` sumaba "las reglas duras del `AGENTS.md`". Peor: §3.5
  listaba "dominio" como descriptivo mientras `profiles.md` ubica `Convention` (normativo) en
  `domain/` — respuestas opuestas para el mismo archivo. §3.5 es ahora la fuente única: **la
  clase la da el `type`, no la carpeta**, e incluye el entrypoint explícitamente.
- **Bomba de tiempo en el dogfood:** la decisión `0011` —permanente— linkeaba a
  `_changes/0001`, que el harvest manda borrar: el gate quedaba verde hoy y rojo el día que se
  cerrara el cambio. Cortado, y la regla ("ningún doc permanente linkea a `_changes/`") quedó
  en `okf-plan` y en el checklist de harvest, que además ganó dos ítems que faltaban
  (carpeta nueva → `# Subdirectories`; entrada en `log.md`).
- **La pregunta de instalación estaba escrita en el vocabulario del kit** ("¿1600 o 1200
  tokens por turno?") — violando, en el primer paso que involucra al usuario, la regla
  "hablale en su idioma" que esta misma versión agrega. Ahora se pregunta por el
  comportamiento, con un fallback documentado si el usuario no contesta la entrevista del
  roadmap.
- Menores: `status: idea` del template de cambio (contradecía la regla de `okf-plan` de no
  abrir docs para ideas sin compromiso), conteos que no cerraban, `okf-init` desalineado del
  `GUIDE` en los dos niveles de instalación, y descripciones stale del `okf_selfcheck`, del
  registro anti-deriva de `DEVELOPING.md` y del linter (atribuía a PyYAML un chequeo que hace
  un parser propio).
- **`okf_selfcheck.py`: 26 → 68 asserts.** Los nuevos cubren exactamente las reglas que este
  review vio derivar. Los cuatro revisores convergieron de forma independiente en 5 findings,
  y 7 de 7 roturas deliberadas del gate fallaron correctamente.

Y como el kit exige que **cada fix se testee adversarialmente**, los arreglos de arriba
pasaron por su propia revisión en frío (consistencia del diff + dogfood re-caminando el
`GUIDE`). Encontró 1 blocker y ~14 majors **introducidos por los propios fixes**, todos
cerrados acá. Los que valen como lección:

- **`cp` de los tres `SKILL.md` a `docs/okf/` los pisaba entre sí** (los tres archivos fuente
  se llaman igual): el camino vendor-neutral instalaba **un** procedimiento de tres, sin error
  visible. Ahora la instrucción renombra explícitamente.
- **`okf-update` desactivaba en silencio la capa normativa:** su lista de frontmatter no
  nombraba `status:`, y el Nivel 4 filtra por `status: accepted`. Una decisión escrita
  siguiendo el contrato al pie de la letra quedaba fuera de la auditoría — la capa que esta
  misma versión construye se apagaba sola en el uso normal.
- **El Nivel 4 de la copia instalada no excluía el rumbo**, así que reportaría cada ítem no
  implementado del roadmap como "violación del código": el falso positivo exacto que la
  decisión 0012 dice mitigar.
- Varias afirmaciones de la primera tanda eran **falsas y estaban escritas como verificadas**
  (números transcritos a mano que ya no coincidían, "sin punteros huérfanos", "nadie lo
  describe en prosa", conteos de copias). Corregidas, y los asserts que las cubren se
  ajustaron para medir lo que dicen medir.

## 0.5.0 — 2026-06-17

### Agregado — buenas prácticas cosechadas de un sistema de contexto real
Tras investigar la "LLM-Wiki" de un repo real (the-conclave) —un sistema de contexto
maduro, equivalente a OKF y en partes más avanzado— se incorporaron sus mejores ideas:

- **Regla "gana el código" (staleness):** si un concepto contradice la fuente
  (código/schema/datos), el concepto es un bug — se arregla, no al revés. En `OKF-SPEC.md`
  (nueva §3.4), el contrato `templates/AGENTS.md`, `okf-update` y `reference/verification.md`
  (nuevo smell **grave**).
- **Ciclo de deprecación** (gap que la revisión en frío ya había marcado): `_decision.md`
  suma `status` (`proposed`/`accepted`/`superseded by NNNN`) + `supersedes`; `okf-update` y
  `reference/maintaining.md` documentan el procedimiento (decisión nueva que *supersedes* a
  la vieja, mover a `archive/` o marcar `SUPERSEDED`, **nombrar el concepto viejo** para grep).
- **"No transcribas hechos del código"** afilado: clasificación in-code vs *por qué*, el
  framing "un número a mano = drift", y el patrón opcional **`_generated/`** (hechos volátiles
  derivados del código por un script propio). En §3.4 y `reference/profiles.md`.
- **Header de frescura** opcional en references (`verified_against`, `source_of_truth`) —
  `OKF-SPEC.md` §3.1 y `templates/knowledge/_reference.md`.
- **"Concepto = estado presente"** (no historial ni planes; sin checkboxes) — §3.4.
- **`log.md` des-enfatizado a claramente opcional:** en un repo bajo git, `git log` + las
  `decisions/` cumplen su función. `OKF-SPEC.md` §6, `GUIDE.md`, `templates/AGENTS.md`,
  `okf-update`, `maintaining.md`.
- **Scratchpad efímero** (`knowledge/_scratchpad.md`) para tareas multi-sesión — `maintaining.md`.

### Cambiado — linter
- `okf_lint.py` ahora ignora **archivos y carpetas con prefijo `_`** (no solo archivos):
  habilita `_generated/` y `_scratchpad.md`. Verificado: el dogfood sigue 0/0 y un `.md`
  normal sin frontmatter sigue dando ERROR.

### Dogfood
- Las `decisions/` del propio bundle adoptan el nuevo `status: accepted`.

## 0.4.3 — 2026-06-17

### Arreglado — pre-commit hook seguro + 2 falsos positivos
- **GRAVE (regresión de 0.4.1):** el hook usaba `git stash --keep-index` + `pop`, que con
  *partial-staging* (stagear parte de un archivo y seguir editándolo) **inyectaba marcadores
  de conflicto y corrompía el working-tree** — y no solo en `knowledge/`, en cualquier archivo.
  Ahora el hook copia el contenido **staged** de `knowledge/` a un tempdir con
  `git checkout-index` y lintea ahí: el working-tree **nunca se toca**. Valida lo mismo (lo
  que se commitea) sin riesgo.
- **Linter (falsos positivos sobre YAML válido):** se tolera un **BOM UTF-8** antes del `---`
  (editores Windows ya no disparan "falta frontmatter"); y una **clave entrecomillada** con `:`
  (`"a:b": 1`) ya no se marca como línea malformada.

## 0.4.2 — 2026-06-17

### Arreglado — gate **determinista** (cierra la divergencia que tapaba el techo)
- **Linter sin PyYAML:** el frontmatter ahora se valida con un **validador del subconjunto
  YAML en Python puro** que corre siempre. Se **removió PyYAML** del camino del veredicto →
  el PASS/FAIL **no depende de qué tengas instalado** (probado: con y sin `yaml` da output
  idéntico). Antes, un `:` sin comillas u otros YAML rotos eran ERROR con PyYAML y pasaban sin
  él → un dev podía commitear local lo que el CI rechazaba. El validador atrapa `:` sin comillas
  (medio y trailing), comillas/brackets sin cerrar, tabs y líneas malformadas. Quitado el
  `pip install pyyaml` del CI (ya innecesario).
- **Falso positivo del linter:** links absolutos dentro de **code-blocks indentados** (≥4
  espacios / tab) ya no se marcan como ERROR.

> Trade-off: el validador stdlib no cubre el 100% del YAML inválido teórico (eso es
> re-implementar PyYAML); lo que se le escape pasa **uniforme** (local == CI) — gap acotado,
> no divergencia. A cambio: gate determinista y **cero dependencias**.

## 0.4.1 — 2026-06-17

### Arreglado — el gate de conformidad, ahora determinista (re-review en frío)
- **PyYAML:** un valor de frontmatter con `:` sin comillas ahora es **ERROR en ambos modos**
  (antes: ERROR con PyYAML, WARN sin → veredicto opuesto). El CI (`okf.yml`) **pinea PyYAML**
  para que el gate autoritativo corra siempre el camino fuerte; docstring sincerado.
- **Pre-commit hook:** ahora linta **lo staged** (`git stash --keep-index` + `trap`), no el
  working-tree — cierra el falso positivo (bloquear un commit que no toca `knowledge/`) y el
  hueco de soundness (snapshot roto entrando a la historia).
- **`okf_selfcheck`:** nuevo assert — el `kit_version` del dogfood debe **coincidir con
  `VERSION`** (antes solo grepeaba presencia → dejó pasar un stamp stale). Dogfood re-estampado;
  semántica fijada (born-at en repos destino, current en el dogfood que el kit mantiene).
- **Linter:** el match "concepto no linkeado en su index" compara el path resuelto, no el
  basename → cierra un falso negativo.

## 0.4.0 — 2026-06-17

Resultado de una **revisión de 4 lentes en frío + dogfood** (el kit aplicado a sí mismo).

### Arreglado (correctness + trampas)
- **Linter (`okf_lint.py`):** ya no chequea links dentro de comentarios HTML ni de
  inline-code (eran falsos positivos — el kit fallaba su propio linter), ni escanea el
  frontmatter buscando links. Se cerró un **falso-negativo**: un ` ``` ` huérfano (p.ej.
  dentro de un comentario) silenciaba chequeos duros y dejaba pasar un link absoluto roto
  por lint/hook/CI. Nuevo **aviso** si un valor de frontmatter lleva `:` sin comillas (la
  trampa que rompía el YAML, env-dependiente).
- **`okf-verify`:** criterio de FAIL completo (enumeraba mal los ERRORs de frontmatter).
- `reference/examples.md` ahora incluye `kit_version` en el root index (antes enseñaba a omitirlo).

### Cambiado (single-source-of-truth, anti-deriva)
- Keep-alive con **una fuente canónica**: `AGENTS.md §2` + `okf-update` (idénticos);
  `GUIDE §5` y `maintaining.md` pasaron a punteros. `okf-update` ahora incluye la
  agrupación del index por `# {type}` y el orden correcto de frontmatter.
- Resuelta la contradicción SPEC-vs-GUIDE: `OKF-SPEC` sanciona `kit_version` (y otras
  claves del productor) en el root index. Gotcha del `:` documentado en SPEC §3.1; `profiles.md`
  apunta a las reglas de frontmatter (antes las omitía).

### Agregado (prevención)
- **`scripts/okf_selfcheck.py`** — meta-linter que valida la consistencia *interna* del kit
  (kit-only; no se instala en repos destino). `DEVELOPING.md` documenta el gate de release
  (selfcheck + cold-review de 4 lentes).
- Bundle **dogfood** `knowledge/` — el kit documentándose en su propio formato (pasa 0/0).

## 0.3.0 — 2026-06-17

### Agregado — capa de mantenimiento y universalidad cross-vendor
- **Contrato de trabajo en `AGENTS.md`**: el entrypoint pasó de índice a **contrato
  completo** (1. leé el contexto → 2. mantené el contexto vivo → 3. verificá antes de
  cerrar), con guardrails inline. Sirve a **cualquier IA** sin depender de skills.
- **`reference/maintaining.md`**: el ciclo de vida post-init (simétrico a `GUIDE.md`) y las
  capas de enforcement (contrato → skill → git hook → CI → cold test).
- **`templates/hooks/pre-commit`**: git hook **universal** — bloquea commits no conformes y
  avisa si cambió código sin tocar `knowledge/`. Corre con cualquier herramienta/IA (nivel git).
- **`reference/install-per-tool.md`**: cómo conectar OKF a Claude Code, Cursor, Copilot,
  Gemini y otras — todo punteros a `AGENTS.md`, sin lock-in.
- Los **skills** se reencuadran como **procedimientos vendor-neutral** (funcionan como skill
  de Claude *o* se siguen directo). El núcleo (contrato + git hook + CI + linter) no depende
  de Claude Code.

## 0.2.0 — 2026-06-17

### Agregado
- Integración **opcional** con [Repomix](https://github.com/yamadashy/repomix) (externo,
  Node/`npx`, **nunca requerido**), documentada en `reference/optional-tools.md`:
  - **Entender el repo** al bootstrapear/migrar empaquetándolo en un único archivo
    comprimido (acelera `okf-init`/`okf-migrate` y `GUIDE.md §3`; un gasto único al
    estructurar, después es mantenimiento incremental).
  - **Token-sizer** del bundle para detectar `index.md`/conceptos demasiado grandes
    (smell de Nivel 2 en `verification.md`) y decidir cuándo partir (`special-cases.md`).
  - Aclaración: Repomix **no consume tokens de LLM** (es un tokenizador local).

## 0.1.0 — 2026-06-17

Primera versión versionada del kit. Contenido:

- **Formato**: `OKF-SPEC.md` (spec condensada y self-contained, OKF v0.1), con la
  convención de **cross-links relativos al archivo** (funcionan en GitHub sin tooling).
- **Guía**: `GUIDE.md` (procedimiento de bootstrap, perfil → siembra → índices →
  verificación) y `README.md`.
- **Universalidad**: `reference/profiles.md` (perfiles código / datos / wiki /
  mixto), `reference/examples.md` (ejemplos en los tres dominios),
  `reference/special-cases.md` (monorepos, migración, escala, idioma).
- **Testeo**: `reference/verification.md` (3 niveles), el linter determinista
  `templates/scripts/okf_lint.py` (solo stdlib, sin `pip install`) y
  `templates/scripts/okf_coldtest.py` (entorno aislado para el test en frío).
- **Skills**: `okf-init` (bootstrap), `okf-update` (mantenimiento), `okf-verify`
  (testeo), `okf-migrate` (migración brownfield).
- **Templates**: `AGENTS.md`/`CLAUDE.md` (entrypoint), `knowledge/` (index, log,
  conceptos), y `ci/okf.yml` (GitHub Action que corre el linter por push, cero tokens).

Sin dependencias externas ni `pip install`; cero apps (Obsidian, etc.) requeridas.
