# Paquete de Clue sin los registros de Factory

- ESTADO: CERRADA
- PRIORIDAD: 35
- ETIQUETAS: 

### Nota (2026-10-13 22:08:20 UTC)

Visto en 20261013-180751-trazabilidad: en la vuelta 4, oracle-clue preparar falló con «contexto demasiado grande» (LIMIT 1 MB): el paquete medía 1,22 MB porque incluye .factory/ y tareas/ (trazabilidad.json y suite.txt de cada candidato anterior, informes de revisión: 524 KB) además del producto (cli.py solo, 337 KB con base, head y parche). Se resolvió con pedir-revision --base <candidato anterior> (vueltas incrementales). Arreglo: que Clue pueda excluir rutas (es_producto de Factory), o que pedir-revision use sola la base incremental cuando el paquete completo no entra, y lo diga en el pedido.

### Nota (2026-10-13 22:14:24 UTC)

Duplica la tarea paquete-producto, que ya pedía esto con más contexto; se trabaja ahí y ésta se cierra.
