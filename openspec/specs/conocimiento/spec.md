# Capability: conocimiento

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: el vault se genera del registro y no se desfasa
Origen: 20261020-140603-kb · conocimiento_cfa7b831bdad34a61.el_vault_se_genera_del_registro_y_no_se_desfasa
Tipo: funcional
`oracle-factory kb` SHALL escribir en `kb/` una nota por cambio (título, fase, responsable, requisitos con su veredicto, decisiones con quién, cuándo y su motivo, riesgos aceptados, commits y mensajes), una por requisito (texto, medidas, cambio que lo trajo y si está vigente) y un índice, enlazadas con wikilinks de Obsidian, con un texto que no depende de cuándo se genera. `kb --verificar` SHALL fallar, sin escribir, si `kb/` no coincide con el registro, y el vault SHALL regenerarse solo en cada decisión que cambia el estado de un cambio.

#### Scenario: un proyecto con un cambio cerrado y otro abierto
- GIVEN un proyecto con un cambio cerrado con revisión, veredicto y un riesgo aceptado, y otro abierto con un responsable
- WHEN se corre oracle-factory kb y después kb --verificar
- THEN hay una nota por cambio y por requisito con esos datos y enlaces que resuelven, y la verificación pasa

#### Scenario: el vault queda viejo
- GIVEN un vault generado
- WHEN una persona aprueba la spec de un cambio, y alguien edita a mano una nota generada
- THEN el vault se regeneró con la aprobación, y kb --verificar falla por la nota editada sin tocarla

### Requirement: una nota humana vence cuando cambian sus fuentes
Origen: 20261020-140603-kb · conocimiento_cfa7b831bdad34a61.una_nota_humana_vence_cuando_cambian_sus_fuentes
Tipo: funcional
Una nota en `kb/notas/` con `fuentes:` en su frontmatter SHALL quedar «por revisar» cuando cambia el contenido de alguna fuente desde que se marcó revisada; `kb --verificar` SHALL listarla y fallar, y `estado` SHALL avisarla en los cambios abiertos que tocaron esa fuente. `oracle-factory kb revisada NOTA` SHALL marcarla revisada sólo desde la terminal de una persona, y una fuente que no existe SHALL ser un error que nombra la nota.

#### Scenario: una guía cuyo archivo cambió
- GIVEN una nota con fuente oracle_factory/cli.py marcada revisada
- WHEN un cambio abierto modifica ese archivo
- THEN kb --verificar falla nombrando la nota y la fuente, estado del cambio lo avisa, y después de kb revisada (persona) pasa

#### Scenario: revisar sin terminal o una fuente que no existe
- GIVEN una nota con una fuente que no existe, y otra por revisar
- WHEN un agente corre kb revisada sobre la segunda, y se pide kb --verificar
- THEN la marca se niega, y la verificación nombra la nota con la fuente inexistente

### Requirement: por qué existe una línea
Origen: 20261020-140603-kb · conocimiento_cfa7b831bdad34a61.por_que_existe_una_linea
Tipo: funcional
`oracle-factory por-que ARCHIVO:LÍNEA` (y `--json`) SHALL ir del commit que escribió esa línea a su cambio (por el trailer, o deducido de sus commits) y SHALL mostrar sus requisitos con su veredicto, las decisiones con quién, cuándo y su motivo, los riesgos aceptados y hallazgos sobre ese archivo, y las notas humanas que lo tienen como fuente; si la línea no es de ningún cambio, SHALL decirlo con su commit. La extensión de VS Code SHALL mostrarlo para la línea del cursor sin modificar nada.

#### Scenario: una línea escrita en un cambio cerrado
- GIVEN un archivo con una línea agregada por un commit de un cambio cerrado que tiene un riesgo aceptado sobre ese archivo, y una nota humana con ese archivo como fuente
- WHEN se pide oracle-factory por-que ARCHIVO:LÍNEA --json, y el comando de VS Code sobre esa línea
- THEN aparecen el commit, el cambio, sus requisitos con veredicto, la aprobación de la spec con quién y cuándo, el riesgo aceptado con su motivo y la nota

#### Scenario: una línea que no es de ningún cambio
- GIVEN una línea escrita por un commit sin trailer y fuera de los commits de cualquier cambio
- WHEN se pide oracle-factory por-que ARCHIVO:LÍNEA
- THEN dice que esa línea no es de ningún cambio de Factory y nombra su commit

### Requirement: preguntar devuelve pasajes vigentes con su cita
Origen: 20261021-235127-fjn-rag · conocimiento_c48413c31f1bcbd66.preguntar_devuelve_pasajes_vigentes_con_su_cita
Tipo: funcional
`oracle-factory preguntar "TEXTO"` (y `--json`) SHALL devolver los pasajes que mejor responden a la pregunta, tomados del vault (`kb/`), de las propuestas, diseños y specs de los cambios, de las specs vigentes y de `docs/`, cada uno con su cita (archivo y sección) y su cambio cuando lo tiene. SHALL dejar afuera las notas de personas por revisar, nombrándolas aparte, y todo lo de un cambio abandonado, y SHALL ser sólo lectura.

