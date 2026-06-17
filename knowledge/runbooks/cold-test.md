---
type: Runbook
title: Correr el cold test (Nivel 3 — la prueba de fuego)
description: Pasá preguntas a un agente en frío con acceso solo al bundle y calificá las respuestas.
resource: ../../reference/verification.md
tags: [ops, verification, cold-test]
timestamp: 2026-06-17T00:00:00Z
---

# Cuándo
Periódicamente, como auditoría. Mide lo único que importa: **¿un agente sin contexto
previo, leyendo solo el bundle, entiende el proyecto?** Es el Nivel 3 de verificación.

# Pasos
1. Armá **5-10 preguntas** que haría un recién llegado, mezclando tipos: operativas
   ("¿cómo corro X?"), de diseño ("¿por qué X sobre Y?"), de dominio, y **una trampa**
   (algo que NO esté en el bundle).
2. Opcional, para aislamiento real, armá un dir limpio con solo el bundle:
   ```bash
   python3 templates/scripts/okf_coldtest.py knowledge --out /tmp/coldtest
   ```
   Copia solo `knowledge/` (+ `AGENTS.md`), sin código ni `.git`, e imprime el prompt.
3. Abrí una **CLI nueva en frío** (o un subagente) en ese dir y pegá el prompt: "Tenés
   acceso solo a `knowledge/`, no leas el código, respondé citando el archivo de cada
   respuesta; si algo no está, decí 'no está en el contexto'".
4. Calificá: correcta y citada / parcial / incorrecta o inventada / admitió bien la trampa.

# Notas / gotchas
- **Bar de aprobación:** >=80% de las preguntas reales correctas y citadas, la trampa
  admitida, y que el agente **haya navegado los `index.md`** (no leído todo).
- Cada respuesta incorrecta/parcial = un **concepto faltante o débil** → escribilo
  (`okf-update`) y re-testeá. Es el feedback loop del [ciclo de vida](../concepts/lifecycle.md).
- La forma **más fiel** (y la única que prueba portabilidad cross-vendor) es correrlo en
  **otra IA**, a mano — un subagente es el mismo modelo. Ver `reference/verification.md`.
