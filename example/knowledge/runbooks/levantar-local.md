---
type: Runbook
title: Levantar cortito local y probarlo a mano
description: "Cómo arrancar el servidor, acortar un link y resolverlo, y dónde queda la base."
resource: src/server.py
tags: [ops, local]
timestamp: 2026-08-07T00:00:00Z
---

# Cuándo

Para probar un cambio a mano, o para reproducir algo que no cubren los
[chequeos automáticos](../checks.md).

# Pasos

1. **Parate en la raíz del repo.** No es opcional: el arranque importa `src.server`
   como paquete y la DB es un path relativo al directorio de trabajo
   (ver [la tabla links](../schema/links.md)).

   ```bash
   cd <repo>
   python3 -c "from src.server import serve; serve()"   # queda en foreground, :8080
   ```

2. **Verificá con qué flags quedó levantado** (el healthcheck es el path vacío):

   ```bash
   curl -s localhost:8080
   ```

3. **Acortar y resolver:**

   ```bash
   curl -s -X POST localhost:8080 -d '{"url":"https://example.com"}'
   curl -i localhost:8080/<code>     # 302 al target, 404 si no existe, 410 si venció
   ```

   `-i` importa: la resolución responde con un redirect, así que sin ver los headers
   no se distingue del error.

# Notas / gotchas

- **El puerto es un argumento de `serve()`, no una variable de entorno**: para
  cambiarlo, `serve(9090)`. No hay flag de línea de comandos.
- **Las flags se leen al importar el módulo**, así que se setean antes de arrancar y
  no se pueden cambiar en caliente:
  `FLAG_QR=1 python3 -c "from src.server import serve; serve()"`. Qué hace cada una
  (y cuáles no hacen nada) está en
  [flags de entorno](../references/flags-de-entorno.md).
- **La DB se crea sola** (`links.db` en el directorio actual) y está en `.gitignore`.
  Para empezar de cero, borrala — pero ojo con
  [los códigos de una DB nueva](../references/codigos-cortos-en-db-nueva.md).
- **Probar con el navegador ensucia**: pide `/favicon.ico` y eso
  [rompe el handler](../references/paths-invalidos-rompen-el-get.md). Con `curl` no
  pasa.
- No hay TLS, ni logs de acceso (`log_message` está anulado): si el servidor "no dice
  nada", es a propósito.
