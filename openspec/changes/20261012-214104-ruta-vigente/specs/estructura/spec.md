# Capability: estructura

## MODIFIED Requirements

### Requirement: ruta canonica para producir artefactos
Tipo: funcional
`oracle-factory ruta ID TIPO` SHALL imprimir la ruta canónica para producir un artefacto de ese tipo (evidencia, clue, revision o checkout) sobre el candidato vigente del cambio —el commit con carpeta de candidato más cercano a HEAD, si el producto no cambió desde él— o sobre HEAD si no hay candidato vigente, nombrando la carpeta del candidato con los 7 primeros caracteres del hash completo del commit, sin crear ni modificar archivos.

#### Scenario: sensor que escribe su evidencia
- GIVEN un cambio abierto y un HEAD sin candidato vigente
- WHEN se usa ruta con el tipo evidencia como salida del sensor
- THEN la ruta es `.factory/cambios/<ID>/candidatos/<sha7 de HEAD>/evidencia` y donde la encuentra

#### Scenario: un commit que sólo guarda registros
- GIVEN un candidato con carpeta propia y, después, un commit que sólo agrega informes o evidencia del cambio
- WHEN se usa ruta con el tipo evidencia
- THEN la ruta es la carpeta del candidato anterior, no la de HEAD, y no se crea ninguna carpeta

#### Scenario: un commit que cambia el producto
- GIVEN un candidato con carpeta propia y, después, un commit que cambia el producto
- WHEN se usa ruta con el tipo evidencia
- THEN la ruta es la de HEAD

#### Scenario: checkout de revisión
- GIVEN un HEAD
- WHEN se usa ruta con el tipo checkout
- THEN imprime `.factory/local/revisiones/<sha7>` del mismo candidato y no crea nada

#### Scenario: tipo desconocido
- GIVEN un tipo que no está en la estructura
- WHEN se ejecuta ruta
- THEN Factory lo rechaza nombrando los tipos válidos
