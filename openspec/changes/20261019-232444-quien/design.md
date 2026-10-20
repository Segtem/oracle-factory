# Design

- Eventos nuevos en el registro del cambio: `tomado` (persona, `con`: agentes declarados, `relevo_de` si corresponde),
  `soltado`, y `agente_sumado` (un agente que corre `tomar` con `--agente`). Se decide con el actor de siempre
  (`actor()`): una persona es quien tiene la terminal; sin terminal ni `--agente` no se puede tomar.
- `quien(estado, ahora)` arma `{responsable, desde, agentes: [{nombre, declarado, ultima_accion, cuando}], revisores_en_curso, ultima_actividad}`
  sólo de los eventos: agentes declarados en `tomado`/`agente_sumado` más los que tienen eventos en las últimas 24 h;
  los revisores en curso salen de `aviso_lanzamientos`.
- `datos_estado` suma `quien`; `mostrar` imprime una línea «Responsable: …; agentes: …». El tablero lo muestra en cada
  cambio y arma «quién está en qué» del proyecto agrupando los cambios abiertos por responsable.
- Tests con Git: un ayudante común fija `GIT_CEILING_DIRECTORIES` al padre del temporal y comprueba
  `git rev-parse --show-toplevel` antes de operar.
