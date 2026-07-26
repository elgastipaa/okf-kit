---
type: Roadmap
title: Rumbo del kit OKF
description: "Hacia dónde va el kit hoy: ingeniería de contexto completa (pasado, presente y futuro) aplicable a cualquier repo sin tooling."
tags: [roadmap]
timestamp: 2026-07-26T00:00:00Z
---

# Visión

Que aplicar `okf-kit` a un repo cualquiera —especialmente uno desarrollado
conversando con IAs— deje **ingeniería de contexto completa**: el pasado ordenado
(`decisions/`), el presente reconocible en segundos (bundle + entrypoint) y el
trabajo futuro gestionado (rumbo + cambios con spec y harvest), todo en markdown +
git, sin apps externas.

# Ahora (en curso)

- (nada activo)

# Después (próximo, en orden)

- Medir si el doc de `_changes/` se saltea sistemáticamente cuando el agente juzga que
  termina en una sola corrida, y si conviene cambiar el umbral del disparador a "¿podría no
  terminar en esta sesión?" ([decisión 0014](decisions/0014-future-layer-measured.md)).
- Arreglar los defectos del harness de medición que destapó la 0014: el resumen de
  `run-eval.py` reporta `input_tokens` (ruido: 6–12) en vez de `cache_read` (85K–300K), que es
  el contexto realmente leído; y el juez `--grade` no sirve para preguntas de comportamiento.

- Que el linter valide lo que hoy solo valida el checklist manual: la clave `authority:`
  (vocabulario cerrado, hoy `authority: banana` pasa `--strict` en silencio), que cada
  carpeta esté listada en el `# Subdirectories` de su padre (hoy se puede agregar un
  subárbol entero invisible desde el entrypoint), y que el texto de cada entrada de
  `index.md` coincida con la `description` del concepto (hoy pueden divergir sin aviso, y
  el índice es lo primero que lee un agente). Los tres salieron del cold-review de 0.6.0.
- Que el pre-commit hook del kit valide **lo staged** en vez del working tree, como el que
  el kit shippea a otros repos (hoy commitea estado roto y bloquea commits sanos; CI ataja
  el escape, por eso no es urgente).
- Revisar si el linter debería chequear la higiene de `_changes/` (cambios zombie) —
  **solo si** la medición muestra que pasa seguido.

# No-goals (por ahora)

- Reimplementar spec-driven development completo (specs vivas por capability,
  estilo OpenSpec): el kit cubre el ciclo cambio→harvest; para más que eso, se
  documenta interop, no se compite.
- Tooling nuevo obligatorio para la capa de futuro: sigue siendo markdown + git
  (la [decisión 0004](decisions/0004-vendor-neutral-no-external-apps.md) manda).
