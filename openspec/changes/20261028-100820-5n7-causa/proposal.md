# Que aprobar-spec diga qué línea de qué archivo falta completar

## Why

Al aprobar una spec, Factory bloquea si la propuesta, la spec o las tareas todavía tienen la marca de pendiente de la plantilla. El mensaje decía solo «hay que completar y revisar primero: <archivo>», sin indicar qué línea ni cuántas quedaban. Pasó dos veces en esta sesión, con una propuesta que mencionaba la marca en su propio texto: se perdió un rato buscando una marca que estaba en una frase escrita a mano. Brian pegó el bloqueo y no tenía forma de saber qué hacer.

## What changes

- El bloqueo de `aprobar-spec` nombra, de cada archivo que todavía tiene la marca de pendiente, la primera línea que la tiene (con su número y su texto, acortado) y cuántas más quedan en ese archivo.
- Si hay varios archivos con pendientes, el mismo mensaje los lista todos, en el orden de siempre (propuesta, spec, tareas), en lugar de decir uno por vez.
- Si falta un archivo, el mensaje dice que falta, no que hay que completarlo.
- El mensaje sigue empezando con «hay que completar y revisar primero: <ruta>», para que no cambie lo que ya lo lee.

## Out of scope

- Los otros mensajes de bloqueo de Factory.
- Aprobar sin completar, o saltearse la marca.
- Marcar la línea en el editor o en el tablero.

## Human decisions

- Cuánto texto de la línea mostrar (propongo 80 caracteres, con puntos suspensivos si se corta).
