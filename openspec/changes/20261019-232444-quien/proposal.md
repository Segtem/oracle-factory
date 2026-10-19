# Quién trabaja en qué: tomar un cambio, su persona y sus agentes en estado y en el tablero

## Why

Factory sirve para trabajar solo o en pair programming, con personas que trabajan con sus agentes. Hoy el registro dice
quién hizo cada acción, pero no quién tiene un cambio ahora ni qué agentes trabajan en él: el reparto vive en un
`reparto.md` a mano y en lo que las personas se dicen. Brian lo pidió el 2026-10-19 como primer paso del tablero
colaborativo (después vienen presencia y chat con Live Share).

## What changes

- `oracle-factory tomar ID [--con AGENTE]`: una persona, desde su terminal, se registra como responsable del cambio y
  declara con qué agente trabaja. Si otra persona ya lo tiene, Factory no se lo saca: hace falta `--relevo`, que deja
  constancia de quién lo tenía. `oracle-factory soltar ID` lo libera. Un agente (`--agente`) no puede tomar un cambio
  para sí: se suma como agente que trabaja en él.
- `estado` (y `--json`) y el tablero muestran, por cambio, la persona responsable, los agentes declarados y los que
  actuaron hace poco, los revisores lanzados sin resultado, y la última actividad de cada uno. El tablero suma, para el
  proyecto, quién está en qué.
- Los tests que usan Git no pueden tocar un repositorio que los contenga (lo que pasó el 2026-10-19 con una rama
  `tarea/viejo` creada en el worktree real).

## Out of scope

- Presencia en tiempo real y chat (Live Share): es el cambio siguiente.
- Bloquear a otro proceso: tomar un cambio es un acuerdo registrado, no un candado.

## Human decisions

- Brian eligió el 2026-10-19: empezar por quién trabaja en qué, sin red, antes de Live Share.
- «Hace poco» para la actividad de un agente: las últimas 24 horas (propuesta).
