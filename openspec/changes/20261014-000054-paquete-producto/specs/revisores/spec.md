# Capability: revisores

## ADDED Requirements

### Requirement: el paquete de revisión excluye lo que no es producto
Tipo: funcional
`pedir-revision` SHALL preparar el paquete de Clue excluyendo `.factory/`, `tareas/` y todo otro archivo del diff que no cuente en la huella del producto. El paquete SHALL nombrar esas exclusiones y los archivos que dejaron afuera, y el pedido al revisor SHALL decir que no forman parte de lo revisado.

#### Scenario: un candidato con registros de vueltas anteriores
- GIVEN un candidato cuyo diff contra la base trae un cambio de producto, informes y evidencia en .factory/ y una nota en tareas/
- WHEN se pide una revisión
- THEN el paquete contiene sólo el archivo de producto, nombra .factory y tareas como exclusiones con sus archivos, y el pedido lo dice

#### Scenario: un registro fuera de esas carpetas
- GIVEN un candidato que además cambia un archivo que no es producto fuera de .factory/ y tareas/
- WHEN se pide una revisión
- THEN ese archivo también queda excluido

### Requirement: Factory comprueba las exclusiones del paquete
Tipo: funcional
Un paquete cuyas exclusiones dejan afuera un archivo del producto SHALL NOT usarse: `pedir-revision` SHALL fallar sin guardar el informe, y la preparación de la revisión SHALL no usar el informe de ese paquete y avisar por qué. Los paquetes sin exclusiones de vueltas anteriores SHALL seguir usándose.

#### Scenario: un paquete que excluye producto
- GIVEN un informe guardado cuyo paquete excluye un archivo del producto
- WHEN se prepara la revisión
- THEN ese informe no se usa y el aviso nombra el archivo

#### Scenario: un paquete anterior sin exclusiones
- GIVEN un informe guardado con un paquete preparado sin exclusiones
- WHEN se prepara la revisión con oracle-clue 0.1.0a2
- THEN el informe se usa como antes
