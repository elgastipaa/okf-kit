---
type: Reference
title: Un path con caracteres fuera de base62 revienta el GET
description: "decode() levanta ValueError ante cualquier carácter que no esté en el alfabeto, así que pedidos como /favicon.ico terminan en error del handler."
resource: src/codes.py
tags: [gotcha, http]
timestamp: 2026-08-07T12:00:00Z
verified_against: "f55d2fe"
source_of_truth: code
---

`do_GET` toma el path, le saca las barras y se lo pasa directo a `codes.decode`. No
hay validación previa: `decode` recorre el string haciendo `ALPHABET.index(ch)`, y
ante un carácter que no esté en base62 —un punto, un guion, un `%`— levanta
`ValueError: substring not found`. La excepción sube sin que nadie la agarre, así que
el request muere con un traceback en vez de un 404.

Casos que pasan solos, sin que nadie escriba mal una URL:

- `GET /favicon.ico` — lo pide cualquier navegador.
- `GET /robots.txt`, `/.well-known/...` — lo piden los crawlers.
- Cualquier path con más de un segmento: `lstrip("/")` sólo saca las barras del
  **principio**, así que `/a/b` llega a `decode` con la barra del medio adentro.

Además, un código sintácticamente válido pero inexistente (`/abc`) sí decodifica bien
y responde 404 — el error es sólo del alfabeto, no de la existencia.

# Arreglado

`decode()` valida cada carácter y lanza un `ValueError` con mensaje propio; el handler lo
atrapa y devuelve **404**. Un path inválido y un código inexistente ahora se ven igual desde
afuera, que es lo correcto: los dos significan "acá no hay nada".
