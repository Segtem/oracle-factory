# Capability: trazabilidad

## ADDED Requirements

### Requirement: el sensor registra qué líneas ejecuta cada caso
Tipo: funcional
`oracle_factory.trazabilidad` SHALL correr los casos que un sensor asigna a cada requisito con una traza de líneas de la biblioteca estándar y SHALL escribir `trazabilidad.json` con `esquema` `oracle-factory.trazabilidad-casos/1`, cada requisito con sus casos y cada caso con su resultado y las líneas que ejecutó de archivos del proyecto (rutas relativas, sin el entorno virtual). Un caso que falla SHALL quedar registrado con su resultado, sin cortar la traza de los demás.

#### Scenario: dos requisitos con sus casos
- GIVEN un proyecto con dos requisitos y un caso de prueba para cada uno, que ejecutan funciones distintas
- WHEN el sensor traza los casos
- THEN trazabilidad.json asigna a cada caso las líneas de su función y no las de la otra

#### Scenario: un caso que falla
- GIVEN un caso que falla
- WHEN el sensor traza los casos
- THEN el caso queda con resultado de falla y los demás casos quedan trazados

### Requirement: trazabilidad cruza los casos con el diff del candidato
Tipo: funcional
`oracle-factory trazabilidad ID` SHALL leer `trazabilidad.json` de la evidencia del candidato vigente y cruzarlo con las líneas que el candidato cambió respecto de su base: por requisito, las líneas cambiadas que ejecutan sus casos; las líneas cambiadas ejecutables que no ejecuta ningún caso, como sin respaldo; y los archivos cambiados que la traza no puede ver. Las líneas que no son ejecutables (comentarios, en blanco) SHALL NOT figurar sin respaldo. Con `--json` SHALL imprimir un objeto con `esquema` `oracle-factory.trazabilidad/1`, el candidato y la base. Sin trazabilidad.json en la evidencia SHALL fallar diciendo dónde va y cómo generarla.

#### Scenario: una línea cambiada sin respaldo
- GIVEN un candidato que cambia una función que prueba un caso y otra que no prueba ninguno, más un comentario y un archivo que no es Python
- WHEN se pide trazabilidad
- THEN la primera figura bajo su requisito, la segunda como sin respaldo, el comentario en ninguna de las dos y el archivo como no rastreable

#### Scenario: sin trazabilidad en la evidencia
- GIVEN un candidato con evidencia pero sin trazabilidad.json
- WHEN se pide trazabilidad
- THEN falla nombrando la ruta esperada, sin escribir nada

### Requirement: los límites de la trazabilidad se declaran
Tipo: funcional
La salida de `trazabilidad`, en texto y en JSON, SHALL declarar que ejecutar una línea no prueba que sea correcta y que el código que corre en otro proceso no se traza.

#### Scenario: límites a la vista
- WHEN se pide trazabilidad, en texto o con --json
- THEN la salida incluye los dos límites
