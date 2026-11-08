# Capability: flujo

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: un valor del registro que no es una ruta se informa sin caerse
Origen: 20261016-114832-informe-no-texto · flujo_cb386f39710102296.un_valor_del_registro_que_no_es_una_ruta_se_informa_sin_caerse
Tipo: funcional
Cuando el registro de un cambio guarda como informe o decisiones de la revisión, o como informe o hechos del juicio, un valor que no es una ruta de texto, `estado`, `resumen`, `donde` y el próximo paso SHALL responder sin fallar; `estado` SHALL listar un pendiente que nombre ese campo como no válido, y el próximo paso SHALL rehacer lo que ya no vale: la revisión (pedir-revision o revisar), o el juicio (juzgar).

#### Scenario: un informe de revisión que es un número
- GIVEN un cambio juzgado cuyo registro guarda la revisión con informe 5
- WHEN se piden estado, resumen, donde y el próximo paso
- THEN ninguno falla, estado dice que el informe de revisión no es válido y el próximo paso rehace la revisión

#### Scenario: los cuatro campos con valores que no son texto
- GIVEN un cambio juzgado y, de a uno, el informe y las decisiones de la revisión y el informe y los hechos del juicio con un número, una lista o un objeto
- WHEN se piden estado, resumen, donde y el próximo paso
- THEN ninguno falla, estado nombra ese campo como no válido y el próximo paso rehace la revisión para los de la revisión y el juicio para los del juicio

### Requirement: dos procesos que escriben el mismo registro no se pisan
Origen: 20261016-175720-bloqueo-registro · flujo_c467adb55cba3c0a6.dos_procesos_que_escriben_el_mismo_registro_no_se_pisan
Tipo: funcional
Cuando un proceso de Factory va a escribir el registro de un cambio y otro proceso lo cambió desde que el primero lo leyó o escribió por última vez, el primero SHALL NOT reemplazarlo y SHALL decir que el archivo cambió durante la operación; el cambio del otro proceso SHALL quedar. La comparación y el reemplazo SHALL ser una sola operación frente a otro proceso de Factory que escribe en la misma carpeta. Un mismo proceso que lee y escribe el registro varias veces SHALL seguir funcionando como antes.

#### Scenario: otro proceso escribe entre la lectura y la escritura
- GIVEN un proceso que leyó el registro de un cambio
- WHEN otro proceso lo escribe y después el primero lo guarda
- THEN el primero no lo reemplaza, dice que el archivo cambió durante la operación, y el registro conserva lo que escribió el otro

#### Scenario: otro proceso escribe entre la comparación y el reemplazo
- GIVEN un proceso que tiene tomada la carpeta del registro y va a escribirlo
- WHEN otro proceso guarda el registro en ese momento
- THEN el segundo espera a que el primero termine, ve que el registro cambió y no lo reemplaza

#### Scenario: un proceso que lee y escribe varias veces
- GIVEN un proceso que lee el registro y lo guarda dos veces seguidas
- WHEN nadie más lo escribe
- THEN las dos escrituras quedan, sin error

### Requirement: juzgar acepta los hechos de varios sensores
Origen: 20261017-023151-hechos-varios · flujo_c3eeedacc969eee2a.juzgar_acepta_los_hechos_de_varios_sensores
Tipo: funcional
`juzgar` SHALL aceptar `--con` repetido, un archivo de hechos por sensor, y SHALL juzgar con todos a la vez. El registro SHALL guardar cada archivo con su huella; si cualquiera cambia, falta o no es una ruta, el juicio SHALL dejar de valer, `estado` SHALL nombrar ese archivo y el próximo paso SHALL repetir el juicio con los mismos archivos. `donde` SHALL listarlos todos. Con un solo `--con` o sin él, el registro SHALL ser el de siempre.