#### Scenario: una pregunta sobre una decisión
- GIVEN un proyecto con un cambio cerrado, otro abandonado y una nota de personas por revisar que hablan del mismo tema
- WHEN se pregunta por ese tema
- THEN aparecen pasajes del cambio cerrado con su cita, ninguno del abandonado ni de la nota por revisar, que figura aparte, y nada en el proyecto cambió salvo el índice local

### Requirement: la búsqueda es híbrida y dice qué usó
Origen: 20261021-235127-fjn-rag · conocimiento_c48413c31f1bcbd66.la_busqueda_es_hibrida_y_dice_que_uso
Tipo: funcional
`preguntar` SHALL ordenar los pasajes fusionando un ranking léxico (sin distinguir tildes ni mayúsculas), uno semántico por embeddings y la cercanía en el grafo del vault (un cambio y sus requisitos), y SHALL decir en cada resultado cuánto aportó cada vía. Sin un proveedor de embeddings disponible, SHALL seguir con lo léxico y el grafo y decirlo.

#### Scenario: una pregunta con otras palabras
- GIVEN un pasaje que explica algo con palabras distintas de las de la pregunta, y un proveedor de embeddings
- WHEN se pregunta con esas otras palabras
- THEN el pasaje aparece entre los primeros por la vía semántica, y sin proveedor la respuesta avisa que es sólo léxica y por el grafo

### Requirement: los embeddings son configurables y locales por defecto
Origen: 20261021-235127-fjn-rag · conocimiento_c48413c31f1bcbd66.los_embeddings_son_configurables_y_locales_por_defecto
Tipo: funcional
Sin configuración, `preguntar` SHALL pedir los embeddings a Ollama en la máquina local con `qwen3-embedding:0.6b`. `.factory/config.json` SHALL poder elegir otro modelo, otra URL, un proveedor compatible con la API de OpenAI (con la clave en la variable de entorno que nombre) o ninguno, y ningún texto del proyecto SHALL salir de la máquina a una URL que el proyecto no configuró.

#### Scenario: un proyecto sin configuración y otro con un proveedor externo
- GIVEN un proyecto sin `rag` en su configuración, y otro con un proveedor OpenAI apuntando a un servidor de prueba
- WHEN se pregunta en cada uno
- THEN el primero pide los embeddings sólo a la dirección local por defecto, y el segundo sólo a la URL configurada con la clave de su variable

### Requirement: el índice se mantiene solo
Origen: 20261021-235127-fjn-rag · conocimiento_c48413c31f1bcbd66.el_indice_se_mantiene_solo
Tipo: funcional
El índice SHALL vivir en `.factory/local/rag/` y SHALL actualizarse solo al preguntar cuando cambió el corpus: agrega lo nuevo, borra lo que ya no está y reusa el embedding de cada pasaje que no cambió; un modelo distinto SHALL invalidar sus embeddings. Ninguna persona SHALL tener que reconstruirlo para que las respuestas estén al día.

#### Scenario: el vault cambia entre dos preguntas
- GIVEN un índice armado
- WHEN un cambio se cierra (y su nota se regenera) y se vuelve a preguntar
- THEN la respuesta ya incluye lo nuevo, y sólo se pidieron embeddings de los pasajes que cambiaron

### Requirement: la calidad se mide con preguntas de oro
Origen: 20261021-235127-fjn-rag · conocimiento_c48413c31f1bcbd66.la_calidad_se_mide_con_preguntas_de_oro
Tipo: funcional
`oracle-factory preguntar --evaluar --salida CARPETA` SHALL correr las preguntas de `kb/preguntas-de-oro.json` y dejar, para Oracle, por pregunta si algún archivo esperado quedó entre los cinco primeros y en qué puesto, y por corrida los aciertos, el MRR, el modo (con o sin embeddings) y el modelo. Factory SHALL tener sus propias preguntas de oro, aprobadas por una persona, y medir con ellas su RAG.

#### Scenario: evaluar el RAG de Factory
- GIVEN las preguntas de oro de Factory y su vault
- WHEN se evalúa con embeddings
- THEN los hechos dicen, por pregunta y en total, cuántas acertaron, y Oracle juzga con ellos el umbral acordado

