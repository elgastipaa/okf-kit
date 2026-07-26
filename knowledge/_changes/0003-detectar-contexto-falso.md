---
type: Change
title: La divergencia contexto↔código se encuentra barata y la decide el usuario
description: Rankear dónde buscar drift usando resource+git, darle método al Nivel 2, y meter el "Ahora" del roadmap a la auditoría de cumplimiento.
status: active
timestamp: 2026-07-26T00:00:00Z
---

# Por qué

La [medición de la capa de futuro](../decisions/0014-future-layer-measured.md) dejó dos casos
de **contexto falso**: un agente anotó como feature nueva algo que el repo ya tenía, y el
roadmap de un conejillo afirmaba trabajo en curso que la fuente daba por terminado (lo
escribió el propio autor de la medición). El kit ya tiene la maquinaria para cazar eso
—`okf-verify` Nivel 2 (drift descriptivo) y Nivel 4 (cumplimiento), con la regla de que **el
usuario decide** si el bug es el código o el documento— pero no se usa, y las razones son
concretas:

- El **Nivel 2 no tiene método**: el 4 dice "por cada norma buscá su violación, no su
  confirmación"; el 2 solo dice "reportá los smells que veas". Y lo descriptivo es justo la
  dirección donde vive el contexto falso.
- **Nada los dispara**: los dos son "opcional, periódico", explícitamente fuera de CI. Un
  chequeo completo que hay que acordarse de correr no se corre. El problema es el **costo y
  el gatillo**, no la falta de idea — por eso agregar más chequeo completo no lo arregla.
- **`resource:` existe en el frontmatter y no lo mira nadie**, ni el linter.

# Resultado esperado (la spec)

- **CUANDO** se corre el chequeo sobre un bundle con drift **sembrado a propósito** (un
  conteo cambiado, una ruta que se movió, un "Ahora" cuyo trabajo ya está hecho) →
  **ENTONCES** lo encuentra y lo reporta nombrando el concepto y su fuente.
- **CUANDO** se corre sobre un bundle **limpio** → **ENTONCES** no reporta nada. Un detector
  con falsos positivos se deja de correr en dos semanas, igual que el Nivel 4 hoy.
- **CUANDO** un concepto declara `resource:` y el código apuntado cambió mucho desde su
  `timestamp` → **ENTONCES** aparece arriba en el ranking de dónde mirar, calculado **sin
  leer código y sin gastar tokens** (git + frontmatter alcanzan).
- **CUANDO** un concepto **no** declara `resource:` → **ENTONCES** entra igual al muestreo; no
  puede volverse invisible por no tener la clave.
- **CUANDO** el roadmap tiene un ítem en **"Ahora"** cuyo trabajo ya está terminado →
  **ENTONCES** la auditoría lo reporta (hoy el roadmap está excluido del Nivel 4 entero, y
  para "Ahora" esa exclusión está mal: es una afirmación descriptiva, no intención).
- **CUANDO** encuentra algo → **ENTONCES** lo lleva al usuario clasificado (el doc está
  podrido / el código se desvió / ambos cambiaron) **sin resolverlo solo**.

# Fuera de alcance

- **La otra mitad del problema: que el contexto falso sea difícil de *escribir*.** Drift y
  "nació falso" son fallas distintas: una auditoría caza lo que *se volvió* falso, pero el
  roadmap de forgeidle era falso el día que se escribió. El chequeo en momento de escritura
  ya existe medido solo para el disparador de scope creep; generalizarlo va en **su propio
  cambio**, y con medición (criterio de la [0010](../decisions/0010-generated-volatile-facts.md)).
- Automatizar la resolución. El usuario decide; ya es la regla del Nivel 4 y no se toca.
- Meter el Nivel 4 en CI: lee código y cuesta. El ranking sí puede ser determinista; la
  auditoría no.

# Plan / Tareas

- [x] Ranking por churn: `resource:` + `timestamp` + `git log` → lista corta de sospechosos,
      determinista y sin tokens. Vive en `templates/scripts/okf_stale.py` (script aparte)
