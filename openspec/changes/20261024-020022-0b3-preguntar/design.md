# Design

## Diagnóstico

`rag.py:preguntar` fusiona rankings y devuelve hasta ocho pasajes con puntuación positiva. RRF ordena candidatos: su
puntuación no es probabilidad de que respondan. El corpus no agrega registros; `evaluar` sólo busca rutas esperadas
entre los cinco primeros. Se reutilizará la clasificación vigente de `listar`/`tablero`, sin inferir fases de la prosa.

## Resolución

1. Normalizar tildes y mayúsculas y reconocer una familia acotada de consultas de cantidad/listado de cambios o tareas
   de Factory: todos, abiertos, cerrados y abandonados. Negaciones, combinaciones o filtros no admitidos no se convierten
   silenciosamente en otro filtro. «Cómo cerrar tareas» sigue siendo una consulta documental.
2. Para el registro, leer el estado en cada consulta y dar resultado exacto, filtro y fuentes/IDs comprobables, incluso
   cuando el resultado sea cero. No usar embeddings ni contar pasajes.
3. Para conocimiento, conservar corpus vigente, exclusiones y configuración de embeddings; aplicar un criterio explícito
   y probado de respaldo. Calibrarlo con positivos y negativos, sin presentar RRF como confianza. La advertencia será
   «no encontré respaldo suficiente», sin prometer detectar universalmente preguntas sin respuesta.
4. Un filtro de estado fuera del alcance se comunica como no admitido. No usar similitudes documentales para afirmar
   datos del registro. Si se ofrecen pasajes, rotularlos como candidatos.

## Clientes y contrato

La respuesta distingue `registro`, `documentos`, `sin_respaldo` y `consulta_no_admitida`, con pregunta, respuesta directa
cuando existe, filtro, fuentes y pasajes candidatos. Conserva modo/modelo/aportes y notas por revisar. Si cambia el
contrato del JSON actual, se declara un esquema nuevo y se actualizan sus consumidores juntos. CLI, MCP y VS Code
usan el mismo resultado, sin tres lógicas de respuesta ni escrituras nuevas en el proyecto.

## Medición

Fixtures con abiertos, cerrados archivados, abandonados y proyecto vacío comprueban conteos, variantes, fuentes,
actualización tras un cierre e independencia de Ollama. Fixtures documentales separan respuesta relevante, coincidencia
casual y falta de respaldo. Se conserva el conjunto de 22 preguntas y el umbral humano ≥18/22 con embeddings.
Los nuevos grupos informan errores y abstenciones correctas/incorrectas por separado; sus medidas se proponen a Brian.
Las pruebas deterministas no requieren red; la medición real informa modo, modelo y límites, sin ocultar degradaciones.

Cada arreglo tendrá regresión contra el código viejo y mutaciones detectadas. `tools/verify_preguntar.py` producirá
evidencia por contrato y suite completa con fuentes quietas, con catálogos por requisito más corrida completa.
La revisión usará agy y agy2 después de integrar la configuración autorizada en docs.
