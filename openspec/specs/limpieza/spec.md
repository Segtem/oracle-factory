# Capability: limpieza

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: los registros no llevan la ruta privada
Origen: 20261005-193914-quitar-la-ruta · limpieza_c6ac32e7f17eb48b5.los_registros_no_llevan_la_ruta_privada
Tipo: funcional
Los registros que Factory lee (la fuente de los requisitos, incluidos los requisitos previos, y la ruta de los hechos en el registro de cada cambio) SHALL expresar rutas relativas a la raíz del proyecto, sin la ruta de la máquina que los escribió.

#### Scenario: requisito con fuente absoluta
- GIVEN un requisito cuya fuente contiene la ruta absoluta de la máquina del autor
- WHEN se aplica la limpieza
- THEN la fuente queda relativa al proyecto y apunta al mismo documento

#### Scenario: registro con los hechos en ruta absoluta
- GIVEN el registro de un cambio con los hechos del veredicto en ruta absoluta
- WHEN se aplica la limpieza
- THEN la ruta queda relativa y los hechos se siguen verificando por su huella

### Requirement: las decisiones conservan su integridad
Origen: 20261005-193914-quitar-la-ruta · limpieza_c6ac32e7f17eb48b5.las_decisiones_conservan_su_integridad
Tipo: funcional
Cuando la limpieza cambia el contenido de un requisito con una decisión de medidas registrada, SHALL actualizar el hash de esa decisión y dejar un evento que registre el hash anterior y el nuevo, de modo que `estado` no muestre pendientes que antes no tenía.

#### Scenario: cambio cerrado con decisiones de medidas
- GIVEN un cambio cerrado cuyo requisito tiene una decisión con hash
- WHEN se aplica la limpieza
- THEN `estado` muestra lo mismo que antes y el evento documenta el cambio de hash

### Requirement: la evidencia no se reescribe
Origen: 20261005-193914-quitar-la-ruta · limpieza_c6ac32e7f17eb48b5.la_evidencia_no_se_reescribe
Tipo: no funcional
La limpieza SHALL NOT modificar los archivos de `tareas/`, y su verificación SHALL comprobar que cada uno conserva sus mismos bytes.

#### Scenario: evidencia con la ruta histórica
- GIVEN un informe o un paquete de Clue de `tareas/` que contiene la ruta
- WHEN se aplica la limpieza
- THEN el archivo queda byte a byte igual

### Requirement: limpieza repetible y verificable
Origen: 20261005-193914-quitar-la-ruta · limpieza_c6ac32e7f17eb48b5.limpieza_repetible_y_verificable
Tipo: no funcional
La herramienta SHALL ser idempotente, y un verificador SHALL comprobar que ningún registro conserva la ruta, que `tareas/` no cambió y que el estado de cada cambio es el mismo antes y después.

#### Scenario: segunda ejecución
- GIVEN una limpieza ya aplicada
- WHEN se vuelve a ejecutar
- THEN no cambia ningún archivo

#### Scenario: verificación del estado
- GIVEN el estado de todos los cambios antes de limpiar
- WHEN se limpia y se vuelve a consultar
- THEN la salida de estado de cada cambio es la misma, salvo las rutas
