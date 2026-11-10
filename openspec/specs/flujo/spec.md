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

### Requirement: autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona
Origen: 20261108-233304-ywj-actua · flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona
Tipo: funcional
El sistema DEBE ofrecer `oracle-factory autopilot ID --ejecutar` solo con `--agente`: sin él, DEBE fallar con un error claro sin correr ni escribir nada. El bucle NUNCA DEBE correr un comando de decisión de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `abandonar`, `modo`, `autonomia`, `soltar`, `decidir-union`), aunque la decisión llegue mal clasificada; y DEBE detenerse sin ejecutar nada cuando la decisión es `terminado`, `frenar` o `pedir_a_persona`, mostrando en el último caso el comando listo para pegar.

#### Scenario: sin agente
- DADO que se corre `autopilot ID --ejecutar` sin `--agente`
- CUANDO se ejecuta
- ENTONCES falla con un error que pide `--agente` y no corre ni escribe nada

#### Scenario: una decisión de persona
- DADO un cambio cuyo próximo paso es `cerrar`
- CUANDO corre el bucle
- ENTONCES se detiene sin ejecutar nada y muestra el comando de la persona

#### Scenario: una decisión de persona mal clasificada
- DADO una decisión `actuar` cuyo comando es uno de persona
- CUANDO el bucle va a ejecutarla
- ENTONCES se detiene sin correrla y lo dice

### Requirement: el_bucle_observa_decide_actua_y_vuelve_a_observar
Origen: 20261108-233304-ywj-actua · flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar
Tipo: funcional
El sistema DEBE, en cada vuelta, observar el estado, decidir con `autopilot.decidir`, y si la acción es `actuar` correr el comando de Factory con `--agente NOMBRE` en un proceso aparte, o si es `delegar_al_agente` lanzar el comando de `--lanzar` con la instrucción como último argumento (sin `--lanzar`, detenerse diciendo que falta), y volver a observar después de cada paso.

#### Scenario: un comando mecánico
- DADO una decisión `actuar` con `oracle-factory juzgar ID`
- CUANDO corre el bucle con `--agente a`
- ENTONCES corre `juzgar` con `--agente a`, vuelve a observar y sigue con lo que venga

#### Scenario: trabajo creativo con agente
- DADO una decisión `delegar_al_agente` y `--lanzar COMANDO`
- CUANDO corre el bucle
- ENTONCES lanza COMANDO con la instrucción como último argumento y vuelve a observar

#### Scenario: trabajo creativo sin agente
- DADO una decisión `delegar_al_agente` y sin `--lanzar`
- CUANDO corre el bucle
- ENTONCES se detiene diciendo que falta `--lanzar` y deja la instrucción

### Requirement: el_bucle_tiene_topes_y_se_frena_solo
Origen: 20261108-233304-ywj-actua · flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo
Tipo: funcional
El sistema DEBE detener el bucle cuando se llega al tope de pasos o de minutos (10 y 120 por defecto, `--max-pasos` y `--max-minutos`), cuando la misma decisión con el mismo comando se repite dos veces seguidas (sin progreso), cuando un comando o el agente lanzado terminan con error o no arrancan, o cuando los datos no se pueden leer; en todos los casos DEBE decir el motivo y no volver a actuar.

#### Scenario: el tope de pasos
- DADO un estado que siempre pide actuar con comandos distintos
- CUANDO se llega a `--max-pasos`
- ENTONCES se detiene y lo dice

#### Scenario: sin progreso
- DADO que la misma decisión con el mismo comando aparece dos veces seguidas
- CUANDO corre el bucle
- ENTONCES se detiene por falta de progreso

#### Scenario: un comando falla
- DADO que el comando de un paso termina con error o el agente lanzado no arranca
- CUANDO corre el bucle
- ENTONCES se detiene con el error y no sigue

### Requirement: cada_paso_deja_su_porque_en_el_registro
Origen: 20261108-233304-ywj-actua · flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro
Tipo: funcional
El sistema DEBE dejar, antes de cada paso, un `mensaje` en el registro del cambio, a nombre del agente, con la acción, el motivo y el comando o la instrucción; y al final, otro con el motivo de la detención, y DEBE mostrar un resumen de los pasos (en texto y con `--json`) con el resultado de cada uno.

