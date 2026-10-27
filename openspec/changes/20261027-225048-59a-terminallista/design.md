# Design

`editores/vscode/extension.js` (`escribirPaso`) pasa a ser asíncrona: si debe crear la terminal, espera `Promise.race` entre `vscode.window.onDidChangeTerminalShellIntegration` (si existe en esa versión de VS Code) y un temporizador de `factory.esperaTerminalMs`. Las escrituras pendientes de una terminal que arranca comparten la misma espera, así se conserva el orden. Los dobles de `vscode` de las pruebas ganan un evento de integración de shell que el caso dispara a voluntad.
