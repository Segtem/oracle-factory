# Salidas en JSON de la CLI: estado, donde y resumen

- ESTADO: CERRADA
- PRIORIDAD: 45
- ETIQUETAS: revision, ide


## Objetivo

`estado --json`, `donde --json` y `resumen --json` con un esquema versionado y estable: fase, modo, requisitos con medidas y veredicto, pendientes, quién decidió qué, artefactos y rutas. Es la base del IDE y de factory-mcp. Sin cambiar la salida de texto actual.

Parte del plan de revisión en el IDE (tarea 20261005-112955-revision-ide, Brian 2026-10-07): unir requisitos, medidas, veredicto y código para que una persona revise el código hecho por IA por promesa, no por archivo. Las decisiones siguen siendo humanas y pasan por la terminal.

### Nota (2026-10-12 22:15:44 UTC)

2026-10-12, comparación con Docker pedida por Brian: Factory se parece a Docker en la identidad por hash (candidato ≈ imagen por digest; candidato vigente ≈ tag; revisión, hechos y veredicto ≈ atestaciones SBOM/procedencia/firmas; vigencia ≈ caché de capas; estado→próximo paso ≈ compose que reconcilia). No se parece en las decisiones de persona: el modelo ahí es terraform plan/apply o los entornos con aprobadores de GitHub Actions. Lo que conviene copiar: un motor con una API estable y todos los frentes como clientes, como la Engine API con docker, Docker Desktop y los IDE. Esta tarea es esa API: CLI, panel tipo Desktop (cambios con fase y próximo paso, candidatos con su digest e insignias vigentes o vencidas), VS Code y factory-mcp leen el mismo JSON. Mostrar siempre a qué candidato se refiere cada dato (como IMAGE ID). Las decisiones desde una interfaz siguen siendo de una persona identificada, con el mismo registro que la terminal. Opcional: gramática sustantivo + verbo (cambio, candidato, requisito, revision). Prioridad subida de 11 a 45 por pedido de Brian.

### Nota (2026-10-13 18:05:53 UTC)

Hecha por el cambio 20261013-153440-cli-json (integrado en 020cc2b): estado ID --json (oracle-factory.estado/1), donde ID --json (.donde/1) y resumen --json (.resumen/1), con la vigencia de revisión y juicio por las mismas reglas que estado en texto; el texto no cambia (comparado contra referencias generadas con main). Es la API para el IDE, el panel y factory-mcp.
