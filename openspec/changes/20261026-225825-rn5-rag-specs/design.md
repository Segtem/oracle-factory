# Design

- `consultas.interpretar_specs` reconoce `spec`, `specs`, `especificacion(es)` y `capacidad(es)` en preguntas de contar o listar («cuántas», «cuáles», «qué specs hay»). Lo compuesto («y»), lo que nombra tareas o cambios y lo que explica («qué son las specs») va al modelo o al buscador; un filtro que no se admite (fechas, negaciones, aprobadas, pendientes…) se rechaza, pero sólo en una pregunta de contar o listar. «Vigentes» y «abiertas» se aceptan como descriptores: siempre se responden las dos cantidades rotuladas.
- `consultas.specs(cli)` lee `openspec/specs/*/spec.md` y, de los cambios abiertos del registro, `openspec/changes/<id>/specs/*/spec.md`.
  Devuelve la misma forma de fuente que `registro` (ruta, cita, texto, archivos, huella del inventario) para que la respuesta
  traiga su respaldo. Cada `spec.md` se acepta sólo si ni él ni su camino son enlaces ni salen del proyecto (`ruta_segura`).
- `consultas.directa` arma la respuesta: «Hay N specs vigentes y M en cambios abiertos» y, si se pidió lista, una línea por spec.
