# OKF kit — Contrato para agentes que trabajan SOBRE el kit

Este repo (`okf-kit`) **es el kit OKF**: la guía + templates + tooling para montar
ingeniería de contexto (OKF) en *otros* repos. Es el **toolsmith**, no un repo de producto.
(El `README.md` orienta a un humano; este archivo es el contrato para una IA que **edita el kit**.)

> ¿Venís a **aplicar OKF a otro repo**? No es acá: leé `GUIDE.md` y usá `templates/`.
> Este contrato es solo para **modificar el kit en sí**.

## Reglas duras (específicas del kit)

- **Una fuente de verdad por regla/procedimiento; el resto apunta, no re-escribe.** La causa raíz
  de los bugs de este kit fue re-statear el mismo procedimiento en N archivos y que derivaran. Si
  tocás una regla, editá su archivo canónico y dejá punteros desde el resto.
- **Las herramientas se consumen desde `templates/`; NO se instalan en la raíz del kit.** El
  `scripts/okf_selfcheck.py` corre `templates/scripts/okf_lint.py`. Copiar el linter o los skills a
  la raíz crearía **dos copias** = la deriva que el kit existe para evitar. (Lo único kit-only en
  `scripts/` es `okf_selfcheck.py`.)
- **`VERSION` es la fuente de verdad de la versión.** Los templates usan `{{KIT_VERSION}}`; el
  dogfood `knowledge/index.md` debe estampar el mismo valor (el selfcheck lo exige).
- **Cada fix se testea adversarialmente antes de darlo por hecho** — la lección de esta historia:
  dos "arreglos" metieron regresiones. Para el hook, probá partial-staging + integridad del working-tree.

## 1. Antes de actuar — leé el contexto

El "qué" y el "por qué" del kit viven en **`knowledge/`** (el kit se dogfoodea en su propio formato
OKF). Empezá por [`knowledge/index.md`](knowledge/index.md). El proceso de desarrollo y el gate de
release están en [`DEVELOPING.md`](DEVELOPING.md).

**El rumbo y el trabajo en curso del kit** están en [`knowledge/roadmap.md`](knowledge/roadmap.md)
(visión, qué sigue, no-goals) y en `knowledge/_changes/` (un doc por cambio en curso). El kit
**se aplica a sí mismo** esta capa: regís por **los mismos disparadores que el kit instala en
los repos destino** —están enumerados en `templates/AGENTS.md` §1, y ninguno requiere que el
usuario los pida—, y el procedimiento es `templates/skills/okf-plan/SKILL.md`. Seguilos desde
`templates/`, no los copies a la raíz (ver "Reglas duras").

## 2. Mientras trabajás — mantené el kit consistente

Si cambiás el kit, actualizá el bundle `knowledge/` que lo documenta (es un bundle OKF normal:
seguí su propio procedimiento de mantenimiento — concepto en la carpeta correcta, `index.md`,
`log.md`) y registrá decisiones de diseño en `knowledge/decisions/`. Una verdad, un lugar.

Si el cambio es no trivial, abrí su doc en `knowledge/_changes/` **antes** de codear (mini-spec +
tareas) y **cosechalo** al cerrar (decisiones al bundle, roadmap al día, doc borrado). Es la misma
capa de futuro que el kit instala en los repos destino — si no la usás acá, no la estás probando.

**Las `decisions/` del kit y las "Reglas duras" de arriba son NORMATIVAS** (`OKF-SPEC.md` §3.5):
obligan al código del kit. Si encontrás kit que las viola, el bug es el kit — reportalo y ofrecé
arreglarlo o **superseder** la decisión; no edites la decisión para que coincida con lo que el
código hace hoy.

## 3. Antes de cerrar — verificá (gate de release)

Corré **`python3 scripts/okf_selfcheck.py`** (consistencia interna: linter limpio sobre el dogfood,
`kit_version` sembrado, keep-alive y capa de futuro coincidentes, rama normativa presente,
presupuesto del contrato, instalación mínima sin huérfanos, material instalado autosuficiente,
referencias que resuelven). Si bumpeás `VERSION`,
re-estampá el dogfood. Para cambios grandes, corré el cold-review de 4 lentes. Detalle en `DEVELOPING.md`.

## Mapa rápido

- **Formato** OKF: `OKF-SPEC.md` · **Aplicar a un repo:** `GUIDE.md` · **Perfiles:** `reference/profiles.md`
- **Templates para repos destino:** `templates/` (no los confundas con la instancia del propio kit)
- **Dev/release del kit:** `scripts/okf_selfcheck.py`, `DEVELOPING.md`
