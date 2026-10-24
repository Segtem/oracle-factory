# Preguntar responde sobre el registro y reconoce los límites de la búsqueda documental

## Why

Brian preguntó «Cuantas tareas cerradas hay?» y recibió ocho pasajes de otros temas, sin respuesta. En main había
56 cambios cerrados, comprobados con `listar --cerrados`; ese número es una observación, no un dato que fijar en código.

Hoy `preguntar` recupera documentos y entrega candidatos con puntuación positiva sin resolver consultas sobre el registro
ni comprobar que esos pasajes respalden la pregunta. Las 22 preguntas de oro sólo miden recuperación documental: pasarlas
no demuestra exactitud de conteos ni capacidad de advertir falta de respaldo.

## What changes

- Resolver cantidades y listados de tareas/cambios de Factory (todos, abiertos, cerrados o abandonados) desde el registro
  vigente, con respuesta directa, filtro aplicado y fuentes comprobables, sin depender de Ollama.
- Conservar la búsqueda híbrida documental, pero distinguir candidatos de respaldo suficiente. Si no encuentra respaldo,
  decirlo; si una consulta de estado excede los filtros admitidos, explicar el límite sin inventar un cálculo.
- Llevar el mismo resultado a CLI, JSON, MCP y VS Code, con el contrato versionado y documentado.
- Evaluar por separado exactitud del registro, recuperación documental y abstención, conservando las 22 preguntas previas
  y agregando variantes, negativos y el caso de Brian. Ningún grupo puede tapar los errores de otro.

## Out of scope

- Un chat generativo o contratar un LLM para redactar respuestas; para los conteos no hace falta.
- Entender cualquier pregunta, estadísticas arbitrarias, filtros temporales o consultas entre proyectos.
- Abrir agentes desde el tablero, cambiar las decisiones humanas o ampliar MCP con escrituras.
- Cambiar el modelo de embeddings, publicar un release o modificar los otros repositorios dentro de este cambio.

## Human decisions

Brian aprueba esta propuesta y su spec antes de implementar. Se propone usar el registro para datos estructurados y
conservar recuperación documental con advertencias, sin proveedor generativo nuevo. Las medidas nuevas se presentan por
grupo para su confirmación, conservando el ≥18/22 documental ya acordado para la medición real con embeddings.
La revisión, cierre, integración y push siguen el flujo humano vigente.
