---
type: Decision
status: accepted
origen: dictado
title: El kit nunca destruye trabajo que git no pueda devolver
description: "Antes de reemplazar o apartar algo del repo del usuario, el kit exige que git lo pueda restaurar, y si no puede se planta en vez de seguir."
tags: [okf, instalador, perdida-de-datos, eval]
timestamp: 2026-08-05T00:00:00Z
---

# Contexto

La misma clase de bug apareció **tres veces en tres herramientas distintas** del kit, y las
tres podían destruir trabajo del usuario sin dejar rastro:

- **El instalador con `--force`** reemplazaba el `AGENTS.md` del usuario confiando en que el
  mensaje decía *"commiteá antes"*. Ese paso **falla en silencio**: un hook que aborta el
  commit, un `git add` que no incluyó el archivo. Apareció probando el propio kit — el commit
  de un fixture no entró y el archivo se perdió igual.
- **`--upgrade`** reemplazaba skills, linter y hook incondicionalmente, así que una edición del
  usuario sobre material instalado desaparecía en la siguiente actualización.
- **El brazo "sin capa" del harness de medición** aparta archivos del repo bajo prueba para
  medir sin ellos. Un corte a mitad de la corrida dejaría al usuario sin su contexto.

En los tres casos la conducta ingenua —reemplazar y seguir— es indistinguible de la correcta
mientras nada falle, y catastrófica cuando algo falla.

# Decisión

**Antes de reemplazar, apartar o borrar algo del repo del usuario, el kit exige que git lo
pueda devolver.** Si no puede, **se planta y lo dice**; no lo hace "con cuidado".

- `--force` se **niega** si el entrypoint que va a reemplazar tiene cambios sin commitear, y
  avisa fuerte si el destino ni siquiera es un repo git.
- `--upgrade` **no pisa** material instalado que el usuario editó: cada archivo lleva un sello
  con versión **y hash**, y la clasificación distingue *"es mi copia vieja"* de *"lo editaste
  vos"* ([0025](0025-el-material-instalado-se-sella-con-hash.md)).
- El harness **solo corre** el brazo sin capa si el repo es git y esas rutas están limpias;
  restaura siempre, incluso si la corrida explota, y si algo falla imprime la ruta del
  respaldo y el `git checkout` exacto.
- El contrato se actualiza **por secciones**, conservando lo del usuario palabra por palabra
  ([0024](0024-el-contrato-se-actualiza-por-secciones.md)).

# Consecuencias

- **Perder actualizaciones es recuperable; perder trabajo no.** Ante la duda, el kit prefiere
  no actualizar y decirlo.
- **A veces molesta.** Un archivo editado deja de recibir mejoras, y el brazo sin capa se
  niega a correr sobre un repo sucio. Es el trade correcto y está declarado en el propio
  sello, para que no sea una sorpresa.
- **Se descartó explícitamente** el patrón contrario, que existe en el ecosistema: hay
  herramientas cuyo comando de sincronización hace `rm -rf` del directorio de reglas y del
  `CLAUDE.md` del usuario sin mirar git ni preguntar. Es el anti-patrón contra el que existe
  esta decisión (ver [ecosistema-2026](../references/ecosistema-2026.md)).
