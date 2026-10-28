# Capability: bloqueos

## ADDED Requirements

### Requirement: el_bloqueo_de_aprobar_spec_nombra_la_linea
Tipo: funcional
El sistema DEBE, cuando aprobar una spec se bloquea porque la propuesta, la spec o las tareas todavía tienen la marca de pendiente, decir de cada archivo afectado la primera línea que la tiene, con su número y su texto acortado, y cuántas más quedan en ese archivo.

#### Scenario: una plantilla recién creada
- DADO un cambio recién creado, con las marcas de pendiente de la plantilla en sus tres archivos
- CUANDO una persona intenta aprobar la spec
- ENTONCES el mensaje empieza con «hay que completar y revisar primero» y la ruta del primer archivo, y nombra de cada uno de los tres archivos la línea con su número, su texto y cuántas más quedan

#### Scenario: un solo archivo pendiente
- DADO un cambio con la propuesta y las tareas completas y la spec con una sola marca
- CUANDO una persona intenta aprobar la spec
- ENTONCES el mensaje nombra solo la spec y su línea, y no dice que quedan más

#### Scenario: una línea muy larga
- DADO una línea con la marca de más de 80 caracteres
- CUANDO una persona intenta aprobar la spec
- ENTONCES el mensaje muestra solo los primeros 80 caracteres seguidos de puntos suspensivos

### Requirement: el_bloqueo_de_aprobar_spec_dice_si_falta_un_archivo
Tipo: funcional
El sistema DEBE decir que falta un archivo, y no que hay que completarlo, cuando la propuesta, la spec o las tareas no existen.

#### Scenario: falta el archivo de tareas
- DADO un cambio al que se le borró el archivo de tareas
- CUANDO una persona intenta aprobar la spec
- ENTONCES el mensaje dice que falta ese archivo con su ruta

### Requirement: aprobar_spec_no_cambia_cuando_todo_esta_completo
Tipo: funcional
El sistema DEBE seguir aprobando la spec sin ningún cambio cuando ninguno de los tres archivos tiene la marca de pendiente.

#### Scenario: todo completo
- DADO un cambio con los tres archivos completos
- CUANDO una persona aprueba la spec
- ENTONCES la aprobación se registra como hasta ahora
