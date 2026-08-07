# Qué medimos, y qué nos dio

Este kit se mide a sí mismo. Esta página junta **todo** lo que salió, incluido lo que no le
conviene — que es la mayor parte.

Si venís a buscar un número grande para justificar instalar esto: **no lo vas a encontrar acá**,
y esa es la información más útil que te podemos dar.

Los repos son proyectos privados de una sola persona, así que van anonimizados. Los scorecards
crudos **no se publican**: cada corrida guarda la respuesta completa del agente sobre código
privado. Los agregados de abajo se derivan de esos scorecards con
`python3 templates/eval/run-eval.py --summarize *.jsonl`, que lee **solo campos numéricos** —
por construcción no puede filtrar el texto de una respuesta.

| | qué es |
|---|---|
| **Repo A** | juego web por turnos, ~2.700 archivos TS, con código forkeado y términos ambiguos |
| **Repo B** | juego idle chico, bien nombrado, un solo autor |
| **Repo C** | otro juego idle, con su historia en chats que ya no existen |
| **Repo D** | PWA de entrenamiento, con miles de líneas de decisiones ya escritas a mano |

---

## Cómo medimos

Cada pregunta corre en un proceso `claude -p` **fresco** dentro del repo, y se registran turnos,
tokens de contexto, costo y acierto. Lo que hace que el número signifique algo:

- **n ≥ 3 por pregunta, y se reporta la dispersión.** El ruido intra-condición medido fue de
  **~2,3 a 3,5 turnos por pregunta**. Cualquier efecto menor a eso no es un efecto: es haber
  corrido dos veces.
- **El brazo de control aparta los archivos de verdad.** No le pedimos al agente que "ignore" el
  contexto — el contrato se auto-carga antes de que el agente decida nada. Se mueven los
  archivos a un temporal y se restauran siempre, incluso si la corrida explota.
- **El juez corre con `cwd` en el repo**, así que puede abrir el código y verificar. Sin eso
  degrada a comparar paráfrasis.
- **Hay veredicto de premisa falsa y de explicación inventada**, no solo "correcta/incorrecta".
- **El criterio de éxito se escribe antes de mirar el resultado.** Un criterio fijado después
  es una racionalización.
- **Se valida que el scorecard sea uno antes de leerlo**: corridas completas, cero fallidas, y
  el repo bajo prueba sin modificar por la propia corrida.

---

## Eje 1 — Recuperación de hechos: la capa no paga por sí sola

**Repo B (v0.7.4).** 21 corridas por brazo, 7 preguntas.

| brazo | turnos | sd | acierto |
|---|---|---|---|
| con el bundle | 7,81 | 2,36 | 14/21 |
| sin capa | 7,86 | 2,95 | **18/21** |
| un `AGENTS.md` convencional escrito a mano | 8,29 | 2,62 | **19/21** |

Sin diferencia en turnos, y **el acierto era peor con el kit**. Ese resultado disparó una
revisión que encontró la causa y revirtió el cambio que la producía (la decisión `0022`, la
primera que este kit tumbó con su propia medición).

**Repo A (v0.8.0).** 12 corridas por brazo, 4 preguntas. Acá está el resultado que más nos
costó publicar:

| brazo | turnos | sd | acierto | tokens de contexto |
|---|---|---|---|---|
| sin capa | 7,00 | 3,46 | 9/12 | 233.534 |
| **capa escrita a mano por el dueño** | **4,92** | 1,44 | 11/12 | **154.444** |
| bundle de `okf-init`, instalado a ciegas | 7,33 | 3,17 | 10/12 | 242.077 |
| ídem + capa generada del código | 8,75 | 5,67 | 11/12 | 278.368 |
| ídem + índice que rutea por necesidad | 5,83 | 1,34 | 10/12 | 159.778 |

**El −34% de turnos que este kit citaba como su mejor número lo produjo el autor humano de esa
capa, no el formato.** Un bundle instalado a ciegas quedó **indistinguible de no tener capa**.

Probamos las dos hipótesis caras para cerrar la brecha —generar los hechos del código, y
reemplazar el índice por tipo por uno que rutea a 1-3 archivos— y **ninguna separó por encima
del ruido**. La capa generada sí subió el acierto (10/12 → 11/12) sin bajar los turnos.

**Y ahí el instrumento tocó su techo.** Con n=12, el error estándar de la diferencia vale entre
1,1 y 3,4 turnos: **ningún efecto menor a ~20-40% es medible con lo que cuesta medir**. Cerramos
el eje en vez de comprar ruido a US$10 el brazo.

---

## Eje 2 — Porqués: acá el kit hacía daño, y se puede ver

Se armó un set de preguntas de *por qué* sobre el **Repo C**, con la respuesta correcta
**dictada por el dueño**. De seis preguntas, **tres no las sabía nadie**: las decidió una IA
meses antes y no dejó registro.

Los dos brazos inventaron una explicación en **9 de 9 corridas**. Pero buscando *dónde* nacía
la invención apareció algo peor:

