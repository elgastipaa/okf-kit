# Verificación — cómo testear un bundle OKF

Testear un bundle tiene **cuatro niveles**, de lo mecánico a lo que de verdad importa.
Corré 1 y 2 siempre (son baratos); el 3 es la prueba de fuego. El 4 es **opcional y
periódico**, y mira en la dirección contraria: no si el bundle está bien, sino si el
**código respeta** lo que el bundle prescribe.

| Nivel | Qué mide | Naturaleza | Veredicto |
|---|---|---|---|
| **1. Conformidad** | ¿Es OKF válido? (estructura) | Objetivo, chequeable | PASS / FAIL |
| **2. Calidad** | ¿Es un *buen* bundle? | Heurístico, con criterio | smells a corregir |
| **3. Outcome** | ¿Un agente en frío entiende el proyecto con *solo* el bundle? | Comportamiento | **la prueba real** |
| **4. Cumplimiento** *(opcional)* | ¿El código viola alguna decisión aceptada o convención? | Auditoría, con criterio | violaciones a resolver |

> **Quién corre qué:**
> - **Nivel 1** → el script `okf_lint.py` (determinista, solo stdlib, sin instalar nada).
> - **Nivel 2** → el skill `okf-verify` (necesita criterio).
> - **Nivel 3** → un agente en frío: el skill puede **lanzar un subagente** restringido
>   al bundle, o lo corrés vos en una CLI/IA nueva (lo más fiel, y lo único que prueba
>   portabilidad cross-vendor).

---

## Nivel 1 — Conformidad (objetivo, PASS/FAIL)

**La forma rápida y determinista: corré el script** (solo stdlib, sin `pip install`):

```
python3 scripts/okf_lint.py knowledge
```

Sale 0 si conforma (warnings permitidos), 1 si hay errores. `--strict` hace fallar
también con warnings — **usalo con cuidado: el default (sin `--strict`) es el
correcto para CI**, porque un link a un concepto aún no escrito es WARN y no debe
romper el build (consumo permisivo, SPEC §8). Chequea automáticamente todo el checklist de
abajo, que queda como referencia de *qué* valida (y para hacerlo a mano si no podés
correr el script). El script cubre el checklist de abajo **salvo *Entrypoint
resuelto*** (ese lo evalúa el agente con criterio, porque depende de si es un repo de
código) e **ignora los archivos `_*.md`** (plantillas/borradores). Para cada ítem:
`[x]` pasa, `[!]` warning, `[ ]` falla.

> **¿Sin Python en la máquina?** El script necesita un intérprete Python 3 (sin
> librerías). Instalá Python 3, **o** saltá el script: el skill `okf-verify` corre
> este mismo Nivel 1 leyendo los archivos, sin ejecutar nada. El checklist de abajo
> es exactamente lo que valida, en cualquiera de los dos caminos.

- [ ] **Frontmatter parseable.** Todo `.md` no reservado (≠ `index.md`, `log.md`)
  empieza con `---`, cierra con `---`, y el bloque es YAML válido (un mapping).
- [ ] **`type` presente.** Todo concepto tiene `type:` no vacío. *(Único requisito
  duro de OKF — ver `OKF-SPEC.md` §8.)*
- [ ] **Defaults de autoría.** Todo concepto tiene `title`, `description` y
  `timestamp`. `description` es **una sola frase**. *(Warning si falta, no falla.)*
- [ ] **Reservados bien usados.** `index.md` no lleva frontmatter (salvo
  `okf_version` en la raíz). `log.md` con fechas ISO `YYYY-MM-DD`, más nuevas primero.
- [ ] **Links relativos al archivo.** Ningún cross-link empieza con `/`. Todos son
  relativos (`./x.md`, `../dir/y.md`). *(Los `/`-absolutos rompen en GitHub.)*
- [ ] **Links resuelven.** Cada cross-link relativo apunta a un archivo existente.
  *(Roto = warning, no fatal — puede ser conocimiento no escrito aún; pero listalos.)*
- [ ] **Índices cubren y coinciden.** Cada carpeta con conceptos tiene `index.md`;
  sus entradas coinciden con los archivos reales (sin entradas viejas ni archivos
  faltantes). La raíz lista **todos** los subdirectorios **no ignorados** (los de prefijo `_`
  no van: son derivados o efímeros), y los conceptos que vivan en la
  raíz (`roadmap.md`, `glossary.md`) agrupados por `type`. *(Lo de los subdirectorios el
  script todavía no lo valida — se chequea acá.)*