#### Scenario: el porqué
- DADO un paso `actuar`
- CUANDO se ejecuta
- ENTONCES el registro tiene antes un mensaje del agente con la acción, el motivo y el comando

#### Scenario: el final
- DADO que el bucle se detuvo
- CUANDO termina
- ENTONCES el registro tiene un mensaje con el motivo de la detención y la salida muestra el resumen de los pasos

### Requirement: leer_ignora_los_eventos_que_no_son_objetos
Origen: 20261109-012630-nn6-eventos · flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos
Tipo: funcional
El sistema DEBE ignorar, al leer el registro de un cambio, los elementos de `eventos` que no son objetos y tratar un `eventos` que no es una lista como vacío; DEBE avisar una vez por cambio, por la salida de error, cuántos ignoró; NO DEBE tocar el archivo al leer; y para un registro sano NO DEBE cambiar nada ni avisar.

#### Scenario: un evento que no es un objeto
- DADO un registro cuyos `eventos` traen un número, un texto y `null` además de los eventos de siempre
- CUANDO se lee el cambio
- ENTONCES los datos traen solo los eventos que son objetos, y sale un aviso con la cantidad ignorada

#### Scenario: eventos que no es una lista
- DADO un registro con `eventos` en un texto o un número
- CUANDO se lee el cambio
- ENTONCES `eventos` es una lista vacía y sale el aviso

#### Scenario: un registro sano
- DADO un registro sin eventos raros
- CUANDO se lee el cambio
- ENTONCES los datos son los mismos que antes y no sale ningún aviso

#### Scenario: leer no escribe
- DADO un registro con un evento raro
- CUANDO se lee el cambio
- ENTONCES el archivo queda con los mismos bytes

### Requirement: los_comandos_de_lectura_siguen_funcionando_con_eventos_raros
Origen: 20261109-012630-nn6-eventos · flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros
Tipo: funcional
El sistema DEBE seguir mostrando `estado`, `estado --json` y el conocimiento generado (`kb`) de un cambio cuyo registro tiene eventos que no son objetos, con los demás eventos intactos, sin fallar.

#### Scenario: estado
- DADO un cambio con un evento que no es un objeto
- CUANDO se pide `estado` y `estado --json`
- ENTONCES muestran el estado del cambio con sus eventos válidos, sin error

#### Scenario: kb
- DADO un proyecto con un cambio cuyo registro tiene un evento que no es un objeto
- CUANDO se genera `kb`
- ENTONCES termina sin error y la nota del cambio refleja sus eventos válidos

### Requirement: estado_dice_la_ultima_propuesta_de_revision_de_un_agente
Origen: 20261109-030359-8e4-revprop · flujo_c7819789b58cf6ed1.estado_dice_la_ultima_propuesta_de_revision_de_un_agente
Tipo: funcional
El sistema DEBE ofrecer en `estado --json` la clave `propuesta_de_revision`: la última propuesta de revisión de un agente (decisión, candidato, quién y cuándo), o `null` si no hay ninguna, sin cambiar ningún otro dato del estado, y sin romper con un registro cuyos eventos no se pueden leer.

#### Scenario: con propuesta
- DADO un cambio al que un agente propuso una revisión
- CUANDO se pide `estado --json`
- ENTONCES `propuesta_de_revision` trae la decisión, el candidato, el actor y la fecha de la última propuesta

#### Scenario: sin propuesta
- DADO un cambio sin propuestas
- CUANDO se pide `estado --json`
- ENTONCES `propuesta_de_revision` es `null`

#### Scenario: varias propuestas
- DADO un cambio con dos propuestas de agentes
- CUANDO se pide `estado --json`
- ENTONCES trae la última

