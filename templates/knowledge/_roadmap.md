<!--
  TEMPLATE de rumbo. Va en la RAÍZ del bundle como knowledge/roadmap.md (sin el _).
  ES un concepto normal del bundle (el linter lo chequea y va linkeado en el
  index.md raíz): describe la intención VIGENTE del proyecto — hacia dónde va HOY.
  Es estado presente (de la intención), no un plan: acá NO van checkboxes ni
  progreso; eso vive en knowledge/_changes/ (un doc por cambio, ver el skill
  okf-plan). Cuando el rumbo cambia, se EDITA (como cualquier concepto), no se
  acumula historial. Borrá este comentario.
-->
---
type: Roadmap
title: {{Rumbo de <proyecto>}}
description: "{{Una frase: hacia dónde va el proyecto hoy y qué es lo próximo.}}"
tags: [roadmap]
timestamp: {{YYYY-MM-DDTHH:MM:SSZ}}
---

# Visión

{{2-4 frases: qué querés que sea este proyecto cuando "esté", para quién y qué
resuelve. Esto es lo que evita que el proyecto derive feature a feature. Si no
podés escribirlo, es la primera conversación a tener con el usuario.}}

# Ahora (en curso)

{{Los cambios activos, cada uno como link a su doc en `_changes/`. Pocos a la vez
(idealmente 1-3): muchos "en curso" = ninguno en curso. Ej:}}
- {{[Guardar partida](_changes/0001-guardar-partida.md) — para poder cerrar el juego sin perder progreso.}}

# Después (próximo, en orden)

{{Lo que sigue cuando se libere lugar, en orden de prioridad. Solo título + por qué
en una frase — el detalle se escribe recién al abrir el cambio (okf-plan). Acá
también aterrizan las ideas buenas que aparecen a mitad de otro cambio, en vez de
colarse al código. Ej:}}
- {{Ranking semanal — da razón para volver a entrar.}}

# No-goals (por ahora)

{{Lo que decidiste NO hacer, para que ni vos ni una IA lo "agreguen de paso". Tan
valioso como la visión. Si un no-goal deja de serlo, se edita esta lista. Ej:}}
- {{Multiplayer en tiempo real — complejidad que el juego no necesita todavía.}}
