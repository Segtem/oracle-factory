# Preguntar cuántas specs hay y cuáles son

## Why

En el piloto de uso, Brian Hollweg preguntó `oracle-factory preguntar "Cuantas spec hay?"` y obtuvo «No encontré respaldo
suficiente para responder» con ocho pasajes sueltos. El camino directo al registro de `preguntar` sólo entiende
preguntas sobre tareas y cambios; una pregunta de conteo sobre specs cae al buscador de texto, que no cuenta.

## What changes

`preguntar` contesta desde las carpetas de specs, con número y lista, las preguntas de cuántas y cuáles specs hay.
La respuesta separa dos cantidades que «spec» puede significar:

- las **specs vigentes**: una por capacidad, en `openspec/specs/<capacidad>/spec.md`;
- las **specs en cambios abiertos**: las de `openspec/changes/<id>/specs/` de cambios que no están cerrados ni abandonados.

Cita los archivos leídos. Una pregunta de specs con un filtro que no se admite (por ejemplo, por fecha) se rechaza
diciéndolo, en vez de devolver pasajes. Las preguntas sobre tareas y cambios, y las de documentos, responden igual que hoy.

## Out of scope

- Contar requisitos, escenarios o medidas.
- Preguntas compuestas («specs y cambios abiertos»), que siguen yendo al modelo si está configurado.
- Cambiar la elaboración generativa.

## Human decisions

- Brian confirma que «specs» se responda con las dos cantidades (vigentes y en cambios abiertos) y no con una sola.