### Requirement: el_conductor_delega_la_propuesta_antes_de_pedir_la_revision
Origen: 20261109-030359-8e4-revprop · flujo_c7819789b58cf6ed1.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision
Tipo: funcional
El sistema DEBE, ante un próximo paso `revisar` con un candidato vigente, decidir `delegar_al_agente` (con la instrucción de preparar el informe y proponer la decisión, diciendo que la decisión final es de una persona) cuando no hay una propuesta para ese candidato, y `pedir_a_persona` cuando sí la hay; una propuesta de otro candidato, o un dato de propuesta ilegible, no cuenta; sin candidato vigente la acción no cambia (`pedir_a_persona`); y los frenos y los datos ilegibles siguen yendo primero.

#### Scenario: sin propuesta
- DADO el próximo paso `revisar` con candidato `abc1234` y sin propuesta
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente` y la instrucción nombra `revision-preparar`, `revisar --decision` y que decide una persona

#### Scenario: con propuesta del candidato vigente
- DADO el próximo paso `revisar` con candidato `abc1234` y una propuesta para `abc1234`
- CUANDO el conductor decide
- ENTONCES la acción es `pedir_a_persona` con el comando de la persona

#### Scenario: propuesta de otro candidato
- DADO una propuesta para un candidato anterior
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente`

#### Scenario: con un freno
- DADO el próximo paso `revisar` sin propuesta y un freno
- CUANDO el conductor decide
- ENTONCES la acción es `frenar`

### Requirement: el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada
Origen: 20261109-125752-r6d-freno-visto · flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada
Tipo: funcional
El sistema DEBE dejar de declarar el freno `prueba_existente_editada` cuando hay una revisión aprobada y vigente del cambio (decisión `aprobar`, del mismo producto que el candidato actual y sin problemas), y declararlo cuando hay tests existentes editados y no la hay; los avisos de tests editados siguen mostrándose en ambos casos, y los demás frenos no cambian.

#### Scenario: sin revisión aprobada
- DADO un candidato que editó un test que ya existía y ninguna revisión aprobada vigente
- CUANDO se calculan los frenos
- ENTONCES `prueba_existente_editada` figura entre ellos

#### Scenario: con revisión aprobada vigente
- DADO el mismo candidato con una revisión aprobada y vigente
- CUANDO se calculan los frenos
- ENTONCES `prueba_existente_editada` no figura, y el aviso de test editado sigue en `avisos`

#### Scenario: la revisión deja de ser vigente
- DADO una revisión aprobada de un candidato anterior
- CUANDO se calculan los frenos del candidato nuevo
- ENTONCES `prueba_existente_editada` vuelve a figurar

#### Scenario: otros frenos
- DADO una revisión aprobada vigente y dos juicios de Oracle rojos
- CUANDO se calculan los frenos
- ENTONCES `juicios_rojos` sigue figurando

### Requirement: estado_dice_que_segundo_revisor_falta_en_el_camino_completo
Origen: 20261109-162444-701-segundo-revisor · flujo_c350dc50b9b6cde6a.estado_dice_que_segundo_revisor_falta_en_el_camino_completo
Tipo: funcional
El sistema DEBE ofrecer en `estado --json` la clave `segundo_revisor`: el nombre de un revisor configurado cuyo proveedor todavía no informó, cuando el camino del candidato es completo y los informes de todos los candidatos del cambio cubren menos de dos proveedores distintos; en cualquier otro caso (camino ligero o sin calcular, ya hay dos proveedores, ningún revisor configurado de otro proveedor, configuración o informes ilegibles) DEBE ser `null`, sin cambiar ningún otro dato del estado.

#### Scenario: camino completo con un solo proveedor
- DADO un candidato de camino completo con un informe de `agy` y revisores configurados `agy`, `agy2` (mismo proveedor) y `codex`
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `codex`

#### Scenario: ya hay dos proveedores
- DADO informes de `agy` y de `codex`, aunque sean de candidatos distintos
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null`

#### Scenario: camino ligero
- DADO un candidato de camino ligero con un solo informe
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null`

