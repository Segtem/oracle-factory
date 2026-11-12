# Capability: flujo

## ADDED Requirements

### Requirement: migrar_al_almacen_copia_conecta_y_deja_la_baja
Tipo: funcional
El sistema DEBE, con `migrar --almacen ALMACÉN` corrido por una persona desde un producto con sus registros adentro, copiar byte a byte al almacén los archivos versionados de los registros (`.factory/`, `openspec/`, `requisitos/`, `catalogos/`, `tareas/`, `kb/`, `oracle.json` y las demás carpetas del proyecto Oracle que existan), mover al almacén en la misma ruta lo no versionado de esas carpetas, dejar un solo commit en el almacén que nombre el commit de origen del producto, conectar el producto al almacén y borrar los registros del producto dejando la baja en su índice sin commitear; después, Factory desde el producto DEBE ver los mismos cambios que antes.

#### Scenario: un producto con registros adentro
- DADO un producto con registros versionados, un cambio abierto y archivos en `.factory/local/`, y un repo Git vacío como almacén
- CUANDO una persona corre `migrar --almacen` con ese almacén
- ENTONCES el almacén tiene los mismos archivos con el mismo contenido en un commit nuevo, `.factory/local/` está en el almacén, el producto está conectado, sus registros están borrados con la baja sin commitear, y `listar` muestra los mismos cambios

#### Scenario: el almacén por URL
- DADO un repo Git remoto vacío
- CUANDO una persona corre `migrar --almacen` con su URL
- ENTONCES lo clona en la carpeta de datos del usuario, como `conectar`, y migra ahí

### Requirement: migrar_verificar_no_escribe
Tipo: funcional
El sistema DEBE, con `migrar --almacen ALMACÉN --verificar`, decir cuántos archivos versionados copiaría y qué no versionado movería, sin escribir nada en el producto, el almacén ni la configuración del usuario, y salir con error si la migración se negaría.

#### Scenario: verificar antes de migrar
- DADO un producto con registros adentro y un almacén vacío
- CUANDO se corre `migrar --almacen ALMACÉN --verificar`
- ENTONCES dice lo que copiaría y movería, y nada cambia en el disco

### Requirement: migrar_al_almacen_se_niega_sin_tocar_nada
Tipo: funcional
El sistema DEBE negarse a `migrar --almacen`, sin cambiar nada en el producto, el almacén ni la configuración del usuario, si lo corre un agente, si el producto ya está conectado, si los registros del producto tienen cambios sin commitear o archivos sin versionar que no estén ignorados, si el producto tiene el formato anterior a la fase 2, si el almacén no es la raíz de un repo Git, si ya tiene registros de Factory o si almacén y producto están uno dentro del otro.

#### Scenario: cada negativa
- DADO cada una de esas situaciones
- CUANDO se corre `migrar --almacen`
- ENTONCES el comando falla diciendo por qué y el producto, el almacén y la configuración quedan como estaban

### Requirement: el_ensayo_sobre_una_copia
Tipo: funcional
El sistema DEBE ofrecer `tools/ensayar_migracion.py PROYECTO` que migre una copia del proyecto (un clon local de su HEAD en una carpeta temporal, con un almacén temporal y una configuración de usuario temporal) sin tocar el proyecto original ni la configuración del usuario, y escriba un informe JSON con los cambios que lista Factory antes y después, si coinciden, y, con `--pruebas`, el resultado de las pruebas de la copia con los registros afuera.

#### Scenario: ensayar sobre un proyecto chico
- DADO un proyecto con registros adentro
- CUANDO se corre el ensayo
- ENTONCES el informe dice que los cambios antes y después coinciden y el proyecto original y la configuración del usuario no cambiaron
