# Design

- `liveshare.js` suma `compartir()` (`api.share()`), `unirse(enlace)` (`api.join(Uri.parse(enlace))`) y `terminar()`
  (`api.end()`). Sin la API, `instalar()` abre la extensión con el comando `extension.open` y su id.
- `tablero.js` muestra los botones según `sesion.estado` y `rol`, con `data-sesion="compartir|unirse|terminar|instalar"`;
  el panel manda `{tipo: 'sesion', accion}`. Para unirse, la extensión pide el enlace con `showInputBox` y sólo acepta
  un enlace https de Live Share (`prod.liveshare.vsengsaas.visualstudio.com` o `vscode.dev/liveshare`).
- El enlace: `api.share()` lo devuelve al empezar; la extensión lo guarda para mostrarlo y lo copia con
  `vscode.env.clipboard.writeText`. No se le vuelve a pedir a Live Share: llamar a `share()` con una sesión abierta
  intenta empezar otra y la deja a medias (probado por Brian). Una sesión empezada desde la paleta no tiene enlace en el
  tablero: dice que lo copió Live Share al compartir.
