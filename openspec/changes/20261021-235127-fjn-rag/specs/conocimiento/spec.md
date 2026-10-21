# Capability: conocimiento

## ADDED Requirements

### Requirement: preguntar devuelve pasajes vigentes con su cita
Tipo: funcional
`oracle-factory preguntar "TEXTO"` (y `--json`) SHALL devolver los pasajes que mejor responden a la pregunta, tomados del vault (`kb/`), de las propuestas, diseños y specs de los cambios, de las specs vigentes y de `docs/`, cada uno con su cita (archivo y sección) y su cambio cuando lo tiene. SHALL dejar afuera las notas de personas por revisar, nombrándolas aparte, y todo lo de un cambio abandonado, y SHALL ser sólo lectura.

#### Scenario: una pregunta sobre una decisión
- GIVEN un proyecto con un cambio cerrado, otro abandonado y una nota de personas por revisar que hablan del mismo tema
- WHEN se pregunta por ese tema
- THEN aparecen pasajes del cambio cerrado con su cita, ninguno del abandonado ni de la nota por revisar, que figura aparte, y nada en el proyecto cambió salvo el índice local

### Requirement: la búsqueda es híbrida y dice qué usó
Tipo: funcional
`preguntar` SHALL ordenar los pasajes fusionando un ranking léxico (sin distinguir tildes ni mayúsculas), uno semántico por embeddings y la cercanía en el grafo del vault (un cambio y sus requisitos), y SHALL decir en cada resultado cuánto aportó cada vía. Sin un proveedor de embeddings disponible, SHALL seguir con lo léxico y el grafo y decirlo.

#### Scenario: una pregunta con otras palabras
- GIVEN un pasaje que explica algo con palabras distintas de las de la pregunta, y un proveedor de embeddings
- WHEN se pregunta con esas otras palabras
- THEN el pasaje aparece entre los primeros por la vía semántica, y sin proveedor la respuesta avisa que es sólo léxica y por el grafo

### Requirement: los embeddings son configurables y locales por defecto
Tipo: funcional
Sin configuración, `preguntar` SHALL pedir los embeddings a Ollama en la máquina local con `qwen3-embedding:0.6b`. `.factory/config.json` SHALL poder elegir otro modelo, otra URL, un proveedor compatible con la API de OpenAI (con la clave en la variable de entorno que nombre) o ninguno, y ningún texto del proyecto SHALL salir de la máquina a una URL que el proyecto no configuró.

#### Scenario: un proyecto sin configuración y otro con un proveedor externo
- GIVEN un proyecto sin `rag` en su configuración, y otro con un proveedor OpenAI apuntando a un servidor de prueba
- WHEN se pregunta en cada uno
- THEN el primero pide los embeddings sólo a la dirección local por defecto, y el segundo sólo a la URL configurada con la clave de su variable

### Requirement: el índice se mantiene solo
Tipo: funcional
El índice SHALL vivir en `.factory/local/rag/` y SHALL actualizarse solo al preguntar cuando cambió el corpus: agrega lo nuevo, borra lo que ya no está y reusa el embedding de cada pasaje que no cambió; un modelo distinto SHALL invalidar sus embeddings. Ninguna persona SHALL tener que reconstruirlo para que las respuestas estén al día.

#### Scenario: el vault cambia entre dos preguntas
- GIVEN un índice armado
- WHEN un cambio se cierra (y su nota se regenera) y se vuelve a preguntar
- THEN la respuesta ya incluye lo nuevo, y sólo se pidieron embeddings de los pasajes que cambiaron

### Requirement: la calidad se mide con preguntas de oro
Tipo: funcional
`oracle-factory preguntar --evaluar --salida CARPETA` SHALL correr las preguntas de `kb/preguntas-de-oro.json` y dejar, para Oracle, por pregunta si algún archivo esperado quedó entre los cinco primeros y en qué puesto, y por corrida los aciertos, el MRR, el modo (con o sin embeddings) y el modelo. Factory SHALL tener sus propias preguntas de oro, aprobadas por una persona, y medir con ellas su RAG.

#### Scenario: evaluar el RAG de Factory
- GIVEN las preguntas de oro de Factory y su vault
- WHEN se evalúa con embeddings
- THEN los hechos dicen, por pregunta y en total, cuántas acertaron, y Oracle juzga con ellos el umbral acordado
