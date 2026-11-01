# Capability: practicas

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: la_plantilla_de_tareas_pide_escribir_primero_las_pruebas
Origen: 20261031-011717-c2q-pruebaspractica · practicas_c185a6b4ec26306ce.la_plantilla_de_tareas_pide_escribir_primero_las_pruebas
Tipo: funcional
El sistema DEBE incluir en la plantilla de tareas de un cambio nuevo, en español y en inglés, el paso de escribir primero las pruebas de cada escenario de la spec, antes de implementar.

#### Scenario: un cambio nuevo en español
- DADO un proyecto con Factory inicializado
- CUANDO se crea un cambio nuevo
- ENTONCES su tasks.md tiene el paso de escribir las pruebas de cada escenario, y está antes del paso de implementar

#### Scenario: un cambio nuevo en inglés
- DADO un proyecto con Factory inicializado
- CUANDO se crea un cambio nuevo con el idioma inglés
- ENTONCES su tasks.md tiene ese mismo paso en inglés, y está antes del paso de implementar

### Requirement: el_estado_avisa_de_los_requisitos_sin_pruebas_sin_bloquear
Origen: 20261031-011717-c2q-pruebaspractica · practicas_c185a6b4ec26306ce.el_estado_avisa_de_los_requisitos_sin_pruebas_sin_bloquear
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, de los requisitos que no tienen ningún caso de prueba en la trazabilidad del candidato vigente y de que el candidato no tiene trazabilidad, sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: un requisito sin casos
- DADO un cambio con dos requisitos importados y una trazabilidad del candidato donde uno tiene casos y el otro ninguno
- CUANDO se pide el estado
- ENTONCES el aviso nombra el requisito sin casos y no al otro, y el próximo paso y los pendientes no cambian

#### Scenario: un candidato sin trazabilidad
- DADO un cambio con requisitos importados y un candidato cuyo sensor no dejó trazabilidad
- CUANDO se pide el estado
- ENTONCES el aviso dice que el candidato no tiene trazabilidad de pruebas, y el próximo paso y los pendientes no cambian

#### Scenario: todos con casos
- DADO un cambio cuyos requisitos tienen todos casos en la trazabilidad
- CUANDO se pide el estado
- ENTONCES no hay aviso de pruebas

### Requirement: una_excepcion_declarada_en_la_spec_explica_por_que_no_hay_pruebas
Origen: 20261031-011717-c2q-pruebaspractica · practicas_c185a6b4ec26306ce.una_excepcion_declarada_en_la_spec_explica_por_que_no_hay_pruebas
Tipo: funcional
El sistema DEBE reconocer la línea `Pruebas: no aplica — motivo` de un requisito en su spec, mostrarla en el estado con su motivo y no avisar por falta de pruebas de ese requisito, y DEBE rechazar una excepción sin motivo.

#### Scenario: una excepción con motivo
- DADO un requisito con la línea Pruebas: no aplica y un motivo, y sin casos en la trazabilidad
- CUANDO se pide el estado
- ENTONCES el estado muestra la excepción con su motivo y no avisa de falta de pruebas de ese requisito

#### Scenario: una excepción sin motivo
- DADO un requisito con la línea Pruebas: no aplica y sin motivo
- CUANDO se importa o se pide el estado
- ENTONCES se rechaza diciendo que la excepción necesita un motivo, y el requisito no queda exceptuado

### Requirement: pedir_revision_muestra_la_lista_previa_sin_bloquear
Origen: 20261031-220741-vts-listaprevia · practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear
Tipo: funcional
El sistema DEBE mostrar la lista previa a la revisión cuando se pide una revisión, antes de lanzar al revisor, sin cambiar el pedido que recibe el revisor ni impedir que la revisión se pida.

#### Scenario: se pide una revisión
- DADO un cambio con un candidato listo para revisar y un revisor configurado
- CUANDO se pide la revisión
- ENTONCES la salida muestra la lista previa antes de la línea que anuncia el lanzamiento del revisor, y el revisor se lanza igual

#### Scenario: el pedido no cambia
- DADO el mismo cambio y el mismo candidato
- CUANDO se pide la revisión
- ENTONCES el texto del pedido que recibe el revisor es el mismo que sin la lista

### Requirement: la_lista_previa_tiene_una_sola_fuente
Origen: 20261031-220741-vts-listaprevia · practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente
Tipo: funcional
El sistema DEBE tener la lista previa en un solo lugar de código, con una pregunta por cada clase de problema y la regla de reusar lo existente y arreglar la clase, y DEBE tener un documento docs/lista-previa.md que contenga cada pregunta tal cual, de modo que el mensaje y el documento no puedan divergir.

#### Scenario: el documento y el mensaje dicen lo mismo
- DADO la lista previa del código y el documento docs/lista-previa.md
- CUANDO se comparan
- ENTONCES cada pregunta de la lista aparece en el documento con el mismo texto

#### Scenario: se agrega una pregunta sin actualizar el documento
- DADO una pregunta nueva en la lista del código que el documento no tiene
- CUANDO se corre la comprobación
- ENTONCES la comprobación falla nombrando la pregunta que falta

### Requirement: la_guia_para_agentes_nombra_la_lista_previa
Origen: 20261031-220741-vts-listaprevia · practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa
Tipo: funcional
El sistema DEBE decir en la guía para agentes que genera oracle-factory agentes que existe la lista previa y que se mira antes de pedir una revisión, y DEBE detectar como vieja una guía que no lo dice.

