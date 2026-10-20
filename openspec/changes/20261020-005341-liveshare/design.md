# Design

- La extensión no suma dependencias: toma la API de Live Share con `vscode.extensions.getExtension('ms-vsliveshare.vsliveshare')`
  y `getApi(versión)`, como hace el paquete `vsls`. Sin la extensión, o si devuelve null, todo sigue como hoy.
- Presencia: `api.session` (rol, nombre) y `api.peers` (nombre, rol), con `onDidChangeSession` y `onDidChangePeers`, se
  pasan a `tablero.html` como `sesion`. Todo nombre se escapa.
- Anfitrión: `shareService('oracle-factory')` con pedidos `tablero` (el JSON de `oracle-factory tablero --json`),
  `terminal` (comando a escribir sin Enter, con la misma validación que el panel local) y `mensaje` (lo guarda con la CLI
  y lo reparte). Avisos a los invitados: `cambio` (se rehizo el tablero) y `mensaje`.
- Invitado: `getSharedService('oracle-factory')`; pide el tablero al abrir y al recibir `cambio`; los enlaces abren
  `Uri.joinPath(carpeta del espacio compartido, archivo)`.
- CLI: `mensaje ID TEXTO [--de NOMBRE]`. Sin `--de`, el autor es el actor de siempre (persona con terminal o agente);
  `--de` lo usa la extensión del anfitrión para un mensaje que llegó por Live Share: el evento dice `de` y `via: live-share`
  (Factory no autentica a nadie; Live Share sí). Evento `mensaje` con `forma: "mensaje"`: no cuenta como decisión.
- Pruebas: el panel en node con un `vscode` falso que trae una extensión de Live Share falsa (anfitrión e invitado
  conectados en memoria).
