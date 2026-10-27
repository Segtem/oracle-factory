# Design

`oracle_factory/tablero.py` (`armar`) agrega `yo` (misma lectura de `git config user.name` que usa el trailer en `cli.py`, sin escribir nada) y `proyecto.actividad` a partir de los eventos que ya arma para cada cambio abierto. El esquema sigue en `oracle-factory.tablero/1`: sólo se suman campos. `editores/vscode/tablero.js` recibe `yo` en los datos y rotula el paso; la sección de actividad se arma allí, con el mismo escapado.
