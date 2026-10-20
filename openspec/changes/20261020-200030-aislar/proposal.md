# El checkout de un revisor no toca el repositorio: un clon aparte en vez de un worktree

## Why

`pedir-revision` le arma a cada revisor un checkout del candidato con `git worktree add`. Un worktree comparte con el
repositorio su configuración y sus ramas, así que lo que un revisor hace con git ahí le cae al repositorio real. Pasó dos
veces: el 2026-10-19 una rama `tarea/viejo` apareció en el worktree de un cambio y los commits siguientes fueron a parar
ahí; el 2026-10-20 un revisor probó un nombre raro con `git config user.name` en su checkout, quedó en
`.git/config` del repositorio, y siete commits y una revisión de Brian se registraron con ese nombre.

## What changes

- El checkout de revisión es un clon local aparte (`git clone --local`: en el mismo disco enlaza los objetos, sin copiarlos, y no depende de ellos) en el commit del candidato:
  su configuración, sus ramas y sus hooks son suyos. Lo que un revisor haga con git ahí no cambia el repositorio.
- Cada pedido tiene su propio clon (`.factory/local/revisiones/<sha>-<revisor>-<n>`): dos revisores no comparten checkout,
  y un checkout viejo (un worktree de antes) ya no se usa. El clon no tiene remoto, y antes de validar el informe vuelve
  al commit del candidato.

## Out of scope

- Aislar al revisor del resto del disco: eso es cosa del sandbox de cada revisor.

## Human decisions

- Brian eligió el 2026-10-20 hacerlo antes de seguir revisando.
