# Capability: trazabilidad

## ADDED Requirements

### Requirement: cada commit nuevo dice de qué cambio es
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
