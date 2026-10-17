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
