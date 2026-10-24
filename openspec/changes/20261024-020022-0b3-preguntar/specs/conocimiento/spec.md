# Capability: conocimiento

## ADDED Requirements

### Requirement: preguntar elabora respuestas a preguntas abiertas del proyecto
Tipo: funcional
Con un modelo generativo configurado, `preguntar` SHALL aceptar preguntas abiertas en lenguaje natural sobre el proyecto
y elaborar respuestas usando documentos recuperados y herramientas de consulta al registro, sin exigir frases exactas
ni limitar la respuesta a una lista de fragmentos. SHALL combinar fuentes cuando corresponda, citar el respaldo de las
afirmaciones verificables y distinguir hechos observados de inferencias. Si falta información o la consulta es ambigua,
SHALL explicarlo o pedir aclaración, sin inventar hechos ni prometer respuesta a cualquier pregunta.

#### Scenario: explicar una decisión con sus consecuencias
- GIVEN un cambio cuya decisión y motivo constan en el registro y cuyo diseño explica sus consecuencias
- WHEN se pregunta por qué se eligió esa solución y qué implica, con dos redacciones distintas no fijadas como comandos
- THEN se elabora una explicación consistente con ambas fuentes, con citas que respaldan los hechos y las inferencias indicadas

#### Scenario: pregunta que combina conocimiento y registro
- GIVEN la documentación de las revisiones y cambios abiertos con hallazgos pendientes
- WHEN se pregunta qué falta revisar en el proyecto y cómo se resuelve
- THEN consulta el registro para identificar pendientes y la documentación para explicar el procedimiento, citando ambos

### Requirement: la elaboración usa herramientas acotadas y un modelo explícito
Tipo: funcional
El modelo generativo SHALL configurarse por separado del de embeddings. SHALL poder usarse un proveedor local Ollama o
uno compatible con OpenAI explícitamente configurado, con credenciales fuera de los archivos versionados. SHALL NOT
elegirse ni descargarse un modelo o usarse un proveedor externo implícito. Las consultas solicitadas por el modelo SHALL
validarse y limitarse a recuperación y operaciones tipadas de sólo lectura sobre datos del proyecto; los cálculos SHALL
ejecutarse en código sobre el registro, nunca contando pasajes. SHALL haber límites de llamadas, tiempo y tamaño, y
SHALL NOT ejecutarse código o shell arbitrario ni decisiones o escrituras por instrucciones del modelo o de una fuente.
Si falta modelo o falla, SHALL avisarlo y conservar las consultas directas y la recuperación disponibles sin inventar una respuesta generada.

#### Scenario: herramientas válidas e inválidas
- GIVEN un modelo que solicita contar cambios, una llamada con argumentos inválidos y otra que intenta escribir
- WHEN se procesan las solicitudes
- THEN sólo se ejecuta la consulta válida, los límites y rechazos son explícitos y el registro permanece intacto

#### Scenario: no hay modelo o el proveedor falla
- GIVEN un proyecto sin modelo generativo y otro cuyo proveedor no responde
- WHEN se pregunta por el estado o por conocimiento
- THEN informa que no hubo elaboración generativa y ofrece sólo resultados directos o pasajes disponibles, sin usar otro proveedor

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
probabilidad de certeza. SHALL NOT enviar texto a un proveedor que el proyecto no haya configurado explícitamente.

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
El texto y JSON de `preguntar` SHALL distinguir respuesta del registro, respuesta elaborada, recuperación documental,
falta de respaldo, necesidad de aclaración y consulta no admitida, con fuentes, herramientas usadas y límites.
SHALL informar por separado los modelos de embeddings y generación. El JSON SHALL tener esquema versionado y documentado.
El botón de VS Code y la herramienta MCP SHALL mostrar el mismo contenido que la CLI, incluidos conteos y advertencias,
y SHALL conservar la operación de sólo lectura salvo el índice local existente.

#### Scenario: preguntar desde los tres clientes
- GIVEN las mismas fuentes y una pregunta de conteo, una abierta que combina fuentes y una sin respaldo
- WHEN se consulta por CLI, MCP y el comando de VS Code
- THEN los clientes conservan resultado, tipo, fuentes y advertencias sin cambiar el registro

### Requirement: la evaluación distingue exactitud relevancia y abstención
Tipo: funcional
La evaluación SHALL conservar las 22 preguntas documentales existentes y agregar consultas al registro, preguntas
abiertas que combinen fuentes y herramientas, variantes reservadas, conteos cero, actualización del registro, filtros
no admitidos y preguntas sin respaldo. SHALL emitir hechos y detalle por pregunta y grupo, distinguiendo exactitud,
recuperación entre los cinco primeros, respaldo de respuestas y citas, abstenciones correctas e incorrectas.
SHALL distinguir pruebas con modelo simulado de una medición con el modelo generativo real elegido por la persona,
e informar ambos modelos, configuración y límites. Las medidas SHALL juzgar los grupos por separado: un buen conteo
SHALL NOT compensar mala recuperación ni abstención generalizada. Se conserva el umbral documental humano ≥18/22 en la
medición real con embeddings; las medidas nuevas requieren la confirmación humana correspondiente.

#### Scenario: evaluar respuestas y errores provocados
- GIVEN las preguntas de evaluación y una corrida real identificada, junto con fixtures deterministas
- WHEN se evalúa y se provoca un conteo incorrecto, un pasaje irrelevante o una abstención ante una guía disponible
- THEN los hechos identifican el grupo y error, y al menos una medida del grupo afectado falla aunque los otros pasen
