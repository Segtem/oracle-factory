# Capability: conocimiento

## ADDED Requirements

### Requirement: preguntar cuenta y lista cambios desde el registro vigente
Tipo: funcional
`oracle-factory preguntar` SHALL reconocer consultas de cantidad y listado de tareas o cambios de Factory, para todos,
abiertos, cerrados o abandonados, sin distinguir tildes ni mayúsculas, y SHALL dar el resultado exacto desde el mismo
registro y clasificación que `listar`. SHALL explicar el filtro y dar fuentes comprobables, incluso para cero cambios.
Un cerrado archivado SHALL contar como cerrado; un abandonado SHALL NOT contar como cerrado ni abierto. SHALL leer el
estado en cada consulta sin depender de embeddings ni de un índice documental anterior.

#### Scenario: la pregunta que hizo Brian
- GIVEN dos cambios cerrados archivados, uno abierto y uno abandonado
- WHEN se pregunta «Cuantas tareas cerradas hay?» o «¿Cuántos cambios cerrados hay?»
- THEN responde que hay 2 cerrados, explica qué cuenta y cita las fuentes para comprobarlo

#### Scenario: listado y proyecto vacío
- GIVEN el mismo proyecto y otro sin cambios
- WHEN se pide listar abiertos, contar todos o contar abandonados, con y sin embeddings disponibles
- THEN los resultados corresponden exactamente al registro de cada proyecto, incluido cero, sin llamadas a embeddings

#### Scenario: el registro cambia después de preguntar
- GIVEN una consulta respondida y un índice documental existente
- WHEN se cierra otro cambio y se repite la consulta
- THEN el conteo y las fuentes reflejan el cierre sin reconstrucción manual del índice

### Requirement: la recuperación documental expone si hay respaldo suficiente
Tipo: funcional
Las consultas de conocimiento SHALL conservar búsqueda híbrida sobre fuentes vigentes con sus citas y exclusiones,
y SHALL aplicar un criterio explícito y probado de respaldo para no presentar candidatos irrelevantes como respuesta.
Si no encuentra respaldo suficiente SHALL decirlo. Una consulta de estado con filtros no admitidos SHALL comunicar
su alcance en vez de afirmar un cálculo distinto o deducirlo de pasajes. Un puntaje de ranking SHALL NOT presentarse como
probabilidad de certeza. Este cambio SHALL NOT introducir un proveedor generativo ni nuevos envíos de texto fuera de
la configuración vigente del proyecto.

#### Scenario: coincidencias que no responden
- GIVEN documentos sobre revisión y pruebas, sin información sobre un tema ajeno consultado
- WHEN hay similitudes positivas pero no respaldo según el criterio declarado
- THEN dice «no encontré respaldo suficiente» y no afirma que esos pasajes responden la pregunta

#### Scenario: consulta documental y filtro no admitido
- GIVEN una guía vigente sobre cómo cerrar cambios
- WHEN se pregunta cómo cerrar y, por separado, cuántos se cerraron en un intervalo temporal no admitido
- THEN la primera recupera la guía con cita y la segunda explica el filtro no admitido, sin responder con el total

### Requirement: la respuesta conserva su significado en CLI MCP y VS Code
Tipo: funcional
El texto y JSON de `preguntar` SHALL distinguir respuesta del registro, recuperación documental, falta de respaldo y
consulta de registro no admitida, con sus fuentes y límites. El JSON SHALL tener esquema versionado y documentado.
El botón de VS Code y la herramienta MCP SHALL mostrar el mismo contenido que la CLI, incluidos conteos y advertencias,
y SHALL conservar la operación de sólo lectura salvo el índice local existente.

#### Scenario: preguntar desde los tres clientes
- GIVEN las mismas fuentes y una pregunta de conteo, una documental y una sin respaldo
- WHEN se consulta por CLI, MCP y el comando de VS Code
- THEN los clientes conservan resultado, tipo, fuentes y advertencias sin cambiar el registro

### Requirement: la evaluación distingue exactitud relevancia y abstención
Tipo: funcional
La evaluación SHALL conservar las 22 preguntas documentales existentes y agregar consultas al registro, variantes,
conteos cero, actualización del registro, filtros no admitidos y preguntas sin respaldo. SHALL emitir hechos y detalle
por pregunta y grupo, distinguiendo respuestas exactas, recuperación entre los cinco primeros, abstenciones correctas e
incorrectas. SHALL informar modo, modelo y límites. Las medidas SHALL juzgar los grupos por separado: un buen conteo
SHALL NOT compensar mala recuperación ni abstención generalizada. Se conserva el umbral documental humano ≥18/22 en la
medición real con embeddings; las medidas nuevas requieren la confirmación humana correspondiente.

#### Scenario: evaluar respuestas y errores provocados
- GIVEN las preguntas de evaluación y una corrida real identificada, junto con fixtures deterministas
- WHEN se evalúa y se provoca un conteo incorrecto, un pasaje irrelevante o una abstención ante una guía disponible
- THEN los hechos identifican el grupo y error, y al menos una medida del grupo afectado falla aunque los otros pasen
