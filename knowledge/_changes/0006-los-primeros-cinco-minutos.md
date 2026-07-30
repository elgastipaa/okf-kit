---
type: Change
title: El primer contacto con el kit deja de tener paredes
description: "Un desconocido puede instalar el kit, migrar un repo con contexto propio y entender qué gana, sin chocarse con un comando que no existe ni con un camino sin salida."
status: active
timestamp: 2026-07-30T02:05:00Z
---

# Por qué

La revisión en frío del vibecoder (anexo `0005-anexo-lente-A-vibecoder.md`) encontró que
**todo lo roto está en los primeros cinco minutos**, que es donde el kit se juega la
adopción de alguien que no conoce al autor. Son bugs, no decisiones de diseño: ninguno
necesita medición para arreglarse, y mientras estén, las mejoras que sí necesitan medición
(cambio [0005](0005-el-instrumento-antes-que-el-kit.md)) no llegan a importar porque el
usuario abandonó antes.

El caso más grave lo **creó** la v0.7.3 al tapar una pérdida de datos: ahora el instalador
aborta ante un `AGENTS.md` escrito a mano y rutea a `okf-migrate` — que nunca menciona al
instalador. El repo modal del vibecoder (el que ya viene conversando con una IA y tiene su
propio `CLAUDE.md`) queda **sin linter, sin hook, sin CI, sin skills de mantenimiento y sin
`kit_version`**, y sin ruta para conseguirlos: `--upgrade` no instala lo que no estaba.

# Resultado esperado (la spec)

- **CUANDO** alguien corre el instalador sobre un repo con `AGENTS.md`/`CLAUDE.md` propio
  → **ENTONCES** el mensaje de error no solo lo manda a `okf-migrate`, sino que dice **cómo
  termina** (preservar lo suyo → instalar la maquinaria → re-mergear).
- **CUANDO** un agente sigue `okf-migrate` de punta a punta → **ENTONCES** el repo queda con
  la maquinaria completa (linter, hook, CI, skills, `kit_version`), no solo con el bundle.
- **CUANDO** un usuario que nunca oyó "OKF" describe su síntoma ("cada sesión le explico el
  proyecto de nuevo") → **ENTONCES** el skill correcto se dispara igual.
- **CUANDO** alguien instala el plugin y tipea el comando que promete el README
  → **ENTONCES** ese comando existe.
- **CUANDO** el README dice cómo revertir la instalación → **ENTONCES** el procedimiento que
  describe realmente la revierte.
- **CUANDO** se instala el kit → **ENTONCES** el `CLAUDE.md` instalado es el shim de una
  línea que promete `GUIDE.md`, sin el comentario de template adentro; **y el gate falla si
  vuelve a pasar** (hoy no lo caza).
- **CUANDO** alguien abre el README → **ENTONCES** lo primero es el problema que resuelve y
  la evidencia, no la definición del formato.

# Fuera de alcance

- Todo lo que depende del instrumento (mecanismo 5, dieta del contrato, `runbooks/checks.md`):
  es el cambio [0005](0005-el-instrumento-antes-que-el-kit.md) y lo que quede en el roadmap.
- Subir a OKF 0.2 y el rediseño largo del README (la reescritura completa del pitch). Acá
  solo entra la apertura, que es parte de los primeros cinco minutos.
- La mueblería de adopción (badges, CONTRIBUTING, asciinema): sigue en "Después".

# Plan / Tareas

- [x] `okf-migrate`: paso que instala la maquinaria preservando el entrypoint del usuario.
- [x] Mensaje de error del instalador: cerrar el ciclo con la receta concreta.
- [x] Disparadores de `okf-init` y `okf-migrate` por síntoma, no por la sigla "OKF".
- [x] README (es + en): `/okf:okf-init` y `/okf:okf-migrate`.
- [x] README (es + en): la revocación real (`git clean` + el hook), no `git checkout`.
- [x] `build_claude()` en el instalador + assert **general** en el gate + su rotura.
- [x] Apertura del README por el problema y la evidencia.
- [x] Taguear la serie 0.7.x (el último tag era v0.6.2).
- [x] Gate + las tres suites en verde; probado adversarialmente contra un repo de fixture.

**Dos bugs que aparecieron probando, no en el análisis:**
- **`--force` borraba lo que git no podía devolver.** El "commiteá antes" del mensaje falló en
  silencio en mi propio fixture (el hook del repo abortó el commit) y el archivo se perdió
  igual. Ahora `--force` se niega si hay cambios sin commitear, y avisa si no hay git.
- **Un assert del gate pasaba por la razón equivocada:** su fixture nunca commiteaba, así que
  con la guarda nueva `--force` abortaba y el hook del usuario "sobrevivía" porque no había
  corrido nada. Arreglado el fixture y separado en dos asserts.

# Decisiones y descubrimientos en el camino

- La guarda de la 0.7.3 es correcta y no se toca: el bug no era abortar, era **no dar salida**.
  Arreglar el destino (`okf-migrate`) es la mitad que faltaba de esa decisión.
- El assert del `CLAUDE.md` se escribe **general**, no como point-fix: cualquier archivo
  instalado que conserve su comentario de cabecera es andamiaje y tiene que fallar. El
  chequeo viejo solo buscaba dos tokens literales, así que un tercer tipo de andamiaje
  pasaba invisible — la misma clase de agujero que la 0.7.3 arregló en el denominador.

# Harvest (al cerrar — NO borres este archivo sin completarlo)

- [ ] Verificado el "Resultado esperado" de arriba (probado de verdad, no asumido)
- [ ] Decisiones/descubrimientos de arriba → `knowledge/decisions/` y `references/` (+ sus index)
- [ ] Conceptos del bundle afectados actualizados
- [ ] Si el harvest creó una **carpeta** nueva, sumala al `# Subdirectories` del index raíz
- [ ] Entrada en `log.md`
- [ ] [roadmap](../roadmap.md) al día: esto sale de "Ahora"; "Después" repriorizado
- [ ] Borrar este archivo (git conserva la historia)
