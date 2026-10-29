# Capability: procedencia

## ADDED Requirements

### Requirement: el_lock_de_factory_viaja_con_el_repositorio
Tipo: funcional
El sistema DEBE tener versionado en Git, y no ignorado, el uv.lock de Factory, con cada dependencia fijada con su índice de origen y los hashes SHA-256 de sus archivos.

#### Scenario: el lock está en Git
- DADO el repositorio de Factory
- CUANDO se consulta si Git ignora uv.lock y si lo rastrea
- ENTONCES no lo ignora y lo rastrea

#### Scenario: origen y hashes de cada dependencia
- DADO el uv.lock versionado
- CUANDO se lee cada dependencia que no es el propio proyecto
- ENTONCES tiene un índice de origen declarado y al menos un hash SHA-256

### Requirement: el_lock_de_factory_coincide_con_su_pyproject
Tipo: funcional
El sistema DEBE hacer fallar una prueba cuando el uv.lock versionado no coincide con el pyproject.toml de Factory, de modo que cambiar la versión o una dependencia sin regenerar el lock se detecte.

#### Scenario: el lock coincide
- DADO el uv.lock y el pyproject.toml versionados de Factory
- CUANDO se arma el inventario de procedencia sin consultar ningún entorno
- ENTONCES es confiable y no tiene diferencias

#### Scenario: la versión del proyecto cambió sin regenerar el lock
- DADO una copia del lock y del pyproject.toml con otra versión del proyecto en el pyproject.toml
- CUANDO se arma el inventario
- ENTONCES se declara no confiable y nombra las dos versiones

#### Scenario: una dependencia cambió sin regenerar el lock
- DADO una copia del lock y del pyproject.toml con una dependencia fijada a otra versión en el pyproject.toml
- CUANDO se arma el inventario
- ENTONCES se declara no confiable y nombra la versión exigida y la del lock

### Requirement: un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario
Tipo: funcional
El sistema DEBE marcar como no instalado, sin declarar no confiable el inventario, un paquete que está en el lock y no está instalado en el entorno consultado, y DEBE seguir declarando no confiable una versión instalada distinta de la del lock.

#### Scenario: un paquete del lock que el entorno no instala
- DADO un lock con un paquete que el entorno consultado no tiene instalado, por ejemplo por la versión de Python
- CUANDO se arma el inventario
- ENTONCES ese componente lleva la marca de no instalado y el inventario sigue siendo confiable

#### Scenario: un paquete instalado en otra versión
- DADO un paquete instalado en una versión distinta de la que fija el lock
- CUANDO se arma el inventario
- ENTONCES se declara no confiable y nombra las dos versiones

#### Scenario: un paquete instalado como el lock
- DADO un paquete instalado en la versión que fija el lock
- CUANDO se arma el inventario
- ENTONCES su componente lleva la marca de instalado