#### Scenario: un candidato integrado con dos sensores
- GIVEN un cambio revisado cuyo candidato tiene los hechos de dos frentes en dos archivos, con relaciones distintas
- WHEN se juzga con --con en cada archivo
- THEN Oracle juzga los dos juntos, el veredicto es verde y el registro guarda los dos archivos con su huella; donde los lista

#### Scenario: uno de los archivos cambia después del juicio
- GIVEN un juicio verde con dos archivos de hechos
- WHEN cambia el segundo archivo
- THEN el juicio deja de valer, estado nombra ese archivo y el próximo paso es juzgar otra vez con los dos --con

### Requirement: dos sensores no emiten la misma relación
Origen: 20261017-023151-hechos-varios · flujo_c3eeedacc969eee2a.dos_sensores_no_emiten_la_misma_relacion
Tipo: funcional
Si dos archivos de hechos traen la misma relación, `juzgar` SHALL NOT registrar un veredicto y SHALL mostrar el error de Oracle, que nombra la relación y los dos archivos.

#### Scenario: dos frentes que emiten la misma relación
- GIVEN un cambio revisado y dos archivos de hechos que traen la misma relación
- WHEN se juzga con los dos
- THEN juzgar falla con el error de Oracle, que nombra la relación y los dos archivos, y el registro no guarda veredicto

### Requirement: un pedido de revisión cortado queda a la vista
Origen: 20261017-135953-higiene · flujo_cecdfd053bebfee21.un_pedido_de_revision_cortado_queda_a_la_vista
Tipo: funcional
`pedir-revision` SHALL registrar el lanzamiento del revisor (revisor y candidato) antes de correrlo y su resultado al terminar, también si se interrumpe. Mientras un lanzamiento no tenga resultado, `estado` y `estado --json` (en `avisos`) SHALL avisar qué revisor se lanzó, cuándo y sobre qué candidato, y que no dejó resultado.

#### Scenario: un revisor que se corta sin terminar
- GIVEN un cambio con un candidato
- WHEN se lanza un revisor y el proceso de pedir-revision termina antes de que el revisor deje resultado
- THEN el registro tiene el lanzamiento, y estado avisa que ese revisor se lanzó sobre ese candidato y no dejó resultado

#### Scenario: un revisor que termina, o se interrumpe con Ctrl-C
- GIVEN un cambio con un candidato
- WHEN un revisor termina, o el pedido se interrumpe con Ctrl-C
- THEN queda su resultado (o «interrumpido») y estado no avisa de un lanzamiento sin resultado

### Requirement: las acciones sin autor se avisan
Origen: 20261017-135953-higiene · flujo_cecdfd053bebfee21.las_acciones_sin_autor_se_avisan
Tipo: funcional
Si el registro de un cambio tiene acciones sin autor identificado, `estado` y `estado --json` SHALL avisar cuántas y cuáles, y que un agente las hace con `--agente NOMBRE`.

#### Scenario: un agente que se olvidó de --agente
- GIVEN un cambio creado e importado sin --agente y sin una persona identificada
- WHEN se pide estado
- THEN avisa que esas acciones quedaron sin autor y cómo identificarlo la próxima vez

### Requirement: init no deja carpetas que Factory no usa
Origen: 20261017-135953-higiene · flujo_cecdfd053bebfee21.init_no_deja_carpetas_que_factory_no_usa
Tipo: funcional
`init` SHALL NOT dejar en el proyecto carpetas de Oracle vacías que Factory no usa (`corpus`, `relaciones`, `diferencial`) si las creó al inicializar, y SHALL NOT tocar las que ya existían. El bloqueo de `medir` SHALL vivir dentro de `.factory/local/` y el `.gitignore` que arma `init` SHALL NOT nombrar `.factory-demo/`.

#### Scenario: un proyecto nuevo
- GIVEN una carpeta vacía
- WHEN se corre init y después se miden requisitos con medir
- THEN no quedan corpus, relaciones ni diferencial vacíos, el bloqueo de medir se tomó en .factory/local/locks, y el .gitignore no nombra .factory-demo

