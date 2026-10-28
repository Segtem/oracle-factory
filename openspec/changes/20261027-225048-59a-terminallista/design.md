# Design

`editores/vscode/extension.js` (`escribirPaso`) pasa a ser asíncrona: si debe crear la terminal, espera `Promise.race` entre `vscode.window.onDidChangeTerminalShellIntegration` (si existe en esa versión de VS Code) y un temporizador de `factory.esperaTerminalMs`. Las escrituras pendientes de una terminal que arranca comparten la misma espera, así se conserva el orden. Los dobles de `vscode` de las pruebas ganan un evento de integración de shell que el caso dispara a voluntad.

Si la terminal se cierra mientras arranca (evento `onDidCloseTerminal` o `exitStatus` definido), el comando no se escribe en ella: se abre otra una vez y, si también se cierra, el pedido falla en voz alta. `escribirComando` devuelve a quien pide (un invitado de Live Share, el tablero) verdadero si se escribió y falso si no se pudo, dejando el motivo en la salida; un error de un pedido no traba la cola de los siguientes.
