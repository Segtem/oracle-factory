# Capability: practicas

## ADDED Requirements

### Requirement: el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro
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