#### Scenario: un proyecto con carpetas de Oracle propias
- GIVEN un proyecto que ya tiene corpus/ con casos
- WHEN se corre init
- THEN corpus/ y sus casos siguen igual

### Requirement: una spec de otra capacidad no se pierde en silencio
Origen: 20261020-173143-avisos · flujo_c36d8b0a54786f254.una_spec_de_otra_capacidad_no_se_pierde_en_silencio
Tipo: funcional
`aprobar-spec` SHALL negarse, sin registrar nada, si el cambio tiene en `specs/` una spec de otra capacidad que la suya, y SHALL nombrar esas specs y decir que Factory importa sólo la de su capacidad.

#### Scenario: un cambio con dos specs
- GIVEN un cambio de la capacidad uno con specs/uno/spec.md y specs/dos/spec.md
- WHEN una persona corre aprobar-spec, y después de quitar specs/dos lo corre otra vez
- THEN la primera vez se niega nombrando specs/dos/spec.md y el registro no cambia, y la segunda aprueba

### Requirement: reimportar no deja requisitos huérfanos
Origen: 20261020-173143-avisos · flujo_c36d8b0a54786f254.reimportar_no_deja_requisitos_huerfanos
Tipo: funcional
`importar` SHALL quitar de `requisitos/` los requisitos que una importación anterior del mismo cambio escribió y la nueva ya no trae, y SHALL NOT tocar los requisitos de otros cambios.

#### Scenario: una spec aprobada otra vez
- GIVEN un cambio con sus requisitos importados y otro cambio con los suyos
- WHEN se edita la spec del primero, se aprueba de nuevo y se importa
- THEN requisitos/ tiene los nuevos del primero, no los de su importación anterior, y los del otro cambio siguen igual

### Requirement: un requisito que quedó sin medir se avisa a tiempo
Origen: 20261020-173143-avisos · flujo_c36d8b0a54786f254.un_requisito_que_quedo_sin_medir_se_avisa_a_tiempo
Tipo: funcional
`estado` (y `--json`) SHALL avisar, en cuanto un requisito tiene sus medidas decididas y su `.requisito` todavía dice `sin_medir`, cuál es y qué hacer; y el error de cobertura de `juzgar` SHALL nombrar esos requisitos.

#### Scenario: medidas confirmadas con la marca todavía puesta
- GIVEN un cambio con un requisito cuyas medidas se decidieron sin quitar sin_medir
- WHEN se pide estado y después juzgar
- THEN estado lo avisa con el requisito y cómo seguir, y juzgar se niega nombrándolo

### Requirement: la guía para agentes se genera y no se desactualiza
Origen: 20261022-215347-y70-agentes · flujo_cbbf375bdcabddbc9.la_guia_para_agentes_se_genera_y_no_se_desactualiza
Tipo: funcional
`oracle-factory agentes` SHALL escribir en `AGENTS.md` (creándolo si falta) un bloque entre marcas, armado desde la CLI, con quién decide qué en cada modo de trabajo según `modos.via_agente` (marcando el modo por defecto del proyecto), los comandos de una persona y los de un agente con `--agente`, cómo ver el próximo paso y cómo consultar el proyecto (estado, preguntar, por-que y el MCP); SHALL conservar lo que está fuera del bloque y SHALL agregar `@AGENTS.md` al `CLAUDE.md` si no lo tiene. `--verificar` SHALL fallar sin escribir si el bloque falta o no coincide, e `init` SHALL escribirlo.

#### Scenario: un proyecto con su propio AGENTS.md
- GIVEN un proyecto con un AGENTS.md escrito por personas y un CLAUDE.md sin la línea
- WHEN se corre agentes, se cambia el modo por defecto del proyecto y se corre agentes --verificar
- THEN el bloque está, con la tabla de quién decide y los comandos, lo de las personas sigue igual, CLAUDE.md tiene @AGENTS.md, y la verificación falla por el modo nuevo hasta que se vuelve a correr agentes

