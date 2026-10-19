# Capability: trazabilidad

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: el sensor registra qué líneas ejecuta cada caso
Origen: 20261013-180751-trazabilidad · trazabilidad_cca95191eb0039b11.el_sensor_registra_que_lineas_ejecuta_cada_caso
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
Origen: 20261013-180751-trazabilidad · trazabilidad_cca95191eb0039b11.trazabilidad_cruza_los_casos_con_el_diff_del_candidato
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
Origen: 20261013-180751-trazabilidad · trazabilidad_cca95191eb0039b11.los_limites_de_la_trazabilidad_se_declaran
Tipo: funcional
La salida de `trazabilidad`, en texto y en JSON, SHALL declarar que ejecutar una línea no prueba que sea correcta y que el código que corre en otro proceso no se traza.

#### Scenario: límites a la vista
- WHEN se pide trazabilidad, en texto o con --json
- THEN la salida incluye los dos límites

### Requirement: cada commit nuevo dice de qué cambio es
Origen: 20261019-182313-commits · trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es
Tipo: funcional
`oracle-factory init` y `oracle-factory hooks` SHALL instalar un hook `prepare-commit-msg` que agregue el trailer `Cambio: <ID>` a cada commit hecho en un checkout con exactamente un cambio abierto, sin tocar los otros trailers ni un `Cambio:` que ya esté; con cero o más de un cambio abierto SHALL NOT agregar nada. Si en la carpeta de hooks ya hay un `prepare-commit-msg` ajeno, SHALL NOT pisarlo y SHALL decir cómo encadenarlo. El hook SHALL NOT impedir un commit, tampoco si falta el intérprete de Factory.

#### Scenario: un commit con un cambio abierto
- GIVEN un proyecto con el hook instalado y un solo cambio abierto
- WHEN se hace un commit con `git commit` y un trailer Co-Authored-By
- THEN el mensaje termina con `Cambio: <ID>` junto al Co-Authored-By

#### Scenario: sin un único cambio abierto, o con un hook ajeno
- GIVEN un proyecto sin cambios abiertos, o con dos, o con un prepare-commit-msg que no es de Factory
- WHEN se hace un commit, o se pide oracle-factory hooks
- THEN el commit no lleva trailer, y el hook ajeno queda igual con un aviso de cómo encadenarlo

### Requirement: los commits de un cambio se ven en log, estado y el tablero
Origen: 20261019-182313-commits · trazabilidad_c03c40840efaaab69.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero
Tipo: funcional
`oracle-factory log ID` (y `--json`) SHALL listar los commits del cambio con sha, autor, fecha y asunto, cada uno con cómo se lo unió (trailer o deducido) y si fue candidato revisado o con evidencia: los que llevan su trailer y, para los anteriores al trailer, los deducidos de sus candidatos registrados y del merge que los integró. `estado` SHALL mostrar cuántos commits tiene y el último, y `estado --json` SHALL traerlos. El tablero SHALL mostrarlos por cambio y elegir uno SHALL abrir su diff en VS Code sin modificar nada.

#### Scenario: un cambio cerrado de antes del trailer
- GIVEN un cambio cerrado sin trailers cuyos candidatos se integraron con un merge
- WHEN se pide oracle-factory log ID --json
- THEN están los commits de la rama integrada, marcados como deducidos, y sus candidatos revisados marcados

#### Scenario: un cambio abierto con trailer, en estado y en el tablero
- GIVEN un cambio abierto con commits que llevan su trailer
- WHEN se pide oracle-factory estado ID, se abre el tablero y se elige un commit
- THEN estado dice cuántos commits tiene y el último, el tablero los lista y se abre el diff de ese commit
