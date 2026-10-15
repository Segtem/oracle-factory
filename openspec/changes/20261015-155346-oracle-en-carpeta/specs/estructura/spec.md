# Capability: estructura

## ADDED Requirements

### Requirement: el proyecto Oracle puede estar en una carpeta
Tipo: funcional
Con `"oracle": "CARPETA"` en `.factory/config.json`, Factory SHALL usar esa carpeta como proyecto Oracle: importar los requisitos en `CARPETA/requisitos/`, medirlos, juzgarlos y quitarlos al abandonar desde ahí, y correr Oracle con ese proyecto; `donde` y `buscar` SHALL nombrar los requisitos en esa carpeta. Sin la clave, el proyecto Oracle SHALL seguir siendo la raíz. Una carpeta absoluta, que sale del proyecto o sin `oracle.json` SHALL rechazarse con la causa.

#### Scenario: un proyecto con su Oracle en medidas/
- GIVEN un proyecto Factory con el proyecto Oracle en medidas/ y "oracle": "medidas" en la configuración
- WHEN se crea un cambio, se aprueba, se importa, se miden sus requisitos y se juzga
- THEN los requisitos quedan en medidas/requisitos/, no en la raíz, el juicio usa los catálogos de medidas/, y donde los nombra en medidas/

#### Scenario: sin la clave, todo sigue en la raíz
- GIVEN un proyecto sin la clave oracle en la configuración
- WHEN se importa y se juzga un cambio
- THEN los requisitos y los catálogos son los de la raíz, como antes

#### Scenario: una carpeta inválida
- GIVEN una configuración con oracle absoluta, con .. que sale del proyecto, o en una carpeta sin oracle.json
- WHEN se corre un comando de Factory
- THEN falla diciendo cuál es el problema y no escribe nada

### Requirement: init adopta un proyecto Oracle existente
Tipo: funcional
`oracle-factory init --oracle CARPETA` SHALL inicializar Factory sobre un proyecto Oracle que ya está en esa carpeta: SHALL guardar la carpeta en la configuración y SHALL NOT crear `oracle.json`, `requisitos/` ni catálogos en la raíz; las tareas que ya existen en `tareas/` SHALL quedar como están.

#### Scenario: un repositorio con medidas/ y tareas/
- GIVEN un repositorio Git con medidas/oracle.json, requisitos y catálogos, y un tareas/ con tareas
- WHEN se corre oracle-factory init --oracle medidas
- THEN aparece .factory/ con "oracle": "medidas", la raíz no tiene oracle.json ni catálogos nuevos, y las tareas siguen iguales

### Requirement: los escalares del proyecto se ejecutan sólo si el proyecto lo declara
Tipo: funcional
Con `"confiar_escalares": true` en la configuración, Factory SHALL correr Oracle con `--confiar-escalares` al evaluar medidas; sin esa clave SHALL NOT pasarlo. Un valor que no sea true o false SHALL rechazarse.

#### Scenario: un proyecto con escalares.py
- GIVEN un proyecto Oracle con escalares.py y una medida que lo usa, y "confiar_escalares": true
- WHEN se juzga un cambio medido con esa medida
- THEN Oracle lo evalúa con los escalares del proyecto

#### Scenario: sin declararlo
- GIVEN el mismo proyecto sin la clave confiar_escalares
- WHEN se juzga
- THEN Factory no pasa --confiar-escalares y el error de Oracle llega a la persona