- [x] Muestreo para los conceptos sin `resource:` — `--rotate` mueve la ventana por semana ISO
- [x] Darle método al Nivel 2, espejando el del 4 ("buscá la contradicción, no la confirmación")
- [x] Meter "Ahora" del roadmap al Nivel 4 (Visión/Después/No-goals quedan fuera: intención pura)
- [x] Sembrar drift a propósito y verificar los dos escenarios — `scripts/okf_stale_test.py`, 8/8, en CI
- [x] Asserts en `okf_selfcheck.py` (80) + sus casos en `okf_selfcheck_test.py` (23)
- [ ] Instalar `okf_stale.py` también donde ya hay OKF (idlerpg/forgeidle usan kit 0.5.0)

# Decisiones y descubrimientos en el camino

- **Va en un script aparte, no en el linter.** `okf_lint.py` responde "¿es OKF válido?" y da
  pass/fail; esto responde "¿por dónde empiezo a buscar?" y **no puede ser un gate** — la
  antigüedad no es un defecto de conformidad. Mezclarlos habría hecho que el linter falle por
  algo que requiere criterio humano.
- **`resource:` se usa mucho más de lo que suponía**: 7/9 conceptos en idlerpg, 8/13 en
  forgeidle, 14/27 en el dogfood, y con rutas reales al código. La clave estaba en el
  frontmatter desde siempre y **nadie la leía** (ni el linter). El ranking no necesitó
  convención nueva: usa lo que el bundle ya tiene.
- **Señal nueva que no estaba en el plan: el sello podrido.** Un concepto commiteado *después*
  de su propio `timestamp` invalida todas las demás señales, porque se calculan **desde** ese
  valor. Salió de correr el script sobre el propio kit: marcó 5 conceptos que yo había editado
  ese mismo día sin re-sellar.
- **El churn encontró drift real en su primera corrida.** Sospechoso #1:
  `runbooks/bootstrap-a-repo.md` → `GUIDE.md`, 11 commits. Verificado a mano: el runbook decía
  "skills, scripts, okf.yml, git hook" y **nunca mencionaba `okf-plan`**, que el `GUIDE` ya
  instalaba. Drift introducido por mí unas horas antes. Corregido.
- **Primer falso positivo, cazado por el criterio acordado.** El sello podrido comparaba
  instantes: los `timestamp` se escriben a medianoche y el commit del mismo día llega horas
  después, así que marcaba conceptos sanos. Se compara por **día**. Sin ese arreglo el script
  reportaba 10 hallazgos de los cuales 5 eran ruido — y un detector que inventa se deja de
  correr, que es exactamente por qué el Nivel 4 no se corre hoy.
- **El test sembrado encontró un defecto de diseño, no del fixture.** El sello podrido trataba
  igual "editado sin re-sellar" que "creado con fecha retroactiva" — y esto último es legítimo
  y frecuente (fechás el concepto el día en que se decidió la cosa, lo commiteás después). El
  falso positivo además **tapaba** la clasificación real de esos conceptos, porque cortaba
  antes de calcular el churn. Ahora exige ≥2 commits: el concepto tuvo que ser **modificado**.
- **El test de inyecciones encontró que un assert mío era demasiado débil.** El de "solo se
  audita Ahora del rumbo" chequeaba que *Ahora* e *intención pura* coexistieran; borré la
  mitad de **inclusión** ("del rumbo se audita solo Ahora") y siguió pasando, porque la mitad
  de **exclusión** alcanzaba para satisfacerlo. Ahora exige las dos. Tercera vez en el día que
  la inyección caza un assert que yo había leído como correcto: **leer un chequeo no dice si
  funciona.**
- **`near()` fallaba con texto envuelto.** En markdown a 90 columnas una frase se parte en dos
  líneas (`intención\n   pura`) y el literal no matchea. Afectaba a todos los asserts de texto.
  Ahora colapsa espacios primero — un assert que falla por el formato del texto es un impuesto.

- **Los conejillos no sirven para validar este script**: sus bundles se escribieron *después*
  del último commit de código, así que el churn es 0 y es correcto que lo sea. La validación
  tuvo que hacerse sobre el dogfood del kit, que sí tiene código moviéndose bajo conceptos
  viejos.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" (probado de verdad, no asumido)
- [ ] Decisiones/descubrimientos → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Si el harvest creó una **carpeta** nueva, sumada al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado
- [ ] Borrar este archivo (git conserva la historia). **Ningún doc permanente puede quedar
      linkeando a `_changes/`** — cortá ese link primero (solo el roadmap linkea acá).
