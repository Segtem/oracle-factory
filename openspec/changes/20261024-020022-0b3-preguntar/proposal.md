# Preguntar responde preguntas abiertas sobre el proyecto con fuentes y herramientas

## Why

Brian preguntó «Cuantas tareas cerradas hay?» y recibió ocho pasajes de otros temas, sin respuesta. En main había
56 cambios cerrados, comprobados con `listar --cerrados`; ese número es una observación, no un dato que fijar en código.

Hoy `preguntar` recupera documentos y entrega candidatos con puntuación positiva sin resolver consultas sobre el registro
ni comprobar que esos pasajes respalden la pregunta. Las 22 preguntas de oro sólo miden recuperación documental: pasarlas
no demuestra exactitud de conteos ni capacidad de advertir falta de respaldo.

## What changes

- Admitir preguntas abiertas sobre el proyecto, sin exigir una frase exacta. Un modelo configurado elabora respuestas
  usando documentos recuperados y consultas de sólo lectura al registro. No se limita a entregar fragmentos.
- Resolver cantidades y listados desde el registro vigente, con filtro y fuentes comprobables. Los cálculos los hace
  código sobre los datos, no el modelo contando pasajes. Las consultas simples admitidas funcionan sin modelo generativo.
- Conservar la búsqueda híbrida documental, pero distinguir candidatos de respaldo suficiente. Combinar fuentes cuando
  una explicación lo requiere; si faltan datos, pedir aclaración o decir qué no pudo determinar, sin inventar.
- Llevar el mismo resultado a CLI, JSON, MCP y VS Code, con el contrato versionado y documentado.
- Evaluar por separado exactitud del registro, recuperación documental, respuestas elaboradas con citas y abstención,
  conservando las 22 preguntas previas y agregando variantes, negativos y el caso de Brian.
- Configurar por separado el modelo que redacta y el que produce embeddings. La instalación no elige un modelo
  generativo, descarga modelos ni utiliza un servicio externo sin configuración explícita.

## Out of scope

- Conversación persistente con historial, agentes que editen código o ejecuten acciones desde esta herramienta.
- Garantizar respuesta a toda pregunta, conocimiento general de Internet o consultas entre proyectos.
- Ejecutar SQL, Python, shell o comandos arbitrarios producidos por el modelo. Las herramientas y operaciones son acotadas.
- Abrir agentes desde el tablero, cambiar las decisiones humanas o ampliar MCP con escrituras.
- Cambiar automáticamente el modelo de embeddings, publicar un release o modificar otros repositorios en este cambio.

## Human decisions

La primera spec fue aprobada por Brian, pero excluía un modelo que elaborara respuestas. Esta revisión amplía ese alcance
después de su consulta sobre poder preguntar libremente: necesita una aprobación nueva antes de implementar.
La elección del proveedor y modelo generativo para una corrida real queda explícita antes de configurarlo; aprobar
el diseño no autoriza contratar servicios ni enviar el proyecto a un proveedor externo. Las medidas nuevas se presentan
por grupo, conservando el ≥18/22 documental acordado. Revisión, cierre, integración y push mantienen el flujo humano.
