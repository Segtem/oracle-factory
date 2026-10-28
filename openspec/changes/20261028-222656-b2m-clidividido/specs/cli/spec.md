# Capability: cli

## ADDED Requirements

### Requirement: la_cli_se_comporta_igual_tras_partirse
Tipo: funcional
El sistema DEBE conservar, tras partir cli.py en módulos, todos los nombres que oracle_factory.cli exportaba con las mismas firmas, la misma ayuda en cada subcomando y el mismo comportamiento ante las pruebas existentes, sin modificarlas.

#### Scenario: los nombres y las firmas
- DADO la lista de nombres de primer nivel de cli y la firma de cada función, tomada antes de mover nada
- CUANDO se parte cli.py
- ENTONCES todos los nombres siguen en oracle_factory.cli, son los mismos objetos que usa el código movido y sus firmas son idénticas

#### Scenario: la ayuda
- DADO el texto de ayuda de oracle-factory y de cada subcomando con un ancho de terminal fijo, tomado antes de mover nada
- CUANDO se parte cli.py
- ENTONCES la ayuda de cada uno es idéntica

#### Scenario: las pruebas existentes
- DADO la suite completa anterior al cambio
- CUANDO se corre sobre el código partido
- ENTONCES pasan todas, sin ninguna omitida

### Requirement: lo_movido_lee_a_cli_en_el_momento_de_usarlo
Tipo: funcional
El sistema DEBE hacer que el código movido a otros módulos lea los valores y las funciones de cli en el momento de usarlos, de modo que un valor cambiado en cli, como la raíz del proyecto en una prueba, valga también para lo movido.

#### Scenario: un valor cambiado en cli
- DADO un valor de cli cambiado temporalmente, como su raíz o una función auxiliar
- CUANDO se ejecuta una función movida que lo usa
- ENTONCES usa el valor cambiado y no el original

#### Scenario: ningún nombre de cli queda copiado
- DADO el código fuente de los módulos nuevos
- CUANDO se lo analiza
- ENTONCES ninguna función movida usa un nombre definido en cli como si fuera propio, sino a través de cli

### Requirement: ningun_archivo_fuente_pasa_del_tope
Tipo: funcional
El sistema DEBE mantener cada archivo fuente del paquete por debajo de 200000 bytes y cli.py por debajo de 160000, para quedar lejos del límite de 256000 de Oracle Clue.

#### Scenario: los tamaños actuales
- DADO el paquete oracle_factory tras partir cli.py
- CUANDO se miden sus archivos fuente
- ENTONCES cli.py mide menos de 160000 bytes y ninguno mide 200000 o más

#### Scenario: un archivo que crece de más
- DADO un archivo fuente del paquete que supera 200000 bytes
- CUANDO se corre la prueba de tamaños
- ENTONCES falla nombrando el archivo, su tamaño y el límite de Clue
