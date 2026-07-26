---
type: Reference
title: El formato OKF (spec condensada)
description: Resumen de las reglas del formato — frontmatter, cross-links, index.md, log.md, conformidad.
resource: ../../OKF-SPEC.md
tags: [okf, spec, format]
timestamp: 2026-07-26T00:00:00Z
---

`OKF-SPEC.md` es la especificación condensada y self-contained del Open Knowledge Format
(v0.1), derivada de la spec oficial de Google Cloud pero enfocada en contexto de software.
Lo que hay que recordar:

- **Frontmatter** (YAML entre `---`): `type` es el **único requerido**; recomendados
  `title`, `description` (una frase), `resource`, `tags`, `timestamp` (ISO 8601). Se pueden
  agregar claves extra; los consumidores deben preservarlas.
- **Body**: markdown estructurado. Headings convencionales: `# Schema`, `# Examples`,
  `# Citations`.
- **Cross-links**: relativos al archivo (`../dir/x.md`); **nunca empezar con `/`**. Ver
  [la decisión de links](../decisions/0001-relative-links-over-absolute.md).
- **`index.md`**: listado para [progressive disclosure](../concepts/progressive-disclosure.md);
  sin frontmatter salvo `okf_version` (y `kit_version`) en la raíz.
- **`log.md`**: historial por fecha ISO `YYYY-MM-DD`, más nuevas primero.
- **Conformidad** (§8): solo `type` + frontmatter parseable son duros; el resto es guía
  blanda ([consumo permisivo](../decisions/0002-permissive-consumption.md)).

Para *testear* un bundle hay cuatro niveles (conformidad / calidad / outcome, y cumplimiento
—¿el código respeta lo normativo?— opcional y periódico), detallados en
`reference/verification.md` — el Nivel 1 lo automatiza [el linter](../runbooks/lint-the-bundle.md).

# Citations
[1] [OKF-SPEC.md (en este kit)](../../OKF-SPEC.md)
[2] [Spec oficial OKF — Google Cloud](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
