---
type: Concept
title: Progressive disclosure
description: El agente ve un mapa chico (index.md) y baja solo a los conceptos que necesita.
tags: [okf, navigation, context-window]
timestamp: 2026-06-17T00:00:00Z
---

**Progressive disclosure** es el mecanismo que evita reventar la ventana de contexto: en
vez de cargar todo el bundle, el agente lee un **mapa chico** y baja solo al detalle que
le hace falta.

Lo implementan los archivos `index.md`: cada uno lista qué hay en su scope (subdirectorios
en la raíz; conceptos agrupados por `type` en las hojas), con la `description` de una
frase de cada concepto como snippet. El agente decide desde ahí qué abrir.

# Consecuencias prácticas
- El **entrypoint** (`AGENTS.md`) y los `index.md` deben quedar **chicos** — son índices,
  no enciclopedias. Un `index.md` enorme es un smell de Nivel 2 (ver
  [verificación](../references/okf-format.md)).
- El tamaño *total* del bundle no importa mientras cada `index.md` sea navegable de un
  vistazo. Cuándo partir un bundle que creció: ver [el ciclo de vida](lifecycle.md) y la
  decisión sobre [links relativos](../decisions/0001-relative-links-over-absolute.md), que
  hacen que mover archivos sea barato.
- Las `description` tienen que ser **una sola frase** y útiles como snippet — no genéricas.
