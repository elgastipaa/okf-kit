---
type: Change
status: in-progress
title: Medir elicitación sobre wodlab, y de paso el pasivo que dejó el kit viejo
description: "Aplicar okf-init v0.9.0 a ciegas sobre un clon de wodlab con el dueño disponible, contar qué preguntas produce, y auditar cuántas de las 51 decisiones que escribió el kit v0.6.2 nadie tomó."
tags: [okf, eval, elicitacion]
timestamp: 2026-08-06T00:00:00Z
---

# Por qué este experimento y no otro

La [0032](../decisions/0032-el-instrumento-tiene-un-piso-de-resolucion.md) cerró el eje de
turnos y tokens: con lo que cuesta medir, no se resuelve lo que queda. La
[0033](../decisions/0033-el-kit-preserva-porques-no-acelera-hechos.md) declaró que lo que el
kit sí hace es **preservar porqués y producir preguntas**. Eso tiene su propia forma de
medirse, es barata, y **no depende del instrumento que tocó su techo**: se cuenta cuántas
preguntas produce y cuántas el dueño contesta con conocimiento que no estaba en ningún lado.

`wodlab` es el conejillo correcto por una razón que no buscamos: **ya tiene un bundle OKF
v0.6.2 con 51 decisiones `accepted` y cero preguntas abiertas**. La v0.6.2 es **anterior** al
rework de la [0027](../decisions/0027-una-razon-reconstruida-no-manda.md), o sea que ese bundle
lo escribió el kit **cuando fabricaba porqués y nunca preguntaba**. Ninguna de las 51 declara
`origen`, así que por la regla vigente las 51 afirman hoy "lo dictó una persona".

Eso habilita dos mediciones en el mismo repo, y la segunda mide el **daño**, que es la parte
que ningún kit publica de sí mismo.

# Test A — ¿cuántas preguntas produce, y sirven?

`okf-init` v0.9.0 corre **a ciegas** sobre un clon (`wodlab-okf-test`) con la capa vieja
apartada. Las preguntas que deje (`--questions`) las clasifica **el dueño, no yo**:

- **nueva** — "es cierto, eso nunca lo escribí en ningún lado".
- **ya estaba** — se contesta leyendo el bundle v0.6.2 que ya existía. El kit la está
  redescubriendo, no elicitando.
- **ruido** — irrelevante, o se contesta mirando el código treinta segundos.

Ground truth parcial **gratis**: la clasificación "ya estaba" se puede pre-chequear contra el
bundle viejo antes de molestar a nadie.

<!-- GATE ESCRITO ANTES DE CORRER (0028). No editar después. -->

**Gate del test A.** Referencia: `forgeidle` con v0.8.0 dio **12 preguntas, 9 nuevas, 0 ruido**.

1. **Se reproduce** — ≥ 8 preguntas, **≥ 50% nuevas** y **≤ 20% ruido**. La elicitación es una
   función del kit, no una casualidad de un repo.
2. **Existe pero es flojo** — entre 3 y 7 preguntas útiles, o mayoría "ya estaba". Se publica
   como lo que es: el kit pregunta, pero mayormente redescubre.
3. **No se reproduce** — ≤ 2 preguntas, o mayoría ruido. Entonces la promesa de la 0033 **se
   apoya en un solo repo** y hay que decirlo en el README con esas palabras.

# Test B — ¿cuántas de las 51 decisiones no las tomó nadie?

**Muestra de 12 al azar** (con `sort -R` y semilla registrada, para que no las elija yo entre
las que me convienen). De cada una, el dueño dice:

- **la decidí yo** — hubo una decisión deliberada, esté escrita o no.
- **no la decidí** — salió así, o la decidió una IA, o es una descripción del código disfrazada
  de decisión.
- **no sé** — que a los efectos de autoridad **cuenta como "no la decidí"**: una decisión que
  el dueño no puede confirmar no puede ser normativa.

**Gate del test B.** Antecedentes: en `the-conclave`, 3 de 6 porqués no los sabía nadie; en
`forgeidle` v0.5.0, 7 decisiones normativas fabricadas.

- **≥ 25% "no la decidí"** → el kit viejo **fabricaba autoridad a escala** en repos reales, y
  ese es el titular. Se publica con el número, y `okf-update`/`reference/upgrading.md` tienen
  que ofrecer un camino para auditar un bundle viejo.
- **< 25%** → el daño fue acotado. Se publica igual, y baja la urgencia de la herramienta de
  auditoría.

**Lo que este test NO mide**: si las decisiones son *correctas*. Una razón fabricada puede
acertar. Mide si tienen **autoridad legítima**, que es lo que la 0027 dice que importa.

# El agujero que apareció antes de medir: la autoridad se puede lavar

El dueño confirmó que **`DECISIONS.md` (6699 líneas) lo escribió una IA**. Eso rompe la forma
en que veníamos operacionalizando la [0027](../decisions/0027-una-razon-reconstruida-no-manda.md):

- La regla dice que `origen: dictado` significa **"te lo contó una persona"**.
- En la práctica se venía chequeando como **"cita una fuente escrita"**.
- En un repo vibecodeado **las dos cosas no coinciden**: un init que cosecha de un doc escrito
  por una IA produce una decisión que **cita una fuente y sigue siendo reconstruida**. La
  autoridad no se fabrica en el bundle: se **lava** un paso más arriba.

`okf-migrate` ya advierte que estás leyendo "docs que escribió otra persona u otra IA hace
meses", pero la regla de `origen` **solo cubre el caso "la dedujiste del código"**. Copiarla de
un doc de autor desconocido cae en el hueco.

> Pendiente de confirmar: si el arreglo es (a) que `dictado` exija una **persona** identificable
> y un doc no alcance salvo que alguien confirme quién lo escribió, o (b) que `okf-migrate`
> haga **una sola pregunta al principio** —"¿quién escribió estos docs?"— que determina la
> autoridad de todo lo que se cosecha después. La (b) es una pregunta y decide decenas de
> archivos.

**No se arregla antes de medir.** La corrida a ciegas está en vuelo con la prosa actual, y el
test B existe justamente para cuantificar cuánto daño hace este hueco en un repo real. Arreglar
primero convertiría la medición en una confirmación de lo que ya creo.

**Corrección al registro**: en el análisis de `the-conclave` se afirmó que las 8 decisiones
"citan una fuente escrita **por el dueño**". Lo verificado fue que citan una **fuente escrita**;
la autoría se asumió. Con esto, esa conclusión queda en duda y no debe citarse como evidencia
de que la 0027 se sostiene.

# El loop

Un ítem por iteración, y **se para en los pasos que necesitan al dueño** — que en este
experimento no es una interrupción, es el instrumento.

1. [x] Clon `wodlab-okf-test` desde `wodlab` (270 commits, 6,6 MB sin `node_modules`)
2. [ ] Gate escrito antes de correr nada
3. [ ] Apartar la capa v0.6.2 en una rama, dejando el resto del repo intacto
4. [ ] `okf-init` v0.9.0 **a ciegas** (proceso fresco, sin ver este doc ni el bundle viejo)
5. [ ] Pre-clasificar las preguntas contra el bundle viejo ("ya estaba" / candidata a nueva)
6. [ ] 🙋 **El dueño clasifica** las preguntas del test A
7. [ ] Muestra de 12 decisiones al azar, semilla registrada
8. [ ] 🙋 **El dueño clasifica** la muestra del test B
9. [ ] Leer contra los dos gates y publicar, salga lo que salga
10. [ ] Cosechar: decisiones al bundle del kit, roadmap al día, este doc borrado