#### Scenario: la guía generada
- DADO un proyecto con Factory inicializado
- CUANDO se genera la guía con oracle-factory agentes
- ENTONCES nombra docs/lista-previa.md y dice que se mira antes de pedir una revisión

#### Scenario: una guía vieja
- DADO una guía para agentes sin esa mención
- CUANDO se verifica con oracle-factory agentes --verificar
- ENTONCES se detecta como vieja

### Requirement: el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro
Origen: 20261101-012816-1qf-testseditados · practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, de los archivos de pruebas que existían en la base del candidato y que el candidato borró, renombró o a los que les quitó líneas, nombrando los tests y la cantidad de aserciones quitadas, sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: se quita un test o una aserción
- DADO un candidato que borra un archivo de pruebas de la base y quita un test y una aserción de otro
- CUANDO se pide el estado
- ENTONCES el aviso nombra los dos archivos, el test quitado y la cantidad de aserciones quitadas, y los pendientes y el próximo paso no cambian

#### Scenario: sólo se agregan tests
- DADO un candidato que agrega tests a un archivo de pruebas existente y agrega un archivo de pruebas nuevo
- CUANDO se pide el estado
- ENTONCES no hay aviso de tests editados

#### Scenario: sin candidato vigente
- DADO un cambio sin candidato vigente
- CUANDO se pide el estado
- ENTONCES no hay aviso y el JSON indica que no se pudo calcular

### Requirement: el_pedido_al_revisor_lleva_los_tests_editados
Origen: 20261101-012816-1qf-testseditados · practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados
Tipo: funcional
El sistema DEBE incluir en el pedido que recibe el revisor la lista de tests existentes que el candidato modificó o borró, con la indicación de nombrarla en su informe, y DEBE dejar el pedido igual cuando no hay ninguno.

#### Scenario: hay tests editados
- DADO un candidato que quita un test existente
- CUANDO se pide la revisión
- ENTONCES el pedido del revisor nombra el archivo y el test quitado y pide mencionarlo en el informe

#### Scenario: no hay tests editados
- DADO un candidato que sólo agrega tests
- CUANDO se pide la revisión
- ENTONCES el pedido es el mismo que antes de este cambio

### Requirement: solo_cuentan_los_archivos_de_pruebas
Origen: 20261101-012816-1qf-testseditados · practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas
Tipo: funcional
El sistema DEBE tomar por archivo de pruebas sólo el que está en una carpeta tests o test, o se llama test_*, *_test.* o *.test.*, y no avisar por otros archivos aunque pierdan líneas.

#### Scenario: un archivo de producto pierde líneas
- DADO un candidato que quita líneas de un archivo de producto que no es de pruebas
- CUANDO se pide el estado
- ENTONCES no hay aviso de tests editados

#### Scenario: nombres de archivos de pruebas
- DADO archivos tests/a.py, pkg/test_b.py, pkg/c_test.go y web/d.test.js
- CUANDO se clasifican
- ENTONCES los cuatro cuentan como archivos de pruebas, y src/contest.py y docs/tests.md no

### Requirement: el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas
Origen: 20261101-205730-dm3-alarmasflujo · practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, cuando se pidió revisión para cuatro o más candidatos distintos, sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: cuatro candidatos revisados
- DADO un cambio al que se pidió revisión para cuatro candidatos distintos
- CUANDO se pide el estado
- ENTONCES el aviso nombra la cantidad de rondas y los pendientes y el próximo paso no cambian

#### Scenario: menos de cuatro
- DADO un cambio con tres candidatos revisados, uno de ellos con dos revisores
- CUANDO se pide el estado
- ENTONCES no hay aviso de bucle: los revisores de un mismo candidato son una ronda

#### Scenario: registro ilegible
- DADO un cambio cuyo registro de eventos no se puede leer
- CUANDO se pide el estado
- ENTONCES no hay aviso y el estado no falla

### Requirement: el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto
Origen: 20261101-205730-dm3-alarmasflujo · practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, cuando el candidato vigente agrega más de 450 líneas en archivos de producto, sin contar los archivos de pruebas, y sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: un candidato grande
- DADO un candidato que agrega 600 líneas a un archivo de producto
- CUANDO se pide el estado
- ENTONCES el aviso nombra las líneas agregadas y sugiere partir el cambio

#### Scenario: las pruebas no cuentan
- DADO un candidato que agrega 100 líneas de producto y 800 líneas en un archivo de pruebas
- CUANDO se pide el estado
- ENTONCES no hay aviso de cambio grande

#### Scenario: justo en el umbral
- DADO un candidato que agrega exactamente 450 líneas de producto
- CUANDO se pide el estado
- ENTONCES no hay aviso

#### Scenario: sin candidato vigente
- DADO un cambio sin candidato vigente
- CUANDO se pide el estado
- ENTONCES no hay aviso y el JSON indica que no se pudo calcular

### Requirement: el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado
Origen: 20261101-205730-dm3-alarmasflujo · practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado
Tipo: funcional
El sistema DEBE documentar en `docs/tests.md` los dos avisos con sus umbrales (4 rondas, 450 líneas) tal como están en el código, y DEBE aclarar que el conteo de aserciones quitadas es aproximado.

#### Scenario: el documento coincide con el código
- DADO los umbrales del código y el texto de `docs/tests.md`
- CUANDO se comparan
- ENTONCES el documento nombra los dos números del código y la palabra «aproximado» junto al conteo de aserciones
