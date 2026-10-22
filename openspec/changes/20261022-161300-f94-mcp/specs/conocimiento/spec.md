# Capability: conocimiento

## ADDED Requirements

### Requirement: un agente consulta el proyecto por MCP sin poder cambiarlo
Tipo: funcional
`oracle-factory mcp` SHALL atender por la entrada y la salida estándar el protocolo MCP (initialize, tools/list, tools/call) con las herramientas preguntar, estado, buscar, por_que, resumen, log y listar, que SHALL devolver lo mismo que el comando de la CLI correspondiente. Ninguna herramienta SHALL cambiar archivos del proyecto (salvo el índice local de preguntar), un argumento SHALL ser rechazado si no tiene el tipo o la forma esperada (un texto nunca se toma como una opción) y un error SHALL volver como resultado de error de la herramienta sin cortar el servidor.

#### Scenario: un agente pregunta y consulta un cambio
- GIVEN un proyecto con un cambio y su vault
- WHEN un cliente MCP inicializa, lista las herramientas, llama a preguntar, a estado del cambio y a estado de un cambio que no existe, y pasa como texto algo que empieza con guiones
- THEN recibe las siete herramientas, los pasajes y el estado como los da la CLI, un error de herramienta para el cambio inexistente con el servidor todavía atendiendo, el texto buscado tal cual, y el proyecto sin cambios

### Requirement: preguntar desde VS Code
Tipo: funcional
La extensión de VS Code SHALL ofrecer «Factory: Preguntar al proyecto», en la paleta de comandos y como botón del tablero, que pide la pregunta y SHALL mostrar en un documento sin guardar los pasajes con su cita, como `oracle-factory preguntar`, sin cambiar nada del proyecto.

#### Scenario: una pregunta desde el editor
- GIVEN la extensión en un proyecto de Factory
- WHEN la persona elige el comando o el botón del tablero y escribe una pregunta
- THEN se abre un documento con los pasajes y sus citas, y si cancela no pasa nada
