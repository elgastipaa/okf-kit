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
Claude Code o seguilo directo desde cualquier agente.) Hay tres niveles; corré 1 y 2 vos mismo
leyendo los archivos, y **preparás** el 3 para que lo corra el usuario en una CLI
nueva. Referencia completa: `reference/verification.md` (si está disponible).

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
   con los archivos reales (sin entradas viejas ni faltantes). La raíz lista subdirs.
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
- Conceptos que **repiten el código** en vez de capturar el *por qué*.
- **Duplicación** de la fuente (código/schema copiado en vez de linkeado).
- Conceptos **huérfanos** (sin cross-links entrantes ni salientes).
- `AGENTS.md` o `index.md` **demasiado grandes** (rompe progressive disclosure)
  *(medible con el token-sizer opcional — ver `reference/optional-tools.md`)*.
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

# Salida

Emití el reporte con el formato de `reference/verification.md` (Resultado, Nivel 1
con checklist, Nivel 2 smells, Nivel 3 set de preguntas + prompt, tabla de Issues por
severidad, Veredicto en una línea). Terminá ofreciendo correr `okf-update` para los fixes.