- [ ] **Entrypoint resuelto** *(lo evalúa el agente, no el script)*. Existe
  `AGENTS.md` que apunta a `knowledge/index.md`, **o** el `README` del repo apunta a
  `knowledge/`. Si hay `CLAUDE.md`, es un shim fino. *(El script solo valida que el
  bundle tenga `index.md` raíz, que es lo que lo hace navegable.)*
- [ ] **Sin carpetas vacías.** No hay directorios sin conceptos.

Veredicto Nivel 1 (idéntico al exit code del script): **FAIL (exit 1)** si hay
algún **ERROR** — frontmatter ausente/roto/no-mapping, `type` faltante, YAML inválido,
o **link absoluto `/`**. Todo lo demás es **WARN** y no bloquea (defaults faltantes,
`index.md` con frontmatter, fecha de `log.md` no-ISO, links rotos, índices
desfasados, etc.). Con `--strict`, los warnings también hacen FAIL.

---

## Nivel 2 — Calidad (heurístico, con criterio)

No es pass/fail; son **smells** que bajan el valor del bundle. Reportá los que veas.

> **Quién lo corre importa tanto como el método.** Este nivel y el 4 son los únicos que auditan
> *trabajo que el propio agente pudo haber hecho*, y son los dos donde el sesgo pesa más: quien
> redactó un concepto lo lee sabiendo lo que quiso decir, y quien escribió el código racionaliza
> por qué no viola ninguna decisión. Si la sesión que audita es la que hizo el trabajo, estos dos
> niveles se **delegan a contexto fresco**: el agente `okf-reviewer` que el kit instala, o un
> proceso/CLI nuevo con el prompt (igual que el Nivel 3). Es la misma práctica que el kit usa
> para desarrollarse — el cold-review de `DEVELOPING.md`, al que su propio historial le acredita
> 2 blockers y ~12 majors en una sola pasada.

### Cómo buscar el drift descriptivo (el smell que importa)

El resto de los smells se ven leyendo. Este no: un concepto que contradice el código se ve
igual de prolijo que uno correcto. Necesita método, y es el mismo del Nivel 4 invertido:

1. **Empezá por donde es más probable, no por el principio.** Corré
   `python3 scripts/okf_stale.py knowledge`: con `resource:` + `timestamp` + git te dice
   qué conceptos apuntan a código que se movió mucho desde que se escribieron, cuáles
   apuntan a un archivo que ya no existe, y cuáles tienen el sello de frescura podrido.
   No lee código ni gasta tokens — solo **rankea dónde mirar**. Auditar el bundle entero es
   lo que hace que nadie lo audite.
2. **Por cada concepto de esa lista corta, buscá la contradicción, no la confirmación.**
   Listá qué **afirma sobre el código** —un conteo, una ruta, un nombre, una flag, "existe
   X", "esto está en curso"— y andá a la fuente a intentar **refutarlo**. Leerlo buscando
   que cierre es la forma más rápida de no encontrar nada.
3. **Clasificá cada hallazgo**, porque el arreglo es distinto:
   - **Doc podrido** — el código cambió y el concepto quedó viejo. Gana el código: se
     corrige el concepto (y si el dato es volátil, se **linkea o se genera** en vez de
     re-transcribirlo, o vuelve a pasar).
   - **Código desviado** — solo si lo que contradice es **normativo**; entonces no es este
     nivel, es el 4.
   - **Ambos cambiaron** — el concepto describe algo que ya no existe *de ninguna forma*.
     Se deprecia, no se parcha.
4. **Reportá; no resuelvas solo.** Igual que en el Nivel 4: quién tiene razón lo decide el
   usuario, sobre todo cuando el "arreglo" obvio es borrar el documento.

> **Un dato que hay que transcribir a mano es un dato que va a driftear.** Si el hallazgo es
> un valor copiado, el arreglo duradero no es corregirlo: es que deje de estar copiado
> (`resource`, un link, o el patrón `_generated/`).

- **¿Captura el *por qué* o repite el *qué*?** Smell: un concepto que solo reenuncia
  lo que se lee del código/schema sin agregar intención, decisión ni caveat.
- **¿Duplica la fuente?** Smell: bloques de código/schema copiados en vez de
  linkeados con `resource`. Lo deducible de la fuente se linkea, no se copia.
