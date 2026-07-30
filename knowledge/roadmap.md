---
type: Roadmap
title: Rumbo del kit OKF
description: "Hacia dónde va el kit hoy: ingeniería de contexto completa (pasado, presente y futuro) aplicable a cualquier repo sin tooling."
tags: [roadmap]
timestamp: 2026-07-30T00:00:00Z
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

**Adopción: lo que falta para que el kit se pueda usar sin conocer al autor.**

- **Un repo de ejemplo clonable** (antes/después de un init real, con el diff visible). Hoy la
  única prueba navegable es el dogfood `knowledge/`, que está enterrado, y los mini-bundles de
  `reference/examples.md`. Es lo que convierte a un desconocido.
- Mueblería de adopción: badges, topics de GitHub, `CONTRIBUTING.md`, un asciinema de 30s del
  init. Barato y hoy no existe nada.
- Publicar la medición del harness de eval (turnos/tokens/acierto en los tres conejillos).
  **Es el diferencial que ningún competidor tiene** —el kit es el único que se mide a sí
  mismo— y hoy `/eval/` está gitignoreado. Requiere decidir qué se publica y qué no.

**De la comparación con `harness-sdd`** (el revisor con contexto fresco ya se cerró en la
[0021](decisions/0021-la-auditoria-no-se-auto-aprueba.md); los otros tres roles son no-goal):

- **Estado de sesión en vivo**: un `_changes/` captura el *cambio*, no *dónde quedó la sesión*
  si el contexto se corta a mitad de una tarea. Medir si hace falta antes de agregar archivos.
- **Estado WIP machine-readable**: el roadmap es prosa, así que "≤1 cosa en curso" no lo puede
  enforcear ni el linter ni el hook. Convertirlo en invariante chequeable, sin ceremonia.

**Cerrar lo que quedó escrito y sin medir.**

- Los dos escenarios que la [0015](decisions/0015-rankear-el-drift-antes-de-auditarlo.md) dejó
  sin verificar con un agente: que la auditoría reporte un ítem de "Ahora" ya terminado, y que
  el hallazgo llegue al usuario clasificado sin resolverse solo.
- Si el doc de `_changes/` se saltea sistemáticamente cuando el agente cree que termina en una
  corrida, y si el umbral debería ser "¿podría no terminar en esta sesión?" en vez de "¿es no
  trivial?" ([0014](decisions/0014-future-layer-measured.md)).

**Deudas del tooling.**

- El juez `--grade` del harness de medición no sirve para preguntas de comportamiento: puntuó
  bien una respuesta con premisa falsa. (La métrica de contexto ya se arregló en 0.7.1.)
- El pre-commit hook del kit valida el working tree en vez de lo staged, al revés que el que
  el kit shippea a otros repos. CI ataja el escape, por eso no es urgente.
- Higiene de `_changes/` (cambios zombie) en el linter — **solo si** la medición muestra que
  pasa seguido.

# No-goals (por ahora)

- **Los otros tres roles de `harness-sdd`** (leader / spec_author / implementer): ceremonia de
  equipo grande, sin evidencia de que paguen para un usuario solo. El único que pagaba era el
  revisor, y ya está ([0021](decisions/0021-la-auditoria-no-se-auto-aprueba.md)).
- **Un harvester con contexto fresco:** el harvest necesita recordar qué pasó, y eso lo tiene la
  sesión que hizo el trabajo. Contexto fresco sirve para auditar, no para recordar.

- Reimplementar spec-driven development completo (specs vivas por capability,
  estilo OpenSpec): el kit cubre el ciclo cambio→harvest; para más que eso, se
  documenta interop, no se compite.
- Tooling nuevo obligatorio para la capa de futuro: sigue siendo markdown + git
  (la [decisión 0004](decisions/0004-vendor-neutral-no-external-apps.md) manda).
