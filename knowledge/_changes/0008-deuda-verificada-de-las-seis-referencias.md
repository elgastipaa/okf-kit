---
type: Change
title: La deuda que encontró el análisis de seis herramientas del ecosistema
description: "Cinco arreglos que no necesitan medición: subárboles invisibles, maquinaria pisada sin mirar, reglas sin identidad y disparadores que solo existen en castellano."
status: active
timestamp: 2026-08-03T00:00:00Z
---

# Por qué

Se analizaron seis repos del ecosistema (OpenSpec, rulebook-ai, context-engineering-intro,
mattpocock/skills, speccy, awesome-vibe-coding) buscando qué robar. Salió un plan de cuatro
fases; **esta es la fase 0: lo que no necesita medición porque son bugs o deuda verificada.**

Dos de los hallazgos son contra nosotros y están confirmados a mano, no reportados:

- **El linter no detecta subárboles inalcanzables.** Reproducido: raíz → `mid/` sin `index.md`
  → `deep/` con conceptos. El linter no dice nada. Los chequeos son **locales** (cada carpeta
  contra su propio índice) y nunca transitivos desde la raíz, así que existe contenido al que
  nadie llega navegando desde el entrypoint, con el gate en verde. Es el trabajo que hace el
  `resolve` de speccy.
- **La maquinaria instalada se pisa incondicionalmente.** `install_machinery` reemplaza
  skills, linter y hook sin mirar si el usuario los editó. Es la misma familia de pérdida de
  datos que arregló la 0.7.4 para el entrypoint, un nivel más abajo y todavía abierta.

Y uno de mercado que bloquea todo lo demás: **el 100% de este mercado escribe en inglés** y
nuestros disparadores están solo en castellano. Nadie que tipee *"the AI keeps forgetting my
project"* dispara nada. Los `description:` de los skills son **ejecutables**, no prosa: son lo
primero que hay que traducir.

# Resultado esperado (la spec)

- **CUANDO** el bundle tiene un concepto al que no se llega navegando desde `index.md`
  → **ENTONCES** el linter lo reporta, aunque su carpeta tenga su propio índice bien formado.
- **CUANDO** `--upgrade` va a reemplazar un archivo de la maquinaria que el usuario editó
  → **ENTONCES** lo detecta y **no lo pisa en silencio**; distingue "es mi versión vieja" de
  "lo editaste vos", y para eso cada archivo instalado lleva su sello de versión.
- **CUANDO** el kit deja de shippear un archivo que antes instalaba → **ENTONCES** el upgrade
  lo nombra en vez de dejarlo huérfano para siempre.
- **CUANDO** alguien describe su síntoma **en inglés** → **ENTONCES** el skill correcto se
  dispara igual que en castellano.
- **CUANDO** un usuario quiere silenciar una regla del linter → **ENTONCES** puede hacerlo por
  **id estable**, sin forkear el kit y sin depender de la redacción en castellano del mensaje.

# Fuera de alcance

- Todo lo de las fases 1-3 del plan: `okf-migrate` al frente, `checks.md`, `--pack`, el
  golden-set de "por qué", la palabra líder `fuente primaria`, la dieta del contrato y la
  lista de matar. Cada una tiene su propia condición.
- **Marcadores en el archivo del usuario.** Descartado con evidencia: OpenSpec los tuvo y los
  abandonó, y el `AGENTS.md` de la raíz de su propio repo pesa 0 bytes como sedimento de esa
  migración.
- Nada que agregue prosa al contrato instalado: la medición dice que no mueve el acierto.

# Plan / Tareas

- [x] Alcanzabilidad transitiva desde la raíz en `okf_lint.py` + su rotura.
- [x] Clasificación de tres desenlaces (idéntico / distinto / ausente) antes de reemplazar
      material instalado, y aviso que **no afirma** que hubo edición: una versión vieja
      también difiere.
- [x] Sello de versión por archivo instalado, leyendo **todos** los archivos (OpenSpec lee el
      primero y extrapola; ese es su bug, no lo copiamos).
- [ ] **Pendiente** — Inventario de archivos retirados, para que un archivo que el kit dejó de shippear no
      quede huérfano.
- [x] Disparadores de `okf-init` y `okf-migrate` **en inglés además de castellano**.
- [ ] **Pendiente** — Ids estables de regla en el linter + `--skip`.
- [x] Gate y las tres suites (115/115, 59/59, 22/22, 9/9) en verde, con rotura por cada assert nuevo.

# Decisiones y descubrimientos en el camino

- El eje correcto de una migración **no es automático vs manual, es separable vs entrelazado**
  (OpenSpec). Nosotros nos plantamos en todos los casos; ellos automatizan lo separable y solo
  piden intervención en lo que no lo es. Nuestras tres cubetas coinciden con las suyas por
  evolución convergente, lo que es buena señal del diseño de la 0024.
- Externalizar reglas a datos **no salva de la deriva**: speccy mantiene una segunda copia de
  sus reglas para documentarlas y ya divergió. Por eso los ids van en el código, no en un YAML
  paralelo.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" (probado de verdad, no asumido)
- [ ] Decisiones/descubrimientos → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"
- [ ] Borrar este archivo (git conserva la historia)
