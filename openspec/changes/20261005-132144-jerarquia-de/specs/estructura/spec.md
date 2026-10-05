# Capability: estructura

## ADDED Requirements

### Requirement: estructura documentada
Tipo: funcional
La documentación SHALL describir dónde va cada artefacto de un proyecto Factory: la raíz, el acuerdo y los registros en `openspec/changes/<ID>/`, el trabajo en `tareas/<ID>/` con una carpeta por candidato, y los checkouts de revisión fuera del repositorio, en la carpeta que indica `raiz_revisiones` del `factory.json` del proyecto (por defecto `~/Dev/_revisiones`). La carpeta de cada candidato se llama como el SHA de 7 caracteres de su commit.

#### Scenario: raíz de revisiones configurada
- GIVEN un `factory.json` con `raiz_revisiones` apuntando a otra carpeta
- WHEN se consulta la documentación o se usa ruta con el tipo clue
- THEN la raíz es la configurada y no la de por defecto

#### Scenario: una persona busca la evidencia de un candidato
- GIVEN un cambio con evidencia producida sobre un commit
- WHEN la persona consulta la documentación de estructura
- THEN sabe en qué carpeta está esa evidencia sin conocer la historia del cambio

### Requirement: donde esta cada artefacto
Tipo: funcional
`oracle-factory donde ID` SHALL listar cada artefacto del cambio con su ruta, si existe y qué gate respalda; con `--candidato SHA` SHALL limitarse a ese candidato y SHALL marcar como históricos los artefactos con nombres anteriores a esta estructura.

#### Scenario: cambio con revisión registrada
- GIVEN un cambio con spec aceptada, evidencia y una revisión registrada
- WHEN se ejecuta donde con su ID
- THEN aparecen la propuesta, la spec, los requisitos, la evidencia y el informe de revisión, cada uno con su gate y su ruta

#### Scenario: artefacto ausente
- GIVEN un registro de Factory que referencia un informe que ya no existe
- WHEN se ejecuta donde
- THEN el artefacto aparece marcado como ausente, sin ocultarlo

#### Scenario: cambio anterior a la estructura
- GIVEN un cambio con carpetas como evidencia-mapeo o revision-pendiente
- WHEN se ejecuta donde
- THEN esos artefactos aparecen como históricos y no se mueven

### Requirement: ruta canonica para producir artefactos
Tipo: funcional
`oracle-factory ruta ID TIPO` SHALL imprimir la ruta canónica para producir un artefacto de ese tipo (evidencia, clue, revision) sobre el HEAD actual, sin crear ni modificar archivos.

#### Scenario: sensor que escribe su evidencia
- GIVEN un cambio abierto y un HEAD
- WHEN se usa ruta con el tipo evidencia como salida del sensor
- THEN la evidencia queda en la carpeta del candidato de ese HEAD y donde la encuentra

#### Scenario: tipo desconocido
- GIVEN un tipo que no está en la estructura
- WHEN se ejecuta ruta
- THEN Factory lo rechaza nombrando los tipos válidos

### Requirement: buscar en todo el proyecto
Tipo: funcional
`oracle-factory buscar TEXTO` SHALL buscar en propuestas, specs, requisitos, tareas y registros de Factory, y SHALL mostrar por resultado la ruta, la línea y el cambio al que pertenece.

#### Scenario: texto presente en varios cambios
- GIVEN un texto que aparece en la spec de un cambio y en la tarea de otro
- WHEN se busca
- THEN aparecen los dos resultados, cada uno con su cambio, ruta y línea

### Requirement: listar con filtros
Tipo: funcional
`oracle-factory listar` SHALL aceptar filtros por fase y por estado abierto o cerrado, sin cambiar su salida cuando no se usan filtros.

#### Scenario: cambios abiertos
- GIVEN cambios abiertos y cerrados
- WHEN se lista con el filtro de abiertos
- THEN sólo aparecen los abiertos

### Requirement: respetar lo existente
Tipo: no funcional
Factory SHALL NOT mover, renombrar ni borrar artefactos existentes al adoptar la estructura, y los comandos de esta capacidad SHALL ser de sólo lectura salvo que se diga lo contrario.

#### Scenario: proyecto con cambios anteriores
- GIVEN un proyecto con cambios creados antes de la estructura
- WHEN se usan donde, ruta, buscar y listar
- THEN ningún archivo del proyecto cambia