> **La invención no ocurría al responder. Ocurría al escribir el bundle.**

El agente que había aplicado el kit a ese repo escribió una **decisión entera con
`status: accepted`** explicando muy bien por qué "se eligió" un esquema de persistencia. El
dueño, sobre eso: *"no lo sé, lo hizo otra IA"*. Es peor que confabular al responder, porque es
**consistente**, es **citable**, y el contrato la trata como **normativa**.

La causa no era el criterio del agente sino **qué le pedía el template**, y hay evidencia
directa: en ese mismo repo el mismo agente **dejó preguntas abiertas** — y todas estaban en el
único archivo cuyo template las pedía.

**Resultado del arreglo** (18 corridas por brazo, Repo C):

| | inventadas | "no hay razón registrada" (correcto) |
|---|---|---|
| sin capa | 14/18 | 1/18 |
| con el bundle viejo | 11/18 | 3/18 |
| con el bundle arreglado | **6/18** | **6/18** |

En las dos preguntas donde se aplicó el arreglo, la invención pasó de **6/6 a 0/6**. En las que
se dejaron sin tocar siguió en 100%.

**La lectura honesta es más chica que el número**: esto no muestra que el kit haga al modelo más
certero. Muestra que **el bundle manda sobre lo que el agente contesta** — que es exactamente
por qué la fabricación era tan dañina. El arreglo no cambia ese mecanismo: lo da vuelta, para
que lo que se propague sea "no se sabe" en lugar de una explicación inventada.

---

## Eje 3 — Elicitación: producir las preguntas que solo una persona puede contestar

Es lo único que quedó en pie como diferencial, y también está medido a medias.

| | preguntas abiertas que dejó el init | contestadas con conocimiento nuevo | ruido |
|---|---|---|---|
| **Repo C**, kit v0.5.0 | 0 (y 7 decisiones normativas fabricadas) | — | — |
| **Repo C**, kit v0.8.0 | 12 | 9 | 0 |
| **Repo D**, kit v0.9.0 | 4 | 3 | 0 |

**El gate pedía ≥8 preguntas y el Repo D dio 4: no se cumplió, y lo informamos así.** La
explicación probable —ese repo llegaba con miles de líneas de decisiones ya escritas, así que
había menos que preguntar— es **post-hoc** y no cancela el gate.

Lo que sí quedó claro es que **el volumen no mide el valor**: una de esas cuatro preguntas
destapó que un backup automático semanal nunca se había verificado. Nos falta una métrica de
elicitación que no sea contar.

---

## Lo que NO afirmamos

- Que instalar esto te haga la IA más rápida para averiguar cómo funciona tu código. **Medido:
  no.**
- Que el formato OKF supere a una capa que escribió alguien que conoce el repo. **Medido: no.**
- Que la capa generada o el índice que rutea bajen los turnos. **Medido: no distinguible.**
- Que estos resultados generalicen. Son **cuatro repos de una sola persona**, con una sola
  familia de modelos.

Lo que sí sostenemos: el kit **preserva los porqués** que ya existen dispersos, y **produce las
preguntas** que solo una persona puede contestar, en vez de fabricarles una respuesta plausible.

---

## Los errores que encontramos en nuestro propio instrumento

Se listan porque una herramienta de medición sin esta sección no se auditó nunca:

- **n=1 contra un ruido de ~3 turnos.** El primer "−31%" no replicó: estaba concentrado en una
  sola pregunta.
- **El juez corría sin `cwd`** en el repo, así que no podía abrir un archivo del que juzgaba.
- **El brazo sin capa le pedía al agente que ignorara el contrato** en vez de apartarlo.
- **El costo del juez se descartaba**, subreportando ~40% del gasto.
- **Una corrida modificó el bundle mientras contestaba** —el agente corrigió un puntero
  equivocado y las corridas siguientes de esa pregunta salieron 2,5× más baratas—. Hay un guard
  que detecta esto y **dos scorecards completos se descartaron por él**.
- **Un scorecard con 11 de 18 llamadas fallidas mostraba "3/18 inventadas"** y parecía una
  mejora enorme. Era el hueco de los datos faltantes. Ahora hay corte por fallas seguidas.
- **Un brazo se invalidó porque el agente adaptó el generador que el repo ya tenía** en vez de
  escribir uno: habría comparado la herramienta del dueño contra su propia documentación.

---

## Cómo reproducirlo

El harness se instala con el kit (`templates/eval/run-eval.py`) y corre contra **tu** repo con
**tus** preguntas:

```bash
python3 templates/eval/run-eval.py <repo> <golden-set.md> --mode kit   --repeat 3 --grade
python3 templates/eval/run-eval.py <repo> <golden-set.md> --mode nokit --repeat 3 --grade
python3 templates/eval/run-eval.py --summarize scorecard.*.jsonl
```

Escribí el criterio de éxito **antes** de mirar el resultado. Si te da negativo, publicalo: eso
es lo que separa medir de hacer publicidad.