### Requirement: la guía dice lo que hace la CLI
Origen: 20261022-215347-y70-agentes · flujo_cbbf375bdcabddbc9.la_guia_dice_lo_que_hace_la_cli
Tipo: funcional
Cada comando que la guía presenta como decisión de una persona SHALL negarse cuando lo corre un agente con `--agente`, o dejar sólo una propuesta sin decidir; y cada comando que presenta como de un agente SHALL aceptar `--agente`. Una prueba SHALL recorrer la lista de la guía y comprobarlo, de modo que la guía no pueda prometer algo que la CLI no hace.

#### Scenario: un agente intenta las decisiones de una persona
- GIVEN un cambio en modo confirmación
- WHEN un agente corre con --agente cada comando que la guía marca como de una persona
- THEN cada uno se niega o deja sólo una propuesta, y el registro no tiene ninguna decisión a nombre del agente

### Requirement: los_frenos_salen_de_los_datos_del_cambio
Origen: 20261108-203356-puy-frenos · flujo_cf63459721e7fb9ac.los_frenos_salen_de_los_datos_del_cambio
Tipo: funcional
El sistema DEBE calcular, solo con los registros del cambio, su candidato vigente y Git, los frenos del cambio, cada uno con un identificador y un motivo: `juicios_rojos` (los dos últimos juicios de Oracle son rojos), `hallazgo_alto_abierto` (un informe del candidato vigente trae un hallazgo de severidad alta y no hay una revisión aprobada vigente), `prueba_existente_editada`, `cambio_grande` y `bucle_de_revision` (los dos últimos con los umbrales que ya usa `estado`). Un dato que no se puede leer NO DEBE producir un freno ni romper `estado`.

#### Scenario: dos juicios rojos seguidos
- DADO un cambio cuyos dos últimos juicios de Oracle terminaron con código distinto de cero
- CUANDO se calculan los frenos
- ENTONCES figura `juicios_rojos` con su motivo

#### Scenario: un juicio rojo y uno verde
- DADO un cambio con un juicio rojo y después uno verde, o con un solo juicio rojo
- CUANDO se calculan los frenos
- ENTONCES no figura `juicios_rojos`

#### Scenario: hallazgo alto sin revisión aprobada
- DADO un informe del candidato vigente con un hallazgo de severidad alta y sin revisión aprobada vigente
- CUANDO se calculan los frenos
- ENTONCES figura `hallazgo_alto_abierto`; con una revisión aprobada vigente, no

#### Scenario: datos ilegibles
- DADO un registro con eventos que no se pueden leer, o un informe sin hallazgos legibles
- CUANDO se calculan los frenos
- ENTONCES no se inventa ningún freno y `estado` sigue funcionando

### Requirement: estado_muestra_los_frenos
Origen: 20261108-203356-puy-frenos · flujo_cf63459721e7fb9ac.estado_muestra_los_frenos
Tipo: funcional
El sistema DEBE mostrar los frenos en `estado --json` como la clave `frenos` (lista de objetos con `id` y `motivo`, vacía si no hay) y en `estado` como avisos que empiezan con «FRENO:», sin cambiar el próximo paso, los pendientes ni ningún otro dato del estado.

#### Scenario: con frenos
- DADO un cambio con un freno
- CUANDO se pide `estado --json` y `estado`
- ENTONCES el JSON lo lista en `frenos` y el texto trae un aviso «FRENO:» con el mismo motivo

#### Scenario: sin frenos
- DADO un cambio sin frenos
- CUANDO se pide `estado --json`
- ENTONCES `frenos` es una lista vacía y no hay avisos «FRENO:»

#### Scenario: un freno no decide nada
- DADO un cambio con un freno
- CUANDO se pide su estado
- ENTONCES el próximo paso y los pendientes son los mismos que sin el freno

