# pedir-revision tolera pedidos simultáneos sobre el mismo candidato

- ESTADO: CERRADA
- PRIORIDAD: 30
- ETIQUETAS: 

### Nota (2026-10-13 11:52:42 UTC)

Visto el 2026-10-13: cuatro pedir-revision lanzados a la vez sobre el mismo candidato chocaron en git worktree add del checkout (.factory/local/revisiones/<sha>: 'ya existe' y lock de git) y además numeran paquete-<revisor>-N contando archivos, lo que también puede pisarse. Se resolvió escalonando los lanzamientos. Arreglo probable: bloqueo por candidato alrededor de crear el checkout y numerar el paquete (como bloqueo_medidas), con una prueba de dos pedidos concurrentes.

### Nota (2026-10-14 12:55:38 UTC)

Hecho en el cambio 20261014-100834-revision-simultanea (merge 2755f75): turno por cambio con fcntl.flock en .factory/local/locks/<id>.pedir.lock alrededor del checkout, el número y la preparación del paquete, y del evento en factory.json; el revisor corre fuera del turno. Probado en real: las dos vueltas de ese cambio lanzaron codex y agy a la vez sin chocar.
