---
name: okf-verify
description: >
  Testea el bundle de contexto OKF del repo (la carpeta knowledge/) y emite un
  reporte PASS/FAIL. Usalo después de montar el bundle, después de cambios grandes,
  o periódicamente. Corre conformidad estructural y heurísticas de calidad, y
  prepara el test de comportamiento (agente en frío).
---

Este repo usa **OKF** para su contexto en `knowledge/` (ver `AGENTS.md`). Este
skill verifica que ese bundle esté bien. (Procedimiento **vendor-neutral**: skill de
Claude Code o seguilo directo desde cualquier agente.) Hay cuatro niveles; corré 1 y 2 vos mismo
leyendo los archivos, y **preparás** el 3 para que lo corra el usuario en una CLI
nueva. El **Nivel 4 es opcional** (auditoría de cumplimiento): corrélo si el usuario lo pide
o si el bundle no se audita hace mucho. **Es autosuficiente**: todo lo que hace falta para
correrlo y para emitir el reporte está acá, sin depender de que `okf-kit` siga en disco.

**No arregles nada sin avisar.** Emití el reporte primero; ofrecé aplicar los fixes
con el skill `okf-update` si el usuario quiere.

> **Si en esta sesión escribiste o modificaste el bundle (o el código que audita), los Niveles
> 2 y 4 NO los corrés vos: delegalos a un revisor con contexto fresco** — el subagente
> `okf-reviewer`, o, si tu herramienta no tiene subagentes, entregale al usuario el prompt para
> pegarlo en una CLI nueva (igual que el Nivel 3). Su método es *buscá la contradicción*: quien
> redactó un concepto lo lee sabiendo lo que quiso decir, y quien escribió el código racionaliza
> por qué no viola nada. **Decí en el reporte quién corrió cada nivel.** Si no hiciste el
> trabajo que se audita, corrélos vos normalmente.

# Nivel 1 — Conformidad (objetivo, PASS/FAIL)

**Corré el script** (determinista, solo stdlib, sin instalar nada) y parseá su
salida — es la fuente de verdad del Nivel 1:

```
python3 scripts/okf_lint.py knowledge   # estructura: frontmatter, links, índices
python3 scripts/okf_refs.py  knowledge  # referencias vivas: ¿nombra archivos que ya no están?
```

El segundo es el que caza el drift más barato y más común —renombres y borrados—, que es
el que convierte un `code-of-record` en una mentira sin que nadie se entere. **No dice si un
concepto es verdad**: eso es el Nivel 2. Si reporta algo, gana el código: se corrige el
concepto. Si la referencia es a algo externo, se saca con `--ignore`, no editando el script.

Y si el bundle declara `verify:` en sus decisiones, corré también:

```
python3 scripts/okf_decisions.py knowledge/decisions
```

Corre **en la dirección contraria** a todo lo demás: una decisión `accepted` es normativa, así
que un hallazgo acá significa que **el código está en violación**, no que el documento quedó
viejo. Las salidas son arreglar el código o superseder la decisión — **nunca** editar la
decisión para que coincida con lo que el código hace hoy.
**Ojo: ejecuta comandos escritos en markdown.** Si el bundle no es tuyo, mirá primero con
`--list`.

Exit 0 = conforme (warnings permitidos), 1 = errores. Reportá su output tal cual en
la sección Nivel 1 del reporte.

**Si la máquina no tiene Python (o el script no está), NO lo ejecutes:** hacé estos
mismos chequeos vos, leyendo los archivos. Este es el camino oficial para máquinas
sin Python — el Nivel 1 no depende de ejecutar nada:

1. **Frontmatter:** todo `.md` no reservado (≠ `index.md`, `log.md`) abre y cierra
   con `---` y el bloque es YAML válido.
2. **`type` no vacío** en cada concepto. *(Falla dura si falta — es el único
   requisito obligatorio de OKF.)*
3. **Defaults de autoría:** `title`, `description` (una sola frase) y `timestamp`
   presentes. *(Warning, no falla.)*
4. **Reservados:** `index.md` sin frontmatter (salvo `okf_version` en la raíz);
   `log.md` con fechas ISO `YYYY-MM-DD`.
5. **Links relativos:** ningún cross-link empieza con `/`. Listá los que sí.
6. **Links resuelven:** cada link relativo apunta a un archivo existente. *(Roto =
   warning; listalos.)*
7. **Índices:** cada carpeta con conceptos tiene `index.md`, sus entradas coinciden con los
   archivos reales (sin entradas viejas ni faltantes) y **el texto de cada entrada es la
   `description` del concepto**. Cada carpeta lista sus subcarpetas, y la raíz además los
   conceptos que vivan en ella (`roadmap.md`, `glossary.md`), agrupados por `type`.
8. **Entrypoint:** `AGENTS.md` apunta a `knowledge/index.md`, o el `README` apunta a
   `knowledge/`.
9. **Sin carpetas vacías.**

**FAIL (= exit 1 del script)** solo si hay un **ERROR**: frontmatter **ausente / sin
cerrar / que no es un mapping / no-UTF-8** (item 1), `type` faltante (2), **link absoluto
`/`** (5), o **YAML inválido**. El resto — defaults faltantes, index con frontmatter,
`timestamp`/fecha-de-log no-ISO, valor con `:` sin comillas, links rotos, índices
desfasados — es **WARN** y NO hace fallar (salvo `--strict`). Reportá los warnings igual.

# Nivel 2 — Calidad (heurístico)

Reportá smells, no des pass/fail. El **drift descriptivo** es el que importa y el único que
necesita método —un concepto que contradice el código se ve igual de prolijo que uno
correcto—, así que va primero y con procedimiento:

1. **Corré `python3 scripts/okf_stale.py knowledge`** (si está). Con `resource:` +
   `timestamp` + git te dice dónde mirar: qué conceptos apuntan a código que se movió mucho,
   cuáles apuntan a algo que ya no existe, y cuáles tienen el sello de frescura podrido. No
   lee código ni gasta tokens. **Auditar el bundle entero es lo que hace que nadie lo audite.**
2. **Por cada concepto de esa lista corta, buscá la contradicción, no la confirmación.**
   Listá qué afirma sobre el código (un conteo, una ruta, un nombre, una flag, "existe X",
   "esto está en curso") y andá a la fuente a intentar **refutarlo**.
3. **Clasificá:** *doc podrido* (gana el código, se corrige el concepto) · *ambos cambiaron*
   (se deprecia, no se parcha) · *lo que contradice es normativo* → no es este nivel, va al 4.
4. **Reportá; no resuelvas solo.** Quién tiene razón lo decide el usuario, sobre todo si el
   arreglo obvio es borrar el documento.

> Un dato transcrito a mano es un dato que va a driftear: si el hallazgo es un valor copiado,
> el arreglo duradero es que **deje de estar copiado** (`resource`, un link, o generarlo).

Otros smells, sin método (se ven leyendo):
- Conceptos que **repiten el código** en vez de capturar el *por qué*.
- **Duplicación** de la fuente (código/schema copiado en vez de linkeado).
- Conceptos **huérfanos** (sin cross-links entrantes ni salientes).
- `AGENTS.md` o `index.md` **demasiado grandes** (rompe progressive disclosure)
  *(corré `python3 scripts/okf_lint.py knowledge --budget`: separa la prosa del kit —que
  tiene su propio techo de ~7000— de la tuya, que se suma encima. Todo se paga en cada
  turno de cada sesión.)*.
- `description` de varias oraciones o genéricas.
- `Decision` sin contexto/consecuencias.
- Falta de **conocimiento tribal** (decisiones, gotchas, runbooks): estructura linda
  pero vacía de contenido no obvio.

# Nivel 3 — Outcome (automatizable + manual)

Vos ya viste el código, así que **no** podés actuar de agente en frío. Tenés dos vías:

**Automatizada (test de regresión):** generá 5-10 preguntas que haría un recién
llegado (operativas, de diseño, de dominio/datos) + **una trampa** (algo que NO esté
en el bundle). **Lanzá un subagente** (Task/Agent) con contexto fresco y la consigna:
"leé **solo** `knowledge/`, no abras el código, respondé citando el archivo de cada
respuesta; si algo no está, decí 'no está en el contexto'". Para un entorno aislado,
materializalo con `python3 scripts/okf_coldtest.py knowledge --out <dir>` (copia solo
el bundle, sin código ni `.git`) y apuntá ahí al subagente; **verificá que las citas
caigan dentro del bundle** (el aislamiento de un subagente es por instrucción, no
físico). Calificá: ✅ correcta y citada · ⚠️ parcial · ❌ inventó ·
🟦 admitió bien la trampa. **Verificá que las citas apunten a `knowledge/`.** Bar:
≥80% en ✅, trampa en 🟦, navegó por índices. Cada ❌ = concepto faltante → `okf-update`.

**Manual (cross-vendor):** un subagente es el mismo modelo, así que para probar "con
la IA que sea", entregale al usuario el prompt listo para pegar en una CLI/IA nueva
(Claude, Gemini, Cursor…). Es lo único que valida portabilidad real entre herramientas.

# Nivel 4 — Cumplimiento (opcional: ¿el código respeta lo que el bundle prescribe?)

Los niveles 1-3 preguntan "¿está bien el bundle?"; este pregunta al revés. Es una
**auditoría con criterio** (lee código), así que no va en CI y no se corre siempre.

1. Listá lo **normativo auditable**: `decisions/` con `status: accepted`, convenciones, y las
   reglas duras del `AGENTS.md`. Ignorá `proposed` y `superseded`.

   **Del rumbo, solo la sección "Ahora".** Visión, "Después" y no-goals son intención pura:
   que el código no los haya alcanzado es trabajo pendiente, no una violación, y auditarlos
   sería falso positivo. Pero **"Ahora" afirma estado del código** —que ese trabajo está en
   curso— y eso sí es chequeable: un ítem cuyo trabajo **ya está terminado** o que nunca
   arrancó es una afirmación podrida, y un roadmap que miente sale más caro que no tenerlo.
2. Por cada una **buscá su violación** (no su confirmación). Si la decisión trae su forma de
   verificarla (comando/grep/test), corré esa; si no, derivá la señal del texto.
3. Clasificá: **violación** (el código contradice) · **decisión obsoleta** (la realidad
   cambió → se supersede, no se borra) · **ambigua** (no se puede chequear → afilar el doc).
4. **Reportá; no resuelvas solo.** Cada violación tiene dos salidas legítimas: arreglar el
   código, o superseder la decisión. **Nunca** edites la decisión para que coincida con lo
   que el código hace hoy — eso borra el *por qué* y es justo lo que este nivel caza.

Si el bundle tiene muchas decisiones, priorizá las del área que se está tocando y las que
tengan verificación declarada.

# Salida

Emití el reporte con este formato:

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

Terminá ofreciendo correr
`okf-update` para los fixes del bundle — pero las **violaciones del Nivel 4 no se
"arreglan" con `okf-update`**: se llevan al usuario para decidir código vs supersede.
