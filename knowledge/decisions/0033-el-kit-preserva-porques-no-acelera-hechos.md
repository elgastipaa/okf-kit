---
type: Decision
status: accepted
origen: dictado
title: "Lo que el kit promete: preserva porqués y produce preguntas, no acelera la recuperación de hechos"
description: "El −34% que el kit citaba como su mejor número lo produjo el autor humano de esa capa, no el formato; instalar el kit a ciegas no lo reproduce y la promesa se corrige."
tags: [okf, alcance, eval, honestidad]
timestamp: 2026-08-06T00:00:00Z
---

# Contexto

El mejor número del kit —**−34% de turnos y 14/15 de acierto contra 10/15**— se midió con la
capa que **escribió a mano el dueño del repo**. Quedaba sin contestar si ganó el formato OKF o
ganó que esa persona conoce su proyecto.

Se midió: mismo repo, mismas preguntas, y un bundle instalado por `okf-init` **a ciegas** (un
proceso fresco que no vio el golden set). Resultado: el bundle generado quedó **indistinguible
de no tener capa** en recuperación de hechos, y **distinguiblemente peor que la capa humana**.
Agregar la capa generada y la puerta que rutea acercó los números, pero ninguna de las dos
separó por encima del piso del instrumento
([0032](0032-el-instrumento-tiene-un-piso-de-resolucion.md)).

Lo que **sí** ganó en las cuatro condiciones fue la pregunta de **por qué**: ahí el bundle
cosechó razones que una persona había escrito en documentos dispersos y contestó en 3 turnos
contra 5 y 6.

# Decisión

**El kit deja de atribuirse el −34%.** Ese número describe *"lo que gana una capa bien escrita
por alguien que conoce el repo"*, y así se cita.

Lo que `okf-init` entrega, medido y en este orden:

1. **Preserva los porqués** que ya existían dispersos y les da un lugar donde se encuentran.
2. **Produce las preguntas** que solo una persona puede contestar, y las entrega en vez de
   fabricar la respuesta ([0027](0027-una-razon-reconstruida-no-manda.md)).
3. **Entrega un punto de partida correcto** —con su capa generada que no puede mentir y su
   puerta que rutea— **no una capa que compita con una escrita a mano**.

# Consecuencias

- **Es una promesa más chica y defendible**, y sigue siendo la que ninguna plataforma da: la
  memoria nativa de un harness absorbe "guardar contexto", pero no puede **no tener** la
  respuesta y preguntar.
- **El material público del kit no puede prometer ahorro de turnos por instalarlo.** Donde
  aparezca ese framing, es un bug del kit.
- **Publicar esto cuesta y se publica igual** ([0028](0028-la-medicion-manda-y-el-gate-se-escribe-antes.md)
  §4). Un kit que solo publica lo que le conviene no está midiendo: está haciendo publicidad.
- El camino que queda abierto es el de la **elicitación**, y tiene su propia forma de medirse
  —cuántas preguntas produce y cuántas contesta el dueño—, que es barata y no depende del
  instrumento que acaba de tocar su techo.
