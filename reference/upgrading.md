# Actualizar un repo que ya tiene OKF

Un repo con OKF tiene **dos cosas que envejecen distinto**, y confundirlas es el error caro:

| | Qué es | Cómo se mantiene |
|---|---|---|
| **Contenido del bundle** | Los conceptos, decisiones y el log: el conocimiento **del proyecto**. | `okf-update` en cada cambio, y `okf-verify` cada tanto. Es tuyo, nunca se pisa. |
| **Material instalado** | El `AGENTS.md`, los skills, el revisor y los scripts: la maquinaria **del kit**. | Este documento. Se **reemplaza** por la revisión nueva. |

`okf-update` mantiene lo primero y **no puede** tocar lo segundo: corre dentro del repo
destino, sin el kit en disco. Por eso el material instalado se fosiliza en la revisión con la
que el repo nació, mientras el kit sigue mejorando.

## Cómo saber si estás desfasado

El bundle lo dice: `kit_version` en el frontmatter de `knowledge/index.md` es la revisión con
la que se inicializó. Comparala con el `VERSION` del kit.

```
grep kit_version <repo>/knowledge/index.md     # con qué nació
cat <okf-kit>/VERSION                          # dónde va el kit
```

Si difieren, el `CHANGELOG.md` del kit entre esas dos versiones es exactamente la lista de lo
que te estás perdiendo — y de lo que hay que re-copiar.

## Procedimiento

> **Los pasos 3 y 5 son mecánicos y los hace el instalador:**
> `python3 scripts/okf_install.py <repo> --upgrade`. Reemplaza scripts, skills, CI y hook
> (detecta solo el nivel de instalación y si el hook es del kit), re-estampa `kit_version`,
> deja la línea en `log.md`, corre el linter sobre el resultado y **no toca el `AGENTS.md`
> ni el contenido del bundle**. Los pasos 1, 2, 4 y 6 siguen siendo tuyos: son criterio.

1. **Leé el `CHANGELOG` desde la versión del repo hasta la actual.** No es ceremonia: te dice
   qué archivos cambiaron y si alguna regla cambió de forma (p.ej. de 0.5.0 a 0.6.x el
   contrato ganó la capa de futuro y la regla descriptivo/normativo, y aparecieron marcadores
   de recorte que antes no existían).
2. **Averiguá qué nivel de instalación tiene el repo.** Si su `AGENTS.md` no menciona el
   rumbo ni `_changes/`, o no existe `knowledge/roadmap.md`, está en **mínimo** — y la
   actualización **lo respeta**: no le metas la capa de futuro por la ventana. Preguntale al
   usuario si la quiere ahora, en su idioma (ver `GUIDE.md` §1).
3. **Los scripts y los skills se reemplazan enteros** (esto lo hace `--upgrade`). No tienen
   estado del proyecto: `templates/scripts/*.py` → `<repo>/scripts/`,
   `templates/skills/{okf-update,okf-verify}` (+ `okf-plan` si va la capa de futuro) →
   `<repo>/.claude/skills/`, `templates/agents/okf-reviewer.md` → `<repo>/.claude/agents/`, `templates/ci/okf.yml` y `templates/hooks/pre-commit` si estaban
   instalados. Un `pre-commit` que **no** es del kit no se pisa: puede ser del usuario.
4. **El `AGENTS.md` NO se reemplaza entero** — es el único que lleva contenido del proyecto
   mezclado con el del kit. Lo que es del proyecto y **se conserva**: el título y la
   descripción del stack, las **reglas duras** propias, y los `{{placeholders}}` completados
   (capas no-autoritativas, etc.). Lo que es del kit y **se reemplaza**: las secciones 1, 2, 3
   y Procedimientos. Mostrale al usuario qué conservaste y qué reemplazaste **antes** de
   escribir: acá es donde se pierde conocimiento si se hace en silencio.
5. **Re-estampá `kit_version`** en `knowledge/index.md` con el `VERSION` nuevo, y dejá una
   línea en `log.md` (`## YYYY-MM-DD` · qué revisión, desde cuál). Esto también lo hace
   `--upgrade`; si el repo no mantiene `log.md`, lo omite.
6. **Verificá**: `python3 scripts/okf_lint.py knowledge` tiene que pasar. Si la revisión nueva
   trajo convenciones nuevas (p.ej. conceptos en la raíz del bundle agrupados por `type`), el
   linter las va a marcar acá — arreglalas ahora, no después.

> **El contenido del bundle no se toca en este procedimiento.** Si de paso ves conceptos que
> contradicen el código, eso es otro trabajo: `okf_stale.py` para saber dónde mirar y
> `okf-verify` Nivel 2 para resolverlo, con el usuario decidiendo quién tiene razón.