#### Scenario: sin otro proveedor ni datos legibles
- DADO que sólo hay revisores de un proveedor, o una configuración que no se puede leer
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null` y `estado` no falla

### Requirement: el_conductor_pide_el_segundo_revisor_antes_de_la_revision
Origen: 20261109-162444-701-segundo-revisor · flujo_c350dc50b9b6cde6a.el_conductor_pide_el_segundo_revisor_antes_de_la_revision
Tipo: funcional
El sistema DEBE, ante un próximo paso `revisar` con un `segundo_revisor` válido (texto no vacío de letras, dígitos, punto, guion y guion bajo), decidir `actuar` con el comando mecánico `oracle-factory pedir-revision ID --a ESE_REVISOR`, antes de delegar la propuesta de revisión o pedirle la revisión a una persona; con `segundo_revisor` ausente, `null` o inválido la decisión no cambia; y los frenos y los datos ilegibles siguen yendo primero.

#### Scenario: con segundo revisor
- DADO el próximo paso `revisar` con `segundo_revisor` `codex`
- CUANDO el conductor decide
- ENTONCES la acción es `actuar` y el comando es `oracle-factory pedir-revision ID --a codex`

#### Scenario: sin segundo revisor
- DADO el próximo paso `revisar` con `segundo_revisor` `null` o ausente
- CUANDO el conductor decide
- ENTONCES la decisión es la de siempre (delegar la propuesta o pedir a la persona)

#### Scenario: nombre inválido
- DADO un `segundo_revisor` con espacios o con un `;`
- CUANDO el conductor decide
- ENTONCES la decisión es la de siempre y no corre ese comando

#### Scenario: con un freno
- DADO el próximo paso `revisar` con `segundo_revisor` y un freno
- CUANDO el conductor decide
- ENTONCES la acción es `frenar`

### Requirement: el_segundo_revisor_no_es_uno_que_no_dejo_resultado
Origen: 20261109-194509-ylk-sin-informe · flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado
Tipo: funcional
El sistema DEBE, al calcular `segundo_revisor` en `estado --json`, descartar a un revisor que tenga un lanzamiento sin resultado sobre el candidato vigente, y ofrecer en su lugar el primero (por orden de nombre) de otro proveedor que no tenga ese problema; si no queda ninguno, `segundo_revisor` DEBE ser `null`. Un lanzamiento sin resultado sobre otro candidato, o ya cerrado por un resultado, no descarta a nadie, y el resto de las reglas del `segundo_revisor` no cambia.

#### Scenario: el revisor falló sobre el candidato vigente
- DADO un cambio de camino completo, un informe de `agy`, y un lanzamiento de `codex` sobre el candidato vigente sin resultado
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null` si no hay otro revisor de otro proveedor, y el nombre de otro revisor de otro proveedor si lo hay

#### Scenario: el lanzamiento es de otro candidato o ya terminó
- DADO un lanzamiento sin resultado de `codex` sobre un candidato anterior, o un lanzamiento cerrado por su resultado
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` sigue siendo `codex`

#### Scenario: el conductor no repite el pedido
- DADO el escenario del primer caso con `segundo_revisor` en `null`
- CUANDO el conductor decide sobre el paso `revisar`
- ENTONCES no corre `pedir-revision` y sigue como sin segundo revisor

### Requirement: ante_medir_listar_el_conductor_manda_construir_antes_de_elegir_medidas
Origen: 20261109-201722-oja-construir-primero · flujo_c0d820474143ed460.ante_medir_listar_el_conductor_manda_construir_antes_de_elegir_medidas
Tipo: funcional
El sistema DEBE, ante el próximo paso `medir ID --listar`, mantener la acción `delegar_al_agente` y entregar una instrucción que diga, en este orden: primero construir lo que falte (las pruebas de cada escenario antes que el código, y los catálogos de medidas de los requisitos) sin correr todavía la evidencia completa, después elegir las medidas de cada requisito y proponerlas con `oracle-factory medir ... --requisito R --medida M`, y que confirmarlas es de una persona y que la evidencia se hace después de su confirmación; el motivo, el paso siguiente y el resto de las decisiones del conductor no cambian.

#### Scenario: instrucción completa y en orden
- DADO el próximo paso `medir ID --listar`
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente` y la instrucción nombra construir lo que falte (pruebas primero y catálogos, sin la evidencia completa todavía), proponer las medidas, y que confirmarlas es de una persona y que la evidencia va después, en ese orden

