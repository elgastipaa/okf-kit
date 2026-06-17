# Herramientas opcionales

OKF no requiere nada para usarse (markdown + git). Pero algunas herramientas
**externas y opcionales** aceleran ciertos pasos. Nunca son obligatorias: el kit
funciona 100% sin ellas (caminando archivos a mano y con el linter para lo estructural).

---

## Repomix — empaquetar un repo para LLMs

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

### Uso 2 — Medir el tamaño del bundle (token-sizer)

El linter valida estructura, no tamaño. Para detectar objetivamente un `index.md` o un
concepto **demasiado grande** (smell de Nivel 2 en `verification.md`) o decidir **cuándo
partir** un bundle (`special-cases.md`), medí los tokens:

```
npx repomix@latest knowledge/ --style markdown
```

Repomix imprime un **resumen** (archivos, caracteres, **tokens totales** y los archivos
más pesados por tokens). Para sizing, el agente solo necesita ese resumen impreso, no el
archivo empaquetado entero → barato. Para medir solo los índices (la preocupación central
del progressive disclosure):

```
npx repomix@latest knowledge/ --include "**/index.md"
```

Señal práctica: si un `index.md` pesa desproporcionadamente respecto al resto, agrupá en
subcarpetas; si un concepto domina el conteo, partilo en conceptos enlazados.

### Notas

- **Opcional siempre.** Si no hay Node, el paso "entendé el repo" se hace a mano y el
  tamaño se juzga a ojo — nada se rompe.
- Repomix tiene un **server MCP**: un agente en Claude Code puede invocarlo como tool en
  vez de por shell, si está configurado.