### Requirement: un agente consulta el proyecto por MCP sin poder cambiarlo
Origen: 20261022-161300-f94-mcp · conocimiento_cff5a3575a1b86452.un_agente_consulta_el_proyecto_por_mcp_sin_poder_cambiarlo
Tipo: funcional
`oracle-factory mcp` SHALL atender por la entrada y la salida estándar el protocolo MCP (initialize, tools/list, tools/call) con las herramientas preguntar, estado, buscar, por_que, resumen, log y listar, que SHALL devolver lo mismo que el comando de la CLI correspondiente. Ninguna herramienta SHALL cambiar archivos del proyecto (salvo el índice local de preguntar), un argumento SHALL ser rechazado si no tiene el tipo o la forma esperada (un texto nunca se toma como una opción) y un error SHALL volver como resultado de error de la herramienta sin cortar el servidor.

#### Scenario: un agente pregunta y consulta un cambio
- GIVEN un proyecto con un cambio y su vault
- WHEN un cliente MCP inicializa, lista las herramientas, llama a preguntar, a estado del cambio y a estado de un cambio que no existe, y pasa como texto algo que empieza con guiones
- THEN recibe las siete herramientas, los pasajes y el estado como los da la CLI, un error de herramienta para el cambio inexistente con el servidor todavía atendiendo, el texto buscado tal cual, y el proyecto sin cambios

### Requirement: preguntar desde VS Code
Origen: 20261022-161300-f94-mcp · conocimiento_cff5a3575a1b86452.preguntar_desde_vs_code
Tipo: funcional
La extensión de VS Code SHALL ofrecer «Factory: Preguntar al proyecto», en la paleta de comandos y como botón del tablero, que pide la pregunta y SHALL mostrar en un documento sin guardar los pasajes con su cita, como `oracle-factory preguntar`, sin cambiar nada del proyecto.

#### Scenario: una pregunta desde el editor
- GIVEN la extensión en un proyecto de Factory
- WHEN la persona elige el comando o el botón del tablero y escribe una pregunta
- THEN se abre un documento con los pasajes y sus citas, y si cancela no pasa nada

### Requirement: preguntar elabora respuestas a preguntas abiertas del proyecto
Origen: 20261024-020022-0b3-preguntar · conocimiento_cc12f23b7134ebe23.preguntar_elabora_respuestas_a_preguntas_abiertas_del_proyecto
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
Origen: 20261024-020022-0b3-preguntar · conocimiento_cc12f23b7134ebe23.la_elaboracion_usa_herramientas_acotadas_y_un_modelo_explicito
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
Origen: 20261024-020022-0b3-preguntar · conocimiento_cc12f23b7134ebe23.preguntar_cuenta_y_lista_cambios_desde_el_registro_vigente
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
Origen: 20261024-020022-0b3-preguntar · conocimiento_cc12f23b7134ebe23.la_recuperacion_documental_expone_si_hay_respaldo_suficiente
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
Origen: 20261024-020022-0b3-preguntar · conocimiento_cc12f23b7134ebe23.la_respuesta_conserva_su_significado_en_cli_mcp_y_vs_code
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
Origen: 20261024-020022-0b3-preguntar · conocimiento_cc12f23b7134ebe23.la_evaluacion_distingue_exactitud_relevancia_y_abstencion
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

### Requirement: contar y listar specs
Origen: 20261026-225825-rn5-rag-specs · conocimiento_c6dd9c535b1df9607.contar_y_listar_specs
Tipo: funcional
The system SHALL answer questions of how many and which specs there are directly from the spec folders, reporting the current specs (one per capability) and the specs in open changes as separate numbers, and citing the files it read.

#### Scenario: cuántas specs hay
- GIVEN un proyecto con una spec vigente y un cambio abierto con otra spec
- WHEN se pregunta «cuántas specs hay»
- THEN la respuesta dice 1 vigente y 1 en cambios abiertos, y cita los archivos

#### Scenario: cuáles son
- GIVEN el mismo proyecto
- WHEN se pide la lista de specs
- THEN cada spec aparece con su capacidad, su estado y su ruta

### Requirement: filtro de specs no admitido
Origen: 20261026-225825-rn5-rag-specs · conocimiento_c6dd9c535b1df9607.filtro_de_specs_no_admitido
Tipo: funcional
The system SHALL reject, saying so, a question about specs that carries a filter it does not support, instead of falling back to loose passages.

#### Scenario: filtro por fecha
- GIVEN un proyecto con specs
- WHEN se pregunta «cuántas specs hay desde ayer»
- THEN la respuesta explica que ese filtro no está admitido y no lista pasajes

### Requirement: las demás preguntas no cambian
Origen: 20261026-225825-rn5-rag-specs · conocimiento_c6dd9c535b1df9607.las_demas_preguntas_no_cambian
Tipo: funcional
The system SHALL keep answering questions about tasks and changes, and document questions, exactly as before.

#### Scenario: cambios abiertos
- GIVEN un proyecto con un cambio abierto
- WHEN se pregunta «cuántos cambios abiertos hay»
- THEN la respuesta sigue siendo la del registro de cambios
