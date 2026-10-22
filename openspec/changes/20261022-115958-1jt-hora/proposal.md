# La hora de cada evento con microsegundos: lo de dos ramas en el mismo segundo queda en orden

## Why

El banco de concurrencia encontró un límite de Factory: la hora de cada evento del registro (`cuando`) se guarda en
segundos. Lo que dos personas o sus agentes escriben en el mismo segundo, en dos ramas, no tiene un orden que Factory
pueda saber; al unir las ramas queda primero lo de la rama que integra, aunque se haya escrito después. Con agentes que
trabajan rápido, eso pasa. Hoy el banco lo esquiva separando los días un segundo.

## What changes

- `cuando` lleva microsegundos (`2026-10-22T11:59:58.123456+00:00`), en los eventos y en cada decisión que guarda su hora.
- Los registros viejos, con la hora en segundos, se siguen leyendo, mostrando y uniendo como hasta ahora; nada se migra.
- Al unir dos ramas, los eventos del mismo segundo quedan en el orden en que se escribieron.
- El banco deja de separar los días: los mensajes de a turnos escritos el mismo segundo tienen que quedar en orden.

## Out of scope

- Relojes desincronizados entre máquinas: el orden es el de la hora de cada máquina.
- Reescribir la hora de los registros que ya existen.

## Human decisions

- Ninguna más allá de aprobar la spec.
