# Capability: flujo

## ADDED Requirements

### Requirement: con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia
Tipo: funcional
El sistema DEBE, con almacén aparte, tomar como candidato vigente de un cambio el commit del repo del producto más cercano a HEAD (entre los ancestros de HEAD, HEAD incluido) que tenga carpeta de evidencia en el almacén para ese cambio, siempre que no haya diferencias de archivos entre ese commit y HEAD y que el producto no tenga cambios locales (archivos modificados, en el índice o nuevos no ignorados); si no se cumple, el cambio NO DEBE tener candidato vigente; y sin almacén aparte el candidato DEBE seguir calculándose como hasta ahora.

#### Scenario: el commit con evidencia es HEAD
- DADO un producto conectado a un almacén y una carpeta de evidencia del cambio para HEAD
- CUANDO se pide `estado`
- ENTONCES el candidato vigente es HEAD

#### Scenario: commits sin cambios de archivos después
- DADO evidencia para un commit anterior y después un commit vacío (sin cambios de archivos)
- CUANDO se pide `estado`
- ENTONCES el candidato sigue siendo el commit con evidencia

#### Scenario: el producto cambió
- DADO evidencia para un commit y después un commit que cambia un archivo, o un archivo modificado sin commitear
- CUANDO se pide `estado`
- ENTONCES no hay candidato vigente

### Requirement: con_almacen_aparte_la_huella_es_el_producto_y_este_cambio
Tipo: funcional
El sistema DEBE, con almacén aparte, calcular la huella que decide si la revisión y el juicio de un cambio siguen vigentes a partir del repo del producto (su HEAD y sus archivos no ignorados) y de los archivos de ese cambio en el almacén (su propuesta y su spec, sin los registros que Factory genera, sus requisitos y los catálogos de las medidas que tiene elegidas); un cambio en el producto o en esos archivos DEBE dejar vieja la revisión y el juicio, y un cambio en archivos de otro cambio del almacén NO DEBE dejarlos viejos; sin almacén aparte la huella DEBE seguir calculándose como hasta ahora.

#### Scenario: otro cambio del almacén
- DADO un cambio con revisión aprobada y vigente en un almacén aparte
- CUANDO se edita la spec de otro cambio del mismo almacén
- ENTONCES la revisión del primero sigue vigente

#### Scenario: la spec o el producto de este cambio
- DADO el mismo cambio
- CUANDO se edita su propia spec, uno de sus requisitos, el catálogo de una de sus medidas o un archivo del producto
- ENTONCES su revisión deja de estar vigente

### Requirement: con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto
Tipo: funcional
El sistema DEBE, con almacén aparte, permitir `pedir-revision`, `revision-preparar`, `revision`, `revisar`, `juzgar` y `cerrar`, haciendo sobre el repo del producto todo lo que mira el producto (diferencias, base del candidato, el paquete y la copia para los revisores, trazabilidad, alarmas, `log`, `por-que`, `ruta` y `procedencia`); y NO DEBE escribir nada en el producto en todo el ciclo: ni en su árbol de trabajo ni en su `.git` (índice, refs, hooks, configuración ni objetos).

#### Scenario: de punta a punta
- DADO un producto conectado a un almacén y un cambio con su spec aprobada, sus medidas confirmadas y evidencia de su candidato
- CUANDO se pide la revisión a un revisor de prueba, se registra la revisión, se juzga y se cierra
- ENTONCES cada paso funciona, los registros quedan en el almacén, y el árbol de trabajo y el `.git` del producto son idénticos a antes

#### Scenario: lo que mira el producto
- DADO el mismo cambio con candidato
- CUANDO se piden las alarmas, la trazabilidad, `log`, `por-que` y `ruta`
- ENTONCES se calculan sobre el repo del producto

### Requirement: con_almacen_aparte_no_hay_hook_en_el_producto
Tipo: funcional
El sistema DEBE, con almacén aparte, negarse a instalar con `hooks` cualquier hook en el repo del producto, con un mensaje que diga que los commits de un cambio se deducen de sus candidatos y sin escribir nada; y `log ID` DEBE mostrar los commits del cambio deducidos de sus candidatos.

#### Scenario: hooks con almacén aparte
- DADO un producto conectado a un almacén
- CUANDO se corre `hooks`
- ENTONCES se niega con ese mensaje y el `.git` del producto no cambia

#### Scenario: log sin trailer
- DADO un cambio con candidato en un almacén aparte y commits del producto sin el trailer `Cambio: ID`
- CUANDO se corre `log ID`
- ENTONCES muestra el commit del candidato
