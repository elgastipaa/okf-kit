---
type: Decision
title: cortito se queda en la stdlib de Python, sin dependencias
description: "Todo (HTTP, persistencia, tests) sale de la biblioteca estándar: no hay requirements ni manifiesto de paquete."
status: proposed
origen: reconstruido
verify: none
verify_note: "No hay chequeo mecánico de 'no agregar dependencias': se ve en el diff de imports y en que el CI corre sin ningún paso de instalación."
resource: .github/workflows/ci.yml
tags: [stack, dependencias]
timestamp: 2026-08-07T00:00:00Z
---

# Contexto

El repo no tiene `requirements.txt`, `pyproject.toml` ni `setup.py`; el
[CI](../runbooks/levantar-local.md) instala Python y corre `unittest` sin ningún paso
de instalación, y el README lo declara como propiedad del proyecto ("Python stdlib +
SQLite, sin dependencias"). El servidor HTTP es `http.server`, la DB es `sqlite3` y
los tests son `unittest`, todos de la stdlib.

> Pendiente de confirmar: por qué se eligió no tener dependencias — si es una
> restricción real de despliegue, una preferencia, o un ejercicio. No hay razón
> registrada. **Sin esa confirmación esta decisión no obliga a nadie** (queda
> `proposed`).

# Decisión

No se agregan dependencias externas. HTTP, persistencia y tests salen de la stdlib.

# Consecuencias

- **Lo bueno:** `git clone` y corre; el CI no necesita instalar nada y no hay lockfile
  que mantener. Los [chequeos](../checks.md) son un solo comando.
- **Lo malo, y es lo que hay que tener presente antes de romperla:** `http.server`
  no está pensado para producción (single-thread, sin TLS, sin rate limiting), el
  parseo de rutas es manual y frágil
  (ver [paths que no son códigos](../references/paths-invalidos-rompen-el-get.md)),
  y no hay validación de la URL destino más allá de "no vacía".
- Meter un framework (Flask, FastAPI) o un cliente de otra DB contradice esta
  decisión: si hace falta, se supersede explícitamente, no se agrega de paso.
