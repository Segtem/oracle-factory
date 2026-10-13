# pedir-revision tolera pedidos simultáneos sobre el mismo candidato

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: 

### Nota (2026-10-13 11:52:42 UTC)

Visto el 2026-10-13: cuatro pedir-revision lanzados a la vez sobre el mismo candidato chocaron en git worktree add del checkout (.factory/local/revisiones/<sha>: 'ya existe' y lock de git) y además numeran paquete-<revisor>-N contando archivos, lo que también puede pisarse. Se resolvió escalonando los lanzamientos. Arreglo probable: bloqueo por candidato alrededor de crear el checkout y numerar el paquete (como bloqueo_medidas), con una prueba de dos pedidos concurrentes.