- **¿Algún concepto DESCRIPTIVO contradice el código?** Smell **grave**: un dato del
  bundle (un conteo, una flag, una ruta, un nombre) que ya no coincide con la fuente.
  **Gana el código** — el concepto es un bug. Suele venir de transcribir en vez de linkear.
  *(Si el que contradice es un concepto **normativo** —una decisión aceptada, una
  convención— no es este smell: es una **violación del código**, y va al Nivel 4.)*
- **¿Es un grafo o solo un árbol?** Smell: conceptos huérfanos, sin cross-links
  entrantes ni salientes. Los conceptos relacionados deberían linkearse entre sí.
- **¿Progressive disclosure real?** Smell: `AGENTS.md` o los `index.md` enormes; o
  todo el detalle metido en pocos archivos gigantes en vez de conceptos navegables.
  Medilo objetivamente con el token-sizer opcional (ver `reference/optional-tools.md`).
- **¿Descripciones útiles?** Smell: `description` de varias oraciones, o genérica
  ("Información sobre X"). Tiene que servir como snippet en el índice.
- **¿Las decisiones explican consecuencias?** Smell: un `Decision` sin contexto ni
  consecuencias — solo "hicimos X".
- **¿Cubre el conocimiento tribal?** Smell: estructura linda pero faltan las
  decisiones, gotchas y runbooks que el código no dice. Estructura ≠ contenido.

---

## Nivel 3 — Outcome / comportamiento (la prueba de fuego)

Mide lo único que importa: **¿un agente sin contexto previo, leyendo solo el
bundle, entiende el proyecto?** Es exactamente tu caso de uso.

**Protocolo:**

1. **Armá el set de preguntas (5-10).** Lo que le preguntaría un compañero nuevo o
   un agente al arrancar. Mezclá tipos:
   - *Operativas:* "¿cómo corro las migraciones?", "¿cómo levanto esto local?"
   - *De diseño:* "¿por qué se eligió X sobre Y?"
   - *De dominio/datos:* "¿cuál es el grano de la tabla orders?", "¿dónde pasa el auth?"
   - *Una trampa:* algo que **no** esté en el bundle, para ver si lo admite en vez
     de inventar.
2. **Abrí una CLI nueva, en frío**, en el repo (o con acceso solo a `knowledge/`).
   Pegá este prompt:

   > Tenés acceso **solo** a la carpeta `knowledge/` de este repo. **No leas el
   > código.** Respondé estas preguntas usando solo el bundle OKF, y **citá el
   > archivo** de donde sacás cada respuesta. Si algo no está en el bundle, decí
   > explícitamente "no está en el contexto" en vez de inventar.
   > 1. …  2. …  3. …

3. **Calificá cada respuesta:** ✅ correcta y citada · ⚠️ parcial/sin citar ·
   ❌ incorrecta o inventada · 🟦 admitió bien que no estaba (la trampa).
4. **Bar de aprobación:** ≥ 80% de las reales en ✅, la trampa en 🟦, y que haya
   **navegado por los `index.md`** (no leído todo). Si no, no pasa.
5. **Feedback loop:** cada ❌/⚠️ es un **concepto faltante o débil**. Anotalo y
   metelo al bundle con `okf-update`. Re-testeá.

Este es el test que valida "cualquier IA, sin contexto, entiende el proyecto".

### ¿Se puede automatizar? Sí — tres grados

El "agente en frío" no tiene que ser siempre manual. De menos a más fiel:

1. **Subagente (contexto fresco), aislado por instrucción.** El agente que corre
   `okf-verify` lanza un subagente (Task/Agent) que arranca **sin** la conversación
   actual, con la consigna: "leé **solo** `knowledge/`, no abras el código, respondé
   citando archivos". Después califica las respuestas y **verifica que las citas
   apunten a `knowledge/`**. Limitación: el aislamiento es por instrucción (podría
   espiar el código si desobedece).
2. **Entorno aislado con `okf_coldtest.py`.** Más fuerte: corré
   `python3 scripts/okf_coldtest.py knowledge --out <dir>` — copia **solo** el bundle
   (+ `AGENTS.md`) a un dir limpio, **sin código ni `.git`**, e imprime el prompt. Para
   una **CLI/IA nueva** abierta en ese dir, el código no está al alcance (aislamiento
   real). Para un **subagente** del mismo proceso (ve todo el filesystem) el aislamiento
   sigue siendo por instrucción, pero el entorno limpio reduce fugas y permite chequear
   que las citas caigan dentro del bundle. (Con `--git` crea además un repo limpio para
   probar que el bundle se sostiene clonado.)
