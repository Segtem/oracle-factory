# Capability: flujo

## ADDED Requirements

### Requirement: conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario
Tipo: funcional
El sistema DEBE, con `conectar URL` (una URL de Git, no una carpeta) desde un producto, clonar el almacén en `$XDG_DATA_HOME/oracle-factory/almacenes/NOMBRE` (o `~/.local/share/oracle-factory/almacenes/NOMBRE`), donde NOMBRE sale del último tramo de la URL sin `.git`, y conectarlo como hace `conectar RUTA`; si esa carpeta ya existe y es un clon de la misma URL, DEBE reusarla sin clonar de nuevo; si existe y es otra cosa, DEBE negarse sin tocar nada; un clon que falla DEBE dejar el producto sin conectar y sin carpetas a medias; y DEBE seguir siendo sólo de una persona.

#### Scenario: conectar desde una URL
- DADO un repo remoto de almacén y un producto sin conectar
- CUANDO una persona corre `conectar URL`
- ENTONCES el almacén queda clonado en la carpeta del usuario y el producto conectado a él

#### Scenario: el clon ya existe
- DADO un clon de esa misma URL en la carpeta del usuario
- CUANDO se corre `conectar URL` otra vez, o desde otro producto
- ENTONCES se reusa sin clonar de nuevo

#### Scenario: la carpeta es otra cosa, o el clon falla
- DADO una carpeta con ese nombre que no es un clon de la URL, o una URL que no se puede clonar
- CUANDO se corre `conectar URL`
- ENTONCES se niega con un mensaje, el producto queda sin conectar y no queda ninguna carpeta a medias

### Requirement: sincronizar_une_los_registros_de_todos_sin_escribir_configuracion
Tipo: funcional
El sistema DEBE, con `sincronizar` desde un producto conectado, traer lo del remoto del almacén y unirlo con lo local usando los drivers de unión de Factory pasados con `git -c` en esa misma orden y el `.gitattributes` del almacén (que DEBE escribir y commitear si falta), de modo que el registro de un mismo cambio editado por dos personas quede unido sin perder eventos de ninguna; DEBE rehacer y commitear lo generado después de unir; NO DEBE escribir ninguna configuración de Git en ningún repositorio; y DEBE hacerlo con el bloqueo del almacén tomado.

#### Scenario: dos personas en el mismo cambio
- DADO dos clones del mismo almacén donde dos personas dejaron mensajes distintos en el mismo cambio
- CUANDO la segunda corre `sincronizar` después de que la primera subió
- ENTONCES el registro del cambio tiene los mensajes de las dos, lo generado está rehecho y commiteado, y la configuración de Git de los repos no cambió

#### Scenario: sin `.gitattributes`
- DADO un almacén sin `.gitattributes`
- CUANDO se corre `sincronizar`
- ENTONCES Factory lo escribe y lo commitea antes de unir

### Requirement: sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias
Tipo: funcional
El sistema DEBE, al terminar `sincronizar`, subir el resultado al remoto sólo si lo corre una persona; con `--agente` DEBE traer y unir pero NO subir, y decirlo; DEBE negarse sin cambiar nada si el almacén tiene cambios sin commitear o no tiene remoto; y si la unión deja un conflicto que los drivers no resuelven, DEBE deshacerla, dejar el almacén como estaba antes de sincronizar y nombrar los archivos que chocaron, con código de salida distinto de cero.

#### Scenario: un agente sincroniza
- DADO cambios nuevos en el remoto y en el almacén local
- CUANDO se corre `sincronizar` con `--agente`
- ENTONCES se trae y se une, el remoto no recibe nada y la salida lo dice

#### Scenario: una persona sincroniza
- DADO lo mismo
- CUANDO una persona corre `sincronizar`
- ENTONCES el remoto queda con la unión

#### Scenario: no se puede sincronizar
- DADO un almacén con cambios sin commitear, o sin remoto, o un conflicto en un archivo que no tiene driver
- CUANDO se corre `sincronizar`
- ENTONCES se niega o deshace la unión, el almacén queda como estaba y la salida dice por qué y qué archivos chocaron
