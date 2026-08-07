---
okf_version: "0.1"
kit_version: "0.12.0"
---

# Por dónde empezar

| Si necesitás… | Leé | Fuente de verdad |
|---|---|---|
| Entender qué es este kit y para quién | [`../README.md`](../README.md) · [roadmap](roadmap.md) | el dueño |
| Saber si el kit sirve, con números | [`../MEASUREMENT.md`](../MEASUREMENT.md) | las mediciones |
| Cómo sé que el kit anda / qué comandos correr | [`checks.md`](checks.md) | el repo |
| Ver qué produce sobre código real | [`../example/README.md`](../example/README.md) | el ejemplo, que el gate mantiene al día |
| Por qué una regla del kit es así | [`decisions/index.md`](decisions/index.md) | las decisiones (`accepted` = normativas) |
| Cambiar el formato OKF en sí | [`../OKF-SPEC.md`](../OKF-SPEC.md) | la spec |
| Tocar el instalador o el gate | [`architecture/index.md`](architecture/index.md) · [`checks.md`](checks.md) | el código de `scripts/` |
| Saber qué NO hay que hacer | [roadmap](roadmap.md) (§No-goals) | el dueño |

# Roadmap

* [Rumbo del kit OKF](roadmap.md) - Hacia dónde va el kit hoy: ingeniería de contexto completa (pasado, presente y futuro) aplicable a cualquier repo sin tooling.

# Runbook

* [Cómo se comprueba que el kit anda](checks.md) - Los comandos que prueban que el kit funciona, y qué cubre cada uno.

# Subdirectories

* [architecture](architecture/index.md) - Qué es el kit OKF, su anatomía y el modelo de tres capas.
* [concepts](concepts/index.md) - Los conceptos centrales de OKF: bundle, progressive disclosure, perfiles, ciclo de vida.
* [decisions](decisions/index.md) - Las decisiones de diseño del kit y su por qué.
* [runbooks](runbooks/index.md) - Procedimientos operativos: lint, cold test, bootstrap.
* [references](references/index.md) - El formato OKF y aceleradores externos opcionales.
