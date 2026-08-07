---
type: Decision
title: "El drift se rankea antes de auditarlo: la auditoría no se corre porque es cara, no porque falte"
description: Un script determinista usa resource + timestamp + git para decir dónde buscar divergencia, y el Nivel 2 gana el método que solo tenía el Nivel 4.
status: accepted
origen: dictado
verify: python3 scripts/okf_selfcheck.py 2>&1 | grep -q "PASS.*da método al Nivel 2"
resource: templates/scripts/okf_stale.py
tags: [verification, drift, enforcement]
timestamp: 2026-07-26T00:00:00Z
---

# Contexto

La [medición de la capa de futuro](0014-future-layer-measured.md) dejó dos casos de contexto
falso escrito en el bundle. El kit ya tenía con qué cazarlos —`okf-verify` Nivel 2 (drift
descriptivo) y Nivel 4 (cumplimiento), con la regla de que **el usuario decide** si el bug es
el código o el documento— pero no se usaban, y no por ignorancia:

- El **Nivel 2 no tenía método**. El 4 dice "por cada norma buscá su violación, no su
  confirmación"; el 2 decía "reportá los smells que veas". Y lo descriptivo es justo la
  dirección donde vive el contexto falso.
- **Nada los dispara**: "opcional, periódico", fuera de CI. Auditar el bundle entero contra el
  código es caro; un chequeo que hay que acordarse de correr no se corre.

Agregar *más* chequeo completo no arreglaba nada. El cuello era el **costo de decidir dónde
mirar**.

# Decisión

**Separar el ranking de la auditoría.** Un script determinista dice *dónde* buscar; el juicio
sobre si algo está mal sigue siendo humano/agente.

`templates/scripts/okf_stale.py` (se instala en el repo destino) usa tres señales, todas con
git + el frontmatter que el bundle **ya tiene**, sin leer código y sin gastar un token:

1. **`resource:` que ya no existe** → drift confirmado, no sospecha.
2. **`timestamp` anterior al último commit del propio concepto, con ≥2 commits** → el sello de
   frescura está podrido, y las otras señales se calculan *desde* ese valor.
3. **Churn desde el `timestamp`** → cuántos commits tocaron la fuente. No prueba que el
   concepto esté mal: dice dónde es más probable.

**No es un gate y no da pass/fail.** `okf_lint.py` responde "¿es OKF válido?"; esto responde
"¿por dónde empiezo?". La antigüedad no es un defecto de conformidad, y meterlo en el linter
lo habría hecho fallar por algo que requiere criterio.

**El Nivel 2 gana método**, espejando el del 4: rankear → buscar la **contradicción** y no la
confirmación → clasificar (*doc podrido* / *ambos cambiaron* / *es normativo, va al 4*) →
reportar sin resolver solo. Y **del rumbo se audita solo "Ahora"**: Visión, "Después" y
no-goals son intención pura y auditarlos sería puro falso positivo, pero "Ahora" afirma estado
del código.

# Consecuencias

- **`resource:` dejó de ser decorativa.** Se usa mucho más de lo que se suponía (7/9 conceptos
  en un conejillo, 8/13 en otro, 14/27 en el dogfood) y **nadie la leía**, ni el linter. El
  ranking no necesitó convención nueva. Es el segundo caso del kit de una clave escrita con
  cuidado y nunca consumida — ver [0016](0016-material-instalado-vs-contenido.md) para el
  tercero; `authority:` sigue pendiente.
- **Encontró drift real en su primera corrida, sobre el propio kit**: un runbook que había
  quedado desalineado del `GUIDE` unas horas antes, y 5 conceptos con el sello podrido.
- **El criterio "sobre limpio no inventa" fue lo más rentable de la spec.** Cazó dos defectos:
  el sello comparaba instantes (marcaba como podrido lo editado el mismo día) y trataba igual
  "editado sin re-sellar" que "creado con fecha retroactiva" — y ese falso positivo además
  *tapaba* la clasificación real. Un detector que inventa se deja de correr en dos semanas, que
  es exactamente cómo el Nivel 4 llegó a no correrse.
- **Un dato transcrito a mano es un dato que va a driftear**: si el hallazgo es un valor
  copiado, el arreglo duradero no es corregirlo sino que deje de estar copiado
  ([0010](0010-generated-volatile-facts.md)).

# Verificación

```
python3 scripts/okf_stale_test.py     # 8 casos: encuentra lo sembrado, y sobre limpio se calla
python3 scripts/okf_selfcheck.py      # el método del Nivel 2 y el recorte a "Ahora" no se caen
```

**Alcance de lo verificado.** Cuatro de los seis escenarios del cambio se probaron
**ejecutando** (las tres señales sobre drift sembrado, el silencio sobre limpio, el ranking sin
tokens, los conceptos sin `resource` visibles). Dos quedaron **escritos y con assert de
presencia, pero sin medir con un agente**: que la auditoría reporte un "Ahora" ya terminado, y
que el hallazgo llegue al usuario clasificado. Está en "Después" del rumbo; no se dan por
buenos.