### Requirement: el_conductor_decide_el_siguiente_paso_por_reglas
Origen: 20261108-220606-51z-autopilot · flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas
Tipo: funcional
El sistema DEBE decidir, solo con los datos de `estado` del cambio y por reglas fijas, una acción entre `terminado`, `frenar`, `pedir_a_persona`, `delegar_al_agente` y `actuar`, con el comando o la instrucción, quién actúa y el motivo de la regla. Un comando de decisión de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `abandonar`, `modo`, `autonomia`, `soltar`, `decidir-union`) DEBE ser siempre `pedir_a_persona`; un comando mecánico (`importar`, `juzgar`, `pedir-revision`, `revision-preparar`, `tomar`, `mensaje`) DEBE ser `actuar`; un paso escrito en prosa (corregir, commitear, resolver) o elegir medidas DEBE ser `delegar_al_agente`; y si un paso de revisión llega sin candidato, la acción es construir, también `delegar_al_agente`.

#### Scenario: una decisión de persona
- DADO un cambio cuyo próximo paso es `oracle-factory cerrar ID`
- CUANDO el conductor decide
- ENTONCES la acción es `pedir_a_persona`, con ese comando listo para pegar

#### Scenario: un comando mecánico
- DADO un cambio cuyo próximo paso es `oracle-factory juzgar ID`
- CUANDO el conductor decide
- ENTONCES la acción es `actuar` y el actor es un agente

#### Scenario: trabajo creativo
- DADO un próximo paso en prosa («corregí los hallazgos…») o `medir ID --listar`
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente`

#### Scenario: construir
- DADO un cambio sin candidato vigente cuyo próximo paso es pedir la revisión
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente` y la instrucción es construir primero

### Requirement: el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce
Origen: 20261108-220606-51z-autopilot · flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce
Tipo: funcional
El sistema DEBE frenar, antes de cualquier otra regla, cuando el cambio tiene algún freno de `estado`, cuando el próximo paso no es uno que el conductor reconoce, o cuando faltan archivos del cambio; y DEBE decir `terminado` cuando el cambio está cerrado o abandonado y no tiene próximo paso. Frenar nunca trae un comando para actuar.

#### Scenario: un freno
- DADO un cambio con un freno y un próximo paso mecánico
- CUANDO el conductor decide
- ENTONCES la acción es `frenar`, con los frenos y sin comando

#### Scenario: un paso desconocido o archivos faltantes
- DADO un próximo paso que no empieza con `oracle-factory` ni con un verbo conocido, o que dice que faltan archivos
- CUANDO el conductor decide
- ENTONCES la acción es `frenar` y el motivo lo dice

#### Scenario: un cambio terminado
- DADO un cambio cerrado
- CUANDO el conductor decide
- ENTONCES la acción es `terminado`

### Requirement: autopilot_solo_lee_y_lo_muestra
Origen: 20261108-220606-51z-autopilot · flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra
Tipo: funcional
El sistema DEBE ofrecer `oracle-factory autopilot ID`, de solo lectura, que muestre la decisión en texto y con `--json` (acción, quién, comando, instrucción, motivo y frenos), sin escribir nada en el proyecto ni en el registro del cambio, y que falle con un error claro si el cambio no existe.

#### Scenario: la decisión en texto y en JSON
- DADO un cambio con próximo paso
- CUANDO se corre `autopilot ID` y `autopilot ID --json`
- ENTONCES las dos dicen la misma acción y el mismo comando

#### Scenario: no escribe
- DADO un cambio
- CUANDO se corre `autopilot ID`
- ENTONCES el registro del cambio y el árbol de trabajo quedan idénticos

#### Scenario: un cambio que no existe
- DADO un identificador que no existe
- CUANDO se corre `autopilot ID`
- ENTONCES falla con un error que nombra el identificador