#### Scenario: nada más cambia
- DADO el próximo paso `medir ID --confirmar`, o un freno
- CUANDO el conductor decide
- ENTONCES la decisión es la de siempre (`pedir_a_persona`, o `frenar`)

### Requirement: sin_registros_aparte_nada_cambia
Origen: 20261109-212224-xo0-registros-raiz · flujo_ce4aba0f609f14b30.sin_registros_aparte_nada_cambia
Tipo: funcional
El sistema DEBE tener la raíz de los registros igual a la raíz del producto cuando no se da `--registros`, y en ese caso todos los comandos DEBEN comportarse exactamente como antes (mismas rutas, mismas salidas, mismos registros).

#### Scenario: sin la opción
- DADO un proyecto Factory como los de hoy
- CUANDO se corre cualquier comando sin `--registros`
- ENTONCES la raíz de los registros es la raíz del proyecto y el resultado es el de siempre

### Requirement: con_registros_aparte_el_repo_del_producto_queda_limpio
Origen: 20261109-212224-xo0-registros-raiz · flujo_ce4aba0f609f14b30.con_registros_aparte_el_repo_del_producto_queda_limpio
Tipo: funcional
El sistema DEBE, con `--registros RUTA`, guardar bajo RUTA todo lo que hoy guarda como registro (configuración, carpetas de los cambios, tareas, acuerdos de `openspec/`, conocimiento generado y proyecto Oracle con sus requisitos y catálogos), con las mismas rutas relativas que hoy bajo la raíz del proyecto, y DEBE no crear ni modificar ningún archivo en la raíz del producto con `init`, `nuevo`, `aprobar-spec`, `importar`, `medir`, `mensaje`, `tomar`, `soltar`, `listar` ni `estado`.

#### Scenario: un cambio completo hasta las medidas
- DADO un repo de producto limpio y una carpeta de almacén vacía
- CUANDO se corre `init --registros ALMACEN`, `nuevo`, `aprobar-spec`, `importar` y `medir` con `--registros ALMACEN`
- ENTONCES los registros están bajo ALMACEN y `git status` del producto sigue limpio y sin archivos nuevos

#### Scenario: el producto con su propio git
- DADO el mismo producto con commits propios
- CUANDO se corren esos comandos
- ENTONCES el historial y el árbol de trabajo del producto no cambian

### Requirement: con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno
Origen: 20261109-212224-xo0-registros-raiz · flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno
Tipo: funcional
El sistema DEBE, con `--registros` distinto de la raíz del producto, rechazar `pedir-revision`, `revision-preparar`, `revision`, `revisar`, `juzgar` y `cerrar` con un mensaje que diga que todavía no se admiten con registros aparte (etapa 3 de 6), sin escribir nada y con código de salida distinto de cero, y DEBE hacer que `estado` muestre el cambio sin candidato vigente en vez de fallar.

#### Scenario: un comando de candidato
- DADO un cambio en un almacén aparte
- CUANDO se corre `juzgar --registros ALMACEN`
- ENTONCES falla con el mensaje de la etapa 3 y no cambia ningún archivo, ni del almacén ni del producto

#### Scenario: estado sin candidato
- DADO el mismo cambio
- CUANDO se corre `estado --registros ALMACEN`
- ENTONCES muestra el cambio, sin candidato vigente, y no escribe nada

### Requirement: conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto
Origen: 20261109-233536-jgu-registros-almacen · flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto
Tipo: funcional
El sistema DEBE, con `conectar RUTA` desde una carpeta del producto, guardar en la configuración personal del usuario (`$XDG_CONFIG_HOME/oracle-factory/almacenes.json`, o `~/.config/oracle-factory/almacenes.json`) que el producto usa el almacén RUTA, con el directorio común de Git del producto como clave; DEBE rechazar con un mensaje, sin escribir nada, una RUTA que no exista, que no sea un repo Git, que contenga al producto o esté dentro de él, o una configuración personal ilegible; DEBE preparar la estructura de Factory en el almacén si le falta, sin tocar nunca el repo del producto; y DEBE ser idempotente (conectar dos veces al mismo almacén no cambia nada).

