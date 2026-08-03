---
type: Decision
status: accepted
title: El material instalado se sella con hash, no solo con versión
description: "Cada archivo que el kit instala lleva su versión y el hash de lo que se escribió, que es lo único que distingue una copia vieja del kit de un archivo que editó el usuario."
tags: [okf, upgrade, instalador, perdida-de-datos]
timestamp: 2026-08-03T00:00:00Z
---

# Contexto

`install_machinery` reemplazaba skills, linter, revisor, CI y hook **incondicionalmente**. Es
la misma familia de pérdida de datos que la 0.7.4 arregló para el entrypoint y la
[0024](0024-el-contrato-se-actualiza-por-secciones.md) para el contrato, un nivel más abajo y
sin arreglar: un usuario que ajusta un skill a su repo pierde el ajuste en el próximo
`--upgrade`, sin aviso.

El análisis de dos herramientas que instalan artefactos en repos ajenos mostró las dos salidas
que **no** queríamos:

- **OpenSpec** sella cada archivo generado con la **versión** (`generatedBy`) y decide por ahí
  si reescribir. La consecuencia exacta: si editás el cuerpo y dejás el frontmatter, no se
  toca hasta el próximo bump — y ahí **se pisa en silencio**. La versión sola no distingue
  "esta es mi copia vieja" de "esto lo editaste vos".
- **rulebook-ai** no tiene update: su `sync` hace `rmtree`/`unlink` del destino y regenera.
  Con eso, `--assistant claude-code` borra el `CLAUDE.md` del usuario y `--assistant cursor`
  hace `rmtree('.cursor')` entero, sin mirar git, sin preguntar. Su defensa es declarar las
  reglas desechables y gitignorearlas, que es justamente la capa que el kit quiere versionada.

# Decisión

Cada archivo de maquinaria instalado lleva un sello con **la versión y el sha1 del contenido
que el kit escribió**, comentado según el tipo de archivo. Al actualizar, se recalcula el hash
del cuerpo y se clasifica en **cuatro desenlaces**:

- **ausente** → se escribe;
- **intacto** (el hash coincide) → se reemplaza, es nuestro y nadie lo tocó;
- **editado** (el hash no coincide) → **no se pisa**, se reporta y se sigue;
- **sin sello** (material de un kit anterior al sellado) → se trata como editado: no se puede
  afirmar que lo tocaron, y ante la duda no se destruye.

El hash es lo que hace posible el tercer caso, y el tercer caso es el punto: sin él solo hay
dos salidas, y las dos son malas — o se pisa lo del usuario, o no se actualiza nunca por miedo.

# Consecuencias

- **Un archivo editado deja de recibir mejoras del kit**, y el sello lo dice en su propio
  texto para que no sea una sorpresa. Es el trade correcto: perder actualizaciones es
  recuperable, perder el trabajo no.
- **Cuesta una línea de comentario por archivo instalado.** No toca el presupuesto del
  contrato: son skills y scripts, que no son always-on.
- **No leemos el sello de un archivo y extrapolamos al resto**, que es lo que hace OpenSpec.
  Cada archivo se clasifica solo.
- Junto con la [0024](0024-el-contrato-se-actualiza-por-secciones.md), completa la regla: el
  kit puede actualizar **todo** lo que instaló sin destruir nada del usuario — el contrato por
  secciones, la maquinaria por sello.
