# Design

- `editores/vscode/modelo.js` es puro (sin `vscode`): recibe la salida JSON de la CLI y devuelve los nodos del árbol (etiqueta, descripción, ícono, archivo a abrir, comando a ofrecer). Se prueba con `node` sobre la salida real de proyectos temporales de Factory.
- `editores/vscode/extension.js` es el pegamento con la API de VS Code: un `TreeDataProvider` que corre la CLI (`execFile`, sin shell) y le pasa el JSON a `modelo.js`; abrir un archivo es `vscode.open`; el próximo paso es `terminal.sendText(comando, false)` (sin Enter).
- La CLI se elige así: la configuración `factory.comando`, si no `.venv/bin/oracle-factory` del proyecto, si no `oracle-factory` del `PATH`.
- Un comando que trae algo por completar (MAYÚSCULAS, como `--a NOMBRE`) se escribe igual, para que la persona lo complete; un paso que no es un comando (por ejemplo «corregí … y commitealo») no tiene botón, sólo se muestra.