3. **Proceso/CLI nueva, o directamente otra IA (manual).** Lo más fiel — y la
   **única** forma de probar portabilidad cross-vendor ("con la IA que sea"), porque
   un subagente es el mismo modelo. Esto se corre a mano.

Regla: usá el grado 1-2 como **test de regresión** barato y frecuente; usá el grado
3 de vez en cuando para confirmar que el bundle funciona en *otra* herramienta.

---

## Nivel 4 — Cumplimiento (opcional, periódico)

Los otros tres niveles preguntan *"¿está bien el bundle?"*. Este pregunta lo inverso:
**¿el código respeta lo que el bundle prescribe?** Es el drift más caro, porque no se ve:
el bundle sigue prolijo, el código sigue andando, y la decisión que alguien tomó por una
razón se perdió en silencio.

Es una **auditoría con criterio** (no un script): requiere leer el código, así que no va en
CI ni se corre en cada commit. Corrélo cada tanto, o antes de un release.

1. **Listá lo normativo *auditable*:** las `decisions/` con `status: accepted`, las
   convenciones, y las reglas duras del `AGENTS.md`. (Los `type` normativos están en
   `reference/profiles.md`; la regla, en `OKF-SPEC.md` §3.5.) Ignorá las `proposed` y las
   `superseded`.

   **Del rumbo, solo la sección "Ahora".** Visión, "Después" y no-goals son **intención
   pura**: que el código no los haya alcanzado es trabajo pendiente, no una violación, y
   auditarlos sería puro falso positivo. Pero **"Ahora" afirma estado del código** —que ese
   trabajo está en curso— y eso sí es chequeable: un ítem cuyo trabajo **ya está terminado**
   (o que nunca arrancó) es una afirmación descriptiva podrida, con un costo medido: un
   roadmap desactualizado sale **más caro que no tener roadmap**, porque los agentes gastan
   turnos descubriendo que miente (ver `0014-future-layer-measured`).
2. **Por cada una, buscá su violación**, no su confirmación. Si la decisión declara **cómo
   verificarla** (el comando/grep/test del template `_decision.md`), corré eso. Si no,
   derivá la señal: "usamos cola para emails" → ¿hay envíos directos fuera del worker?
3. **Clasificá cada hallazgo:**
   - **Violación** — el código contradice la decisión. Reportala; **no toques el documento**.
   - **Decisión obsoleta** — la realidad cambió y la decisión ya no tiene sentido. También
     se reporta: el fix es **supersederla** (decisión nueva con `supersedes`), no borrarla.
   - **Ambiguo** — la decisión está redactada tan vaga que no se puede chequear. El fix es
     afilar el documento (y agregarle su forma de verificación).
4. **Resolvé con el usuario, no solo.** Cada violación tiene dos salidas legítimas —
   arreglar el código, o cambiar la decisión explícitamente. Elegir por él (sobre todo
   "actualizo el doc y listo") es el failure mode que este nivel existe para cazar.

> **Escala:** si el bundle tiene muchas decisiones, no audites todas cada vez. Priorizá las
> que tocan el área que se está cambiando y las que tengan verificación declarada (baratas).

---

## Formato de reporte

```markdown
# OKF Verification Report — <bundle> — <YYYY-MM-DD>
Resultado: PASS | PASS-WITH-WARNINGS | FAIL

## Nivel 1 — Conformidad
[x]/[!]/[ ] por ítem (el output del script tal cual, o el checklist de 9 ítems)

## Nivel 2 — Calidad
- Quién lo corrió: yo | revisor con contexto fresco (`okf-reviewer`)
- smells encontrados (o "ninguno")

## Nivel 3 — Outcome
- Set de preguntas usado
- Cómo correrlo (prompt de CLI en frío) — o resultados si ya se corrió

## Nivel 4 — Cumplimiento (si se corrió)
- Quién lo corrió: yo | revisor con contexto fresco (`okf-reviewer`)
- Decisiones/convenciones auditadas y violaciones encontradas (o "ninguna")

## Issues
| Sev | Archivo | Problema | Fix sugerido |
|-----|---------|----------|--------------|
| FAIL/WARN/SMELL | path | … | … |

## Veredicto
<una línea> + próximos pasos
```
