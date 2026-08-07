---
type: Decision
title: El kit se licencia Apache-2.0, no MIT
description: "Apache-2.0 porque OKF-SPEC.md es un derivado condensado del OKF de Google Cloud, que es Apache-2.0, y porque el grant de patentes baja la fricción de adopción."
status: accepted
verify: grep -q "Apache License" LICENSE && grep -q "Apache-2.0" README.md
tags: [licencia, adopcion]
timestamp: 2026-07-29T00:00:00Z
resource: ../../LICENSE
---

# Contexto

El repo **no tenía licencia**. Sin licencia explícita, el default legal es "todos los derechos
reservados": nadie en una empresa puede adoptarlo, por bueno que sea. Era el bloqueante de
adopción más barato de arreglar del kit.

MIT era el candidato obvio por popularidad, pero el `OKF-SPEC.md` de este repo es un
**restatement condensado y generalizado** del `okf/SPEC.md` de
[GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog),
que está bajo **Apache-2.0**. Un derivado de una obra Apache-2.0 tiene que cumplir sus términos
(conservar el aviso, declarar los cambios).

# Decisión

**Apache-2.0**, con un `NOTICE` que acredita el upstream y **declara qué se cambió**:
el formato se generaliza de catálogos de datos a contexto de cualquier dominio, el vocabulario
de `type:` se trata como abierto, y las reglas normativas de autoridad (§3.5), hechos volátiles
(§3.4) y capa de futuro son originales de este kit.

Dos razones, en orden: es la licencia **compatible** con el origen del `OKF-SPEC.md`, y su
**grant explícito de patentes** es lo que hace que legales de empresas la apruebe sin discutir
— exactamente el público que el kit quiere alcanzar.

# Consecuencias

- El `NOTICE` hay que mantenerlo si el `OKF-SPEC.md` se aleja más (o menos) del upstream.
- Apache-2.0 es más verbosa que MIT (202 líneas) pero no impone nada al que la usa: sigue siendo
  permisiva, sin copyleft.
- El crédito al OKF de Google Cloud pasa de ser cortesía del `README` a una obligación cumplida.