#### Scenario: conectar un almacén nuevo
- DADO un repo de producto limpio y un repo Git vacío como almacén
- CUANDO se corre `conectar ALMACEN`
- ENTONCES el producto queda conectado en la configuración personal, el almacén tiene la estructura de Factory y `git status` del producto sigue limpio

#### Scenario: una ruta que no sirve
- DADO una ruta inexistente, o una carpeta que no es un repo Git, o una carpeta dentro del producto, o una que lo contiene
- CUANDO se corre `conectar` con esa ruta
- ENTONCES falla con un mensaje claro y no cambia nada

#### Scenario: la configuración personal ilegible
- DADO un `almacenes.json` que no se puede leer
- CUANDO se corre `conectar ALMACEN`
- ENTONCES falla sin sobrescribirlo

#### Scenario: conectar dos veces
- DADO un producto ya conectado a ALMACEN
- CUANDO se corre `conectar ALMACEN` otra vez
- ENTONCES no cambia nada y lo dice

### Requirement: con_el_producto_conectado_los_comandos_usan_el_almacen
Origen: 20261109-233536-jgu-registros-almacen · flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen
Tipo: funcional
El sistema DEBE, con el producto conectado, usar el almacén en todos los comandos sin `--registros`, corran desde cualquier subcarpeta del producto o desde cualquiera de sus worktrees, con el mismo comportamiento que `--registros ALMACEN` (etapa 1); `--registros` explícito DEBE mandar sobre la conexión; sin conexión DEBE comportarse exactamente como antes; y una configuración personal ilegible DEBE avisarse y tratarse como «no conectado» sin romper el comando.

#### Scenario: desde una subcarpeta y desde un worktree
- DADO un producto conectado y un worktree del mismo repo
- CUANDO se corre `listar` desde una subcarpeta del producto y desde el worktree
- ENTONCES los dos ven los cambios del almacén y no se crea ningún archivo de Factory en el producto

#### Scenario: la opción explícita manda
- DADO un producto conectado a ALMACEN y otro almacén OTRO
- CUANDO se corre un comando con `--registros OTRO`
- ENTONCES usa OTRO

#### Scenario: sin conexión
- DADO un proyecto Factory de los de hoy, sin conexión
- CUANDO se corre cualquier comando
- ENTONCES se comporta como siempre

### Requirement: conectar_sin_argumentos_y_desconectar
Origen: 20261109-233536-jgu-registros-almacen · flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar
Tipo: funcional
El sistema DEBE, con `conectar` sin argumentos, decir a qué almacén está conectado el producto o que no lo está; DEBE, con `desconectar`, quitar la conexión del producto de la configuración personal sin tocar el almacén ni el producto (y decir que no estaba conectado si no lo estaba); y DEBE negar `conectar` y `desconectar` con `--agente` sin escribir nada, y hacer que el conductor los trate como decisiones de una persona.

#### Scenario: ver y quitar la conexión
- DADO un producto conectado
- CUANDO se corre `conectar` y después `desconectar`
- ENTONCES el primero dice el almacén y el segundo lo quita, dejando el almacén y el producto intactos

#### Scenario: un agente no conecta
- DADO el mismo producto
- CUANDO se corre `conectar ALMACEN` o `desconectar` con `--agente claude-code`
- ENTONCES se niega, no cambia nada, y `autopilot` lo clasifica como paso de persona

### Requirement: un_producto_con_su_propio_factory_conectado_se_niega
Origen: 20261109-233536-jgu-registros-almacen · flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega
Tipo: funcional
El sistema DEBE negarse, con un mensaje que explique el conflicto y sin escribir nada, a correr un comando cuando el producto tiene su propia carpeta `.factory/` y además está conectado a un almacén (sin `--registros` explícito).

#### Scenario: los dos a la vez
- DADO un proyecto Factory de los de hoy que además se conectó a un almacén
- CUANDO se corre `estado`
- ENTONCES se niega con un mensaje que dice que hay que desconectar o migrar, y no cambia nada
