# Design

- `consultas.interpretar` reconoce `spec`, `specs`, `especificacion(es)` y `capacidad(es)` con «cuántas/cantidad» o «lista/cuáles», con las
  mismas salvaguardas que ya tiene para cambios: compuestas (` y `) pasan al modelo, filtros temporales se rechazan.
  Si la pregunta también nombra tareas o cambios, manda el camino de cambios (sin cambio de comportamiento).
- `consultas.specs(cli)` lee `openspec/specs/*/spec.md` y, de los cambios abiertos del registro, `openspec/changes/<id>/specs/*/spec.md`.
  Devuelve la misma forma de fuente que `registro` (ruta, cita, texto, archivos, huella del inventario) para que la respuesta
  traiga su respaldo.
- `consultas.directa` arma la respuesta: «Hay N specs vigentes y M en cambios abiertos» y, si se pidió lista, una línea por spec.
