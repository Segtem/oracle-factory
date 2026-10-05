# Sacar de /tmp el checkout de revisión de colaboración

- ESTADO: CERRADA
- PRIORIDAD: 40
- ETIQUETAS: colaboracion, revision


## Objetivo

El paquete de Clue del candidato de colaboración apunta a `/tmp/factory-colaboracion-revision-4ceb4b0`, y `/tmp` se borra al reiniciar. Hay que preparar el checkout del candidato vigente en una ruta durable, regenerar ahí el contexto de Clue y conservar el paquete anterior como histórico, sin editar huellas.

El entorno de la validación anterior (`/tmp/factory-guided-env`) tiene el mismo problema. Los checkouts de revisión-guiada (`/tmp/factory-revision-guiada-candidato-*`) también, pero quedan fuera de esta tarea.

Relacionadas: `20261004-121432-coordinar-dos`, `20261005-100124-colision-ids` (cambia el candidato, así que va antes).

### Nota (2026-10-05 10:04:37 UTC)

Checkouts durables en ~/Dev/_revisiones/factory-colaboracion-{4ceb4b0,17d1c00} con paquetes Clue regenerados; el paquete /tmp queda como histórico. Pendiente: retirar el worktree /tmp viejo (git worktree remove) cuando la persona lo autorice.

### Nota (2026-10-05 10:07:26 UTC)

Worktree /tmp/factory-colaboracion-revision-4ceb4b0 retirado con autorización de Brian (2026-10-05). Sólo tenía sin versionar una copia idéntica de evidencia/. El paquete contexto-clue-4ceb4b0.json queda como histórico; su ruta ya no existe.
