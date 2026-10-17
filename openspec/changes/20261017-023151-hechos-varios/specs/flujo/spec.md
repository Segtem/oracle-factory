# Capability: flujo

## ADDED Requirements

### Requirement: juzgar acepta los hechos de varios sensores
Tipo: funcional
`juzgar` SHALL aceptar `--con` repetido, un archivo de hechos por sensor, y SHALL juzgar con todos a la vez. El registro SHALL guardar cada archivo con su huella; si cualquiera cambia, falta o no es una ruta, el juicio SHALL dejar de valer, `estado` SHALL nombrar ese archivo y el próximo paso SHALL repetir el juicio con los mismos archivos. `donde` SHALL listarlos todos. Con un solo `--con` o sin él, el registro SHALL ser el de siempre.

#### Scenario: un candidato integrado con dos sensores
- GIVEN un cambio revisado cuyo candidato tiene los hechos de dos frentes en dos archivos, con relaciones distintas
- WHEN se juzga con --con en cada archivo
- THEN Oracle juzga los dos juntos, el veredicto es verde y el registro guarda los dos archivos con su huella; donde los lista

#### Scenario: uno de los archivos cambia después del juicio
- GIVEN un juicio verde con dos archivos de hechos
- WHEN cambia el segundo archivo
- THEN el juicio deja de valer, estado nombra ese archivo y el próximo paso es juzgar otra vez con los dos --con

### Requirement: dos sensores no emiten la misma relación
Tipo: funcional
Si dos archivos de hechos traen la misma relación, `juzgar` SHALL NOT registrar un veredicto y SHALL mostrar el error de Oracle, que nombra la relación y los dos archivos.

#### Scenario: dos frentes que emiten la misma relación
- GIVEN un cambio revisado y dos archivos de hechos que traen la misma relación
- WHEN se juzga con los dos
- THEN juzgar falla con el error de Oracle, que nombra la relación y los dos archivos, y el registro no guarda veredicto
