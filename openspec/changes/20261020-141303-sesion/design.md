# Design

- `liveshare.js` suma `compartir()` (`api.share()`), `unirse(enlace)` (`api.join(Uri.parse(enlace))`) y `terminar()`
  (`api.end()`). Sin la API, `instalar()` abre la extensión con el comando `extension.open` y su id.
- `tablero.js` muestra los botones según `sesion.estado` y `rol`, con `data-sesion="compartir|unirse|terminar|instalar"`;
  el panel manda `{tipo: 'sesion', accion}`. Para unirse, la extensión pide el enlace con `showInputBox` y sólo acepta
  un enlace https de Live Share (`prod.liveshare.vsengsaas.visualstudio.com` o `vscode.dev/liveshare`).
- El enlace: `api.share()` lo devuelve al empezar y, si ya se compartió, lo vuelve a dar (con `suppressNotification`
  para no repetir el aviso). La extensión lo guarda para mostrarlo y lo copia con `vscode.env.clipboard.writeText`.
