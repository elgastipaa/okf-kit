# cortito — el ejemplo navegable de okf-kit

Un acortador de links de verdad: Python stdlib + SQLite, 10 archivos, tests en verde, **y sus
bugs**. Está acá para que puedas ver qué produce el kit sobre código real en vez de creerme.

**Nada de este bundle lo escribí a mano.** Se corrió `okf-init` en un proceso limpio, sin
contarle nada del proyecto, y esto es lo que hizo.

## Qué mirar, si tenés dos minutos

| | |
|---|---|
| [`knowledge/index.md`](knowledge/index.md) | **La puerta.** Rutea por necesidad: *"si necesitás X, leé estos 1-3 archivos, y la fuente de verdad es esta"*. No es un índice por tipo. |
| [`knowledge/references/codigos-cortos-en-db-nueva.md`](knowledge/references/codigos-cortos-en-db-nueva.md) | **El mejor hallazgo.** Documentando el código encontró que un piso de seguridad **no se aplicaba** — y que había un test que lo tapaba porque medía otra cosa. |
| [`knowledge/decisions/`](knowledge/decisions/) | Las tres quedaron **`proposed`**, no `accepted`, con `origen: reconstruido`. Dedujo los porqués del código y **se negó a darles autoridad** hasta que una persona los confirme. |
| `--questions` | **8 preguntas abiertas** que el bundle no puede contestar. Eso es lo que el kit produce y ninguna otra herramienta te da: no la respuesta, la pregunta. |

```bash
python3 ../templates/scripts/okf_lint.py      example/knowledge --questions
python3 ../templates/scripts/okf_refs.py      example/knowledge --repo example
python3 ../templates/scripts/okf_decisions.py example/knowledge/decisions --repo example
```

El último dice **0 chequeadas**, y está bien: solo custodia decisiones `accepted`. Estas se
vuelven obligatorias recién cuando alguien contesta los porqués.

## Los dos bugs que encontró

Ninguno los sabía quien escribió el código, y los dos estaban en el repo desde el primer día:

1. **El piso de ids no se aplicaba en una base nueva.** `sqlite_sequence` no tiene fila para la
   tabla hasta el primer `INSERT`, así que el `UPDATE` no hacía nada y el primer código era
   `"1"` — justo lo que el piso existía para evitar. Y el test que "lo cubría" medía
   `encode(FIRST_ID)` en abstracto: **pasaba mientras la propiedad estaba rota**.
2. **Un path inválido devolvía 500** en vez de 404, porque `decode()` reventaba con un
   `ValueError` genérico.

Los dos están arreglados en el código de acá, y los gotchas quedaron como referencia resuelta —
la trampa de SQLite es permanente y el que vuelva a tocar el contador se la come de nuevo.

## Lo que este ejemplo NO es

**No es evidencia.** El repo lo escribió la misma sesión que corrió el init, así que las
preguntas que produjo no miden elicitación. Los números que sí están medidos, con su método y
sus resultados negativos, están en [`../MEASUREMENT.md`](../MEASUREMENT.md).

---

## Correrlo

```bash
python3 -c "from src.server import serve; serve()"      # levanta en :8080
curl -X POST localhost:8080 -d '{"url":"https://example.com"}'
curl -i localhost:8080/<code>
```

## Tests

```bash
python3 -m unittest discover -s tests -t . -q
```

## Flags

Se prenden por entorno: `FLAG_ANALYTICS` (default on), `FLAG_CUSTOM_ALIAS`, `FLAG_QR`.
