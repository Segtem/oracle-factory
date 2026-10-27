# Design

La clasificación vive en `oracle_factory/tablero.py` (`_faltan`, `_paso`): una tabla corta de patrones sobre el texto de `pendientes` y una de verbos para la frase del paso. Se mantiene el texto de `pendientes` y `proximo_paso`, porque la CLI, el MCP y varias pruebas lo leen; el tablero suma `faltan` y `humano` sin cambiar el esquema (`oracle-factory.tablero/1`, sólo campos nuevos). `editores/vscode/tablero.js` usa `faltan` y, si falta (el JSON de un host con una versión anterior), cae a `pendientes` como hoy.
