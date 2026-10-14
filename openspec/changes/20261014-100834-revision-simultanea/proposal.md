# pedir-revision tolera pedidos simultáneos sobre el mismo candidato

## Why

Lanzar a la vez dos revisores (codex y agy) sobre el mismo candidato es lo natural, y hoy choca: los dos pedidos ven que no existe el checkout `.factory/local/revisiones/<sha>`, los dos corren `git worktree add` y uno falla («ya existe», o el lock de git). Además cada pedido numera su paquete contando los `paquete-<revisor>-N.json` que hay, así que dos pedidos del mismo revisor toman el mismo número y se pisan el paquete, la carpeta de trabajo y el informe; y los dos agregan su evento a `factory.json` leyendo y reescribiendo el registro, así que uno puede borrar el del otro. Pasó el 2026-10-13 con cuatro pedidos a la vez y desde entonces cada vuelta se lanza escalonada, a mano.

Tarea de origen: `20261013-115236-revision-simultanea`.

## What changes

- **Los pedidos sobre un mismo cambio se turnan en lo corto**: crear el checkout, numerar y preparar el paquete, y anotar el evento en el registro. El revisor (lo largo) corre sin bloquear a los otros pedidos.
- **El bloqueo se suelta solo**: si un pedido muere (Ctrl+C, corte), el siguiente no queda trabado ni hay que borrar nada a mano.

## Out of scope

- Otras operaciones que escriben el registro a la vez que un pedido (`revisar`, `medir`, `cerrar`): las decide una persona desde su terminal, de a una.
- Windows: el bloqueo usa `fcntl.flock`, como el resto del flujo supone un sistema POSIX.

## Human decisions

- Ninguna: el comportamiento esperado es el que hoy se logra escalonando a mano.
