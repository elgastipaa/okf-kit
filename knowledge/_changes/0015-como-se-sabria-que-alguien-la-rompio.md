---
type: Change
status: in-progress
title: Cada decisión normativa declara cómo se sabría que alguien la rompió
description: "Un campo verify en el frontmatter que ata la decisión al comando que la falsea, con un runner opt-in y una regla que se activa sola cuando el bundle adopta la convención."
tags: [okf, decisiones, drift, tooling]
timestamp: 2026-08-07T00:00:00Z
---

# El problema

Una decisión `accepted` es **normativa**: obliga al código. Pero el kit no tiene forma de
saber si el código **dejó de cumplirla**. `okf_refs.py` caza referencias muertas y el linter
valida estructura; los dos miran el **documento**. Nadie mira si lo que el documento prescribe
sigue siendo cierto.

Es el drift más caro, porque es silencioso: la decisión sigue ahí, con su `status: accepted`,
y el código hace otra cosa desde hace meses.

# La evidencia, que no es nuestra

La idea sale de `okf-decisions.mjs`, que el dueño de un repo escribió sobre su propio bundle.
Ese repo lleva meses usándola, y el corpus dice que **no es ceremonia**:

- **54 de 54** decisiones `accepted` declaran `verify:`.
- **50 traen un comando real**; solo **4** son `none`.
- **35 de 35** targets de archivo **siguen resolviendo**: el sistema no se pudrió.

La mayoría apunta a un test que ya existía (`npx vitest run <test>`). Cuando no había ninguno,
apareció un script chico con el nombre de la decisión: `ningun-reloj-arranca-solo.mjs`,
`anti-repeticion-es-una-decision.mjs`. Eso es exactamente el efecto buscado: **la pregunta
"¿cómo sabría que alguien la rompió?" se contesta al escribir la decisión, no después.**

# Diseño

## La convención

En el frontmatter de una decisión:

```yaml
verify: npx vitest run src/lib/prescription/e1rm.test.ts
# o bien:
verify: none
verify_note: por qué no se puede chequear mecánicamente
```

## Cuándo se exige (opt-in por uso, no por configuración)

**Si alguna decisión del bundle declara `verify:`, el bundle adoptó la convención** y las
demás `accepted` que no la declaran son WARN. Si ninguna la declara, la regla **no dice nada**.

Es lo que evita las dos malas salidas: obligar a todos —que rompería todo bundle existente, y
el kit nunca lo hizo en un cambio de formato— o poner un flag de configuración que nadie
enciende. La adopción se declara **usándola**.

- `verify: none` **sin** `verify_note` es **ERROR**: admitir que no se puede chequear es
  legítimo; hacerlo sin decir por qué es el atajo. Misma lógica que `origen: confirmado`
  ([0034](../decisions/0034-el-porque-perdido-tiene-su-propio-casillero.md)).

## El runner es opt-in, y esto no es un detalle

`okf_decisions.py` **ejecuta comandos escritos en markdown**. En un repo propio eso es igual
que un `npm script`; en un PR desde un fork es **ejecución de código arbitrario**. Por eso:

- **NO se agrega al workflow de CI que instala el kit.** El linter sí, porque no ejecuta nada.
- El docstring dice el riesgo con todas las letras, y el skill que lo invoca también.

# Criterio de aceptación, escrito antes de codear

1. **El linter no rompe ningún bundle existente**: sobre los cuatro repos de prueba y el
   dogfood, la regla nueva **no reporta nada** mientras no adopten la convención.
2. **El runner encuentra de verdad**: corre los 50 `verify` reales del repo que ya usa la
   convención y reporta un resultado por decisión, sin falsos positivos de plomería.
3. **El dogfood decide si es ceremonia.** Se intenta adoptar la convención en las decisiones
   **del propio kit**, que son de otra naturaleza (prosa y tooling, no código de producto). Se
   publica **la proporción real** de `verify` con comando contra `none` — si el kit termina
   con mayoría de `none`, eso es evidencia de que la convención sirve para repos de producto y
   no para todos, y se dice.
4. Asserts + roturas probadas.

# Resultado

**Criterio 1 (no rompe nada existente): cumplido.** Los cuatro bundles que no adoptaron la
convención quedan **mudos**; el que la adoptó del todo, también. La regla solo habla cuando la
adopción quedó **a medias**, que es el único estado peligroso.

**Criterio 2 (el runner encuentra de verdad): cumplido.** Parsea los 50 comandos del corpus
real, los ejecuta con `--repo`, y reporta por decisión. Probado además con una violación
inyectada: exit 1 y el mensaje que dice que **el bug es el código, no el documento**.

**Criterio 3 (¿es ceremonia?): NO lo es, ni siquiera en el caso difícil.**

| repo | con comando real | `verify: none` |
|---|---|---|
| producto (el corpus original) | 50 (93%) | 4 |
| **el kit** (prosa y tooling) | **26 (76%)** | **8** |

Los 8 `none` del kit son honestos y son justamente la información que la convención promete
sacar a la superficie: el método de medición, el piso del instrumento, lo que el kit promete,
una regla que **no** se agregó. Ninguna la puede falsear un comando, y saber **cuáles** son
vale.

Y el dogfood pagó de inmediato: al adoptar la convención, el linter marcó una decisión de
prueba del propio suite que no la declaraba. La regla funcionó antes de terminar de escribirla.

# Lo que se rompió mientras se construía

- **El parser se comía la comilla de cierre.** `.strip('"')` sobre `grep -q "PASS.*algo"` dejaba
  la cadena sin terminar y el shell fallaba. **Las 20 "violaciones" del primer dogfood eran
  eso**, no decisiones incumplidas — un recordatorio de que la primera reacción ante un
  resultado alarmante es dudar del instrumento.
- El mensaje explicativo quedó **dentro** del loop de violaciones y se repetía por cada una.
- El template terminó con **dos** bloques diciendo cómo verificar: el nuevo y uno viejo en
  prosa. Una verdad, un lugar — se borró el viejo.

# Tareas

- [ ] Criterio escrito antes de codear
- [ ] Regla del linter (opt-in por uso) + `verify: none` sin nota = ERROR
- [ ] `okf_decisions.py` (runner opt-in) y su advertencia de ejecución
- [ ] Validar: los 5 bundles quedan mudos; el runner corre contra el corpus real
- [ ] Dogfood en las decisiones del kit, con la proporción publicada
- [ ] `OKF-SPEC`, template de decisión, `okf-verify`
- [ ] Asserts + roturas
