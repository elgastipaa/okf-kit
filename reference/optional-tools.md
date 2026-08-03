# Herramientas opcionales

OKF no requiere nada para usarse (markdown + git). Pero algunas herramientas
**externas y opcionales** aceleran ciertos pasos. Nunca son obligatorias: el kit
funciona 100% sin ellas (caminando archivos a mano y con el linter para lo estructural).

---

## Repomix — empaquetar un repo de código para LLMs

> **Para empaquetar o medir el BUNDLE ya no hace falta**: eso lo hace
> `okf_lint.py --pack`, que viene con el kit y no necesita Node (ver Uso 2). Repomix sigue
> siendo útil para lo que el kit no puede hacer: empaquetar **el código** del repo.

[Repomix](https://github.com/yamadashy/repomix) empaqueta un repo (o una carpeta) en
**un solo archivo AI-friendly**, con **conteo de tokens** y compresión opcional. Corre
con `npx repomix@latest` (necesita Node; el primer `npx` lo descarga).

> **No consume tokens de LLM.** Repomix es un tokenizador **local** (Tiktoken): correrlo
> es gratis. El costo en tokens es solo el agente al *leer* su output — y `--compress`
> lo hace más barato que leer el código crudo.

### Uso 1 — Entender el repo (al bootstrapear o migrar)

En vez de caminar manifests/dirs/archivos a mano (ver `GUIDE.md` §3), para repos
medianos/grandes empaquetá todo en un archivo comprimido y leé ese:

```
npx repomix@latest --compress -o /tmp/repo.md
```

`--compress` usa tree-sitter para quedarse con firmas y estructura (~70% menos tokens).
Es un gasto **único al estructurar el proyecto para OKF**; después el contexto se
mantiene incremental con `okf-update`, sin volver a empaquetar. Respeta `.gitignore` y
excluye secretos automáticamente. Útil también para `okf-migrate` (inventariar contexto
disperso rápido).

### Uso 2 — Medir o empaquetar el BUNDLE: ya no hace falta Repomix

**Esto lo hace el propio kit**, sin dependencias de npm:

```
python3 scripts/okf_lint.py knowledge --pack
```

Emite el bundle entero como **un solo markdown** (a stdout) y reporta por stderr cuántos
archivos, caracteres y tokens aproximados tiene. Sirve para las dos cosas: dárselo a una IA
de una sentada, y medir si un `index.md` o un concepto se está yendo de tamaño (smell de
Nivel 2 en `verification.md`, o decidir cuándo partir un bundle según `special-cases.md`).

Dos propiedades que un `cat *.md` no te da:

- **Cada archivo aparece UNA sola vez** y los links entre conceptos quedan como punteros. Un
  pack que inline cada link produce N copias del mismo concepto: fabrica la deriva que el kit
  existe para evitar, adentro del archivo que le das al agente.
- **El orden es el de navegación** desde `index.md`, y lo que no se alcanza desde la raíz sale
  al final y **señalado**. Si lo mezclara, taparía el problema que el linter reporta.

### Notas

- **Opcional siempre.** Si no hay Node, el paso "entendé el repo" se hace a mano y el
  tamaño se juzga a ojo — nada se rompe.
- Repomix tiene un **server MCP**: un agente en Claude Code puede invocarlo como tool en
  vez de por shell, si está configurado.
