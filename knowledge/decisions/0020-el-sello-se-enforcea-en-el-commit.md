---
type: Decision
title: El sello de frescura se enforcea en el commit, porque es la base de la detección de drift
description: "El hook avisa si un concepto se editó sin bumpear su timestamp, porque okf_stale.py calcula todas sus señales desde ese valor y un sello podrido degrada la detección del bundle entero."
status: accepted
verify: grep -q "timestamp" templates/hooks/pre-commit
tags: [drift, enforcement, hook]
timestamp: 2026-07-30T00:00:00Z
resource: ../../templates/hooks/pre-commit
---

# Contexto

La [0015](0015-rankear-el-drift-antes-de-auditarlo.md) puso a `okf_stale.py` a rankear dónde
buscar divergencia entre el bundle y el código usando `resource` + `timestamp` + git. Pero
**nada obligaba a mantener el `timestamp`**: el linter chequea que exista y que sea ISO, no que
corresponda a la última edición real.

Eso no es un detalle cosmético. El `timestamp` es el **origen de coordenadas** del ranker: los
"sospechosos" se calculan contando commits de la fuente *desde ese valor*. Un sello podrido no
solo no avisa de su propio concepto — hace que el resto de las señales midan mal. El propio kit
lo demostró: en la primera corrida del ranker sobre su dogfood después de la 0.7.0, tres
conceptos editados el día anterior salieron como `SELLO PODRIDO`, y los había editado un agente
que conocía la regla y aun así no la aplicó.

# Decisión

El **pre-commit hook** que el kit instala gana una tercera función: **avisa** (no bloquea) si un
concepto staged cambió y su línea `timestamp` quedó igual que en `HEAD`.

- **Avisa, no bloquea**: la conformidad es lo único bloqueante (§1 del hook). Un sello viejo no
  hace al bundle inválido; hace que la próxima auditoría mire para el lado equivocado.
- **Se juzga lo STAGED, no el working tree** (`git show :archivo` vs `git show HEAD:archivo`) —
  igual que el chequeo de conformidad, y por la misma razón: se valida lo que se va a commitear,
  y el working tree no se toca.
- Se saltean `index.md`, `log.md` y todo lo que empiece con `_` (no son conceptos), y los
  archivos **nuevos** o sin `timestamp` previo (ahí no hay sello que bumpear; que falte ya lo
  avisa el linter).

Queda una división limpia: el **hook previene** en el momento de la edición, `okf_stale.py`
**detecta** después. Antes solo existía la segunda mitad.

# Consecuencias

- La señal del ranker deja de degradarse sola con el uso, que era su falla de diseño más
  silenciosa: cuanto más se editaba el bundle, menos servía para encontrar drift.
- El linter **no** hace este chequeo, y es a propósito: no tiene acceso a git (corre sobre un
  directorio, incluso sobre una copia aislada como en el test en frío). El chequeo vive donde
  está la información.
- Un renombre de archivo aparece como archivo nuevo y no dispara el aviso. Es un gap conocido y
  aceptado: cazarlo pediría seguir renames, y el costo no lo paga.
