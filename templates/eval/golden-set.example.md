# Golden set (EJEMPLO) — copialo y adaptalo a tu repo

Formato leído por `run-eval.sh`. Cada pregunta es un bloque:

- encabezado `### <id> · <category>`  (categorías: `domain`, `where`, `impact`, `ops`, `trap`)
- `- Q:` la pregunta tal cual la haría alguien
- `- expect:` los hechos que una respuesta correcta debe contener **y** el archivo canónico
  que debería citar (es la clave para el juez `--grade`)

El parser solo mira esas tres líneas; el resto del archivo es texto libre para humanos.

---

### q1 · domain
- Q: ¿Para qué sirve el recurso "energía" y cómo se regenera?
- expect: energía limita acciones por tiempo; regenera N/min; vive en docs/systems/energy.md

### q2 · where
- Q: ¿Dónde está implementado el cálculo de daño?
- expect: combat resolver en src/combat/resolve.ts; el wiki rutea desde el codebase-map

### q3 · impact
- Q: Si agrego un enemigo nuevo, ¿qué campos necesito y dónde?
- expect: id, hp, attack, defense; en content/enemies/; ver runbook de authoring

### q4 · ops
- Q: ¿Cómo regenero los hechos del código en la doc?
- expect: comando de generación (ej. npm run wiki:gen); el CI lo verifica

### q5 · trap
- Q: ¿Cómo está integrado el pago con Stripe?
- expect: TRAMPA — no hay integración de pagos en el repo; el agente debe admitir que no
  está documentado en vez de inventar
