# Capability: ide

## ADDED Requirements

### Requirement: el tablero junta todo lo de cada cambio y sus métricas
Tipo: funcional
`oracle-factory tablero --json` SHALL devolver un esquema versionado con, por cada cambio abierto, la decisión que espera de la persona y su comando, la línea de tiempo de sus eventos (qué, quién, de qué tipo y cuándo), los hallazgos de los revisores del candidato vigente con archivo, línea, severidad, revisor y lo que se decidió, sus requisitos con medidas y los archivos que los definen, sus avisos y sus métricas; y SHALL devolver las métricas del proyecto. Las métricas SHALL contarse del registro: tiempo en cada fase y hasta el cierre, vueltas de revisión, hallazgos por severidad y por revisor, riesgos aceptados, decisiones de persona y de agente, requisitos medidos y cumplidos; y del proyecto, cambios por estado, mediana de tiempo hasta el cierre, proporción de cambios cerrados en la primera vuelta y hallazgos por revisor.

#### Scenario: un cambio con revisión y hallazgos
- GIVEN un proyecto con un cambio cerrado y otro abierto cuyo candidato tiene informes de dos revisores con hallazgos
- WHEN se pide oracle-factory tablero --json
- THEN el abierto trae su próxima decisión con el comando, su línea de tiempo en orden, cada hallazgo con archivo, línea, severidad y revisor, y sus métricas; y las del proyecto cuentan los dos cambios

#### Scenario: un proyecto sin cambios
- GIVEN un proyecto recién inicializado
- WHEN se pide oracle-factory tablero --json
- THEN devuelve el esquema sin cambios y métricas en cero, sin fallar

### Requirement: el tablero se ve y se usa en VS Code
Tipo: funcional
La extensión de VS Code SHALL tener un panel «Tablero de Factory» que muestre ese JSON: primero lo que necesita una decisión de la persona, con un botón que escribe el comando en una terminal del proyecto sin ejecutarlo; la línea de tiempo; los hallazgos, que al elegirlos SHALL abrir su archivo en su línea; los requisitos, que SHALL abrir su `.requisito` y el catálogo de cada medida; los avisos y las métricas. SHALL funcionar sin red, SHALL actualizarse cuando cambia el registro de un cambio y SHALL NOT tomar decisiones.

#### Scenario: abrir el tablero y seguir un hallazgo
- GIVEN el proyecto del escenario anterior abierto en VS Code
- WHEN se abre el tablero y se elige un hallazgo, un requisito y el botón del próximo paso
- THEN se abre el archivo del hallazgo en su línea, el .requisito y el catálogo de sus medidas, y la terminal recibe el comando sin Enter

#### Scenario: un registro que cambia
- GIVEN el tablero abierto
- WHEN cambia el factory.json de un cambio
- THEN el tablero se vuelve a armar con el registro nuevo
