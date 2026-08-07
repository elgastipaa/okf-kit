---
okf_version: "0.1"
kit_version: "0.12.0"
---

# Por dónde empezar

| Si necesitás… | Leé | Fuente de verdad |
|---|---|---|
| Qué se está haciendo y qué sigue | [`roadmap.md`](roadmap.md) | el equipo |
| Cómo sé que esto anda / qué comandos correr | [`checks.md`](checks.md) | el repo |
| Levantar el servidor y probar un link a mano | [`runbooks/levantar-local.md`](runbooks/levantar-local.md) | el código |
| De dónde sale el código corto de un link | [`decisions/0002-codigos-derivados-del-id.md`](decisions/0002-codigos-derivados-del-id.md), [`architecture/overview.md`](architecture/overview.md) | el código |
| Qué se guarda de cada link (y qué no) | [`schema/links.md`](schema/links.md) | el código |
| Por qué un link da 404, 410, o rompe el servidor | [`decisions/0003-expirado-responde-410.md`](decisions/0003-expirado-responde-410.md), [`references/paths-invalidos-rompen-el-get.md`](references/paths-invalidos-rompen-el-get.md) | el código |
| Si una `FLAG_*` hace algo de verdad | [`references/flags-de-entorno.md`](references/flags-de-entorno.md) | el código |
| Si puedo usar una librería para esto | [`decisions/0001-solo-stdlib.md`](decisions/0001-solo-stdlib.md) | el equipo |
| Por qué el código de un link parece demasiado corto | [`references/codigos-cortos-en-db-nueva.md`](references/codigos-cortos-en-db-nueva.md) | el código |

# Roadmap

* [Rumbo de cortito](roadmap.md) - Un acortador de links mínimo y sin dependencias; el rumbo todavía no lo dictó nadie y está inferido del código.

# Runbook

* [Cómo se comprueba que este repo anda](checks.md) - Los comandos que prueban que el código funciona, y qué cubre cada uno.

# Subdirectories

* [architecture](architecture/index.md) - Cómo está armado el servicio y por dónde pasa un request.
* [decisions](decisions/index.md) - El por qué de las tres elecciones no obvias del código (las tres, todavía sin confirmar).
* [references](references/index.md) - Gotchas del comportamiento real: flags que no hacen nada, códigos cortos de más, paths que rompen.
* [runbooks](runbooks/index.md) - Cómo levantar y probar cortito a mano.
* [schema](schema/index.md) - La única tabla, su grano y lo que el DDL no dice.
