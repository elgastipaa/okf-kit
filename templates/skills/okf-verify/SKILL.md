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

# Nivel 1 — Conformidad (objetivo, PASS/FAIL)

**Corré el script** (determinista, solo stdlib, sin instalar nada) y parseá su
salida — es la fuente de verdad del Nivel 1:

```
python3 scripts/okf_lint.py knowledge
```

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
7. **Índices:** cada carpeta con conceptos tiene `index.md` y sus entradas coinciden
   con los archivos reales (sin entradas viejas ni faltantes). La raíz lista **todos** los
   subdirs (el script todavía no lo valida — chequealo acá) y los conceptos que vivan en la
   raíz (`roadmap.md`, `glossary.md`), agrupados por `type`.
8. **Entrypoint:** `AGENTS.md` apunta a `knowledge/index.md`, o el `README` apunta a
   `knowledge/`.
9. **Sin carpetas vacías.**

**FAIL (= exit 1 del script)** solo si hay un **ERROR**: frontmatter **ausente / sin
cerrar / que no es un mapping / no-UTF-8** (item 1), `type` faltante (2), **link absoluto
`/`** (5), o **YAML inválido**. El resto — defaults faltantes, index con frontmatter,
`timestamp`/fecha-de-log no-ISO, valor con `:` sin comillas, links rotos, índices
desfasados — es **WARN** y NO hace fallar (salvo `--strict`). Reportá los warnings igual.

# Nivel 2 — Calidad (heurístico)

Reportá smells, no des pass/fail:
- Conceptos **descriptivos** que **contradicen el código** (smell grave: gana el código,
  el concepto es el bug). *(Si el que contradice es normativo —decisión aceptada,
  convención— eso NO es este smell: es una violación del código y va al Nivel 4.)*
- Conceptos que **repiten el código** en vez de capturar el *por qué*.
- **Duplicación** de la fuente (código/schema copiado en vez de linkeado).
- Conceptos **huérfanos** (sin cross-links entrantes ni salientes).
- `AGENTS.md` o `index.md` **demasiado grandes** (rompe progressive disclosure)
  *(regla gruesa: el `AGENTS.md` instalado no debería pasar los ~7000 caracteres —
  se paga en cada turno de cada sesión)*.
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
   reglas duras del `AGENTS.md`. Ignorá `proposed` y `superseded`. **El rumbo y los cambios
   abiertos NO se auditan acá**: que el código todavía no los haya alcanzado es trabajo
   pendiente, no una violación — reportarlos sería un falso positivo.
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
- smells encontrados (o "ninguno")

## Nivel 3 — Outcome
- Set de preguntas usado
- Cómo correrlo (prompt de CLI en frío) — o resultados si ya se corrió

## Nivel 4 — Cumplimiento (si se corrió)
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
