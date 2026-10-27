# El tablero dice a quién necesita cada cambio y qué pasó hace poco

## Why

Cuando dos personas trabajan en el mismo proyecto, el tablero de cada una muestra «TE NECESITA» en toda decisión pendiente, aunque el cambio lo tenga otra persona: Brian preguntó cómo lo vería otra persona trabajando en simultáneo, y hoy vería pedidos que no son suyos. Tampoco hay un lugar donde ver qué pasó últimamente en el proyecto (quién decidió qué, cuándo) sin abrir la línea de tiempo de cada cambio.

## What changes

- `oracle-factory tablero --json` suma `yo`: el nombre de Git de quien lo corre (sólo se lee; vacío si no hay).
- En la página, la decisión de una persona de un cambio cuyo responsable es otra persona se rotula «LA DECIDE <NOMBRE>» en vez de «TE NECESITA». Si el cambio no tiene responsable, o el responsable sos vos, sigue «TE NECESITA».
- El proyecto suma `actividad`: los últimos 10 eventos de todos los cambios abiertos, del más nuevo al más viejo, y la página los muestra en «Actividad reciente» con quién, qué, en qué cambio y cuándo.

## Out of scope

- Presencia en vivo (quién tiene el tablero abierto) y avisos o notificaciones.
- Que un invitado de Live Share vea sus propios pedidos: ve el tablero de quien comparte, con el `yo` de esa persona (se documenta).
- Cambiar quién puede decidir: «LA DECIDE» es información, no un candado.

## Human decisions

- Comparar `yo` con el responsable por nombre exacto de Git (propuesto, igual que ya hace el trailer de commits); si escribís distinto tu nombre, vas a ver «LA DECIDE» sobre lo tuyo.
