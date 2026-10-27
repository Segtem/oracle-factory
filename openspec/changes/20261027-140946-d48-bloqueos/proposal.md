# Mostrar en el tablero qué falta en cada cambio y cómo se destraba

## Why

En el piloto, Brian abrió el tablero y no entendió qué hacer: el próximo paso se mostraba siempre como código aunque fuera una explicación («falta un revisor independiente: declaralo en .factory/config.json…»), sin botón, y la lista de lo que falta para cerrar (`pendientes`) sólo se veía en un tooltip del árbol. Dijo: «esto tenemos que dejarlo en el hud del tablero, las soluciones a los bloqueos». El cambio `bloqueos` arregló los mensajes de la CLI; falta que el tablero los muestre como corresponde.

## What changes

- Cada cambio abierto muestra una lista «Qué falta» con sus pendientes, en el orden en que `estado` los informa, debajo del próximo paso.
- El próximo paso (y cada alternativa) que es un comando de Factory se sigue mostrando como comando con su botón «Escribir en la terminal». El que es una explicación se muestra como texto, rotulado «QUÉ HACER», sin botón ni formato de código.
- Un cambio sin pendientes lo dice («Nada falta: …»), en vez de callar.

## Out of scope

- Rediseño general del tablero, vista de varias personas y el `^C` del botón (cambios aparte).
- Cambiar qué pendientes calcula Factory o qué texto tiene el próximo paso.

## Human decisions

- Si «Qué falta» va siempre visible o plegada (propongo visible: es lo que más se busca).
