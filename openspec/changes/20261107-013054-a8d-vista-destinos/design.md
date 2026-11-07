# Diseño

- `extension.js` (`datosLocales`) agrega al JSON del tablero la clave `destinos`: la salida de `destinos --json --sin-consultar` (o con consulta, una vez, si se apretó «Consultar ahora»), o `null` más `destinos_error` con el motivo si el proyecto no tiene `.factory/destinos.json` o la declaración es inválida. Así un invitado de Live Share, que pide `tablero` a quien comparte, recibe lo mismo sin servicio nuevo.
- `tablero.js` dibuja la sección con una función pura `destinos(d, error, sesion)`; todo texto se escapa. Los botones usan el mecanismo `data-comando` que ya existe (escribe en la terminal sin Enter); el de consultar es un mensaje nuevo `consultar-destinos` que sólo el anfitrión (o quien no está en una sesión) tiene.
- `tools/contrato_vscode.py`: `tablero.js` pasa a leer `("tablero", "destinos")`; `destinos_error` es un nombre propio de la extensión. `contrato.json` declara las claves de `destinos --json`.
- Sin consultar, `desactualizado` es «desconocido» salvo que haya registro; la vista lo dice con todas las letras en vez de mostrarlo «al día».
