# Medir en el arnés la colisión de IDs entre clones

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: colaboracion, arnes


## Objetivo

C4 prueba una tarea común que diverge entre clones, pero no dos tareas nuevas que reciben el mismo ID. Eso pasa cuando dos clones crean una tarea en el mismo segundo y con el mismo sufijo: Task sólo evita la colisión dentro de una misma carpeta. Este hueco aparece como «sin medir» en el requisito de aislamiento.

Hay que extender C4 con la CLI real: mismo ID en dos clones, conflicto add/add al integrar, originales recuperables y migración de uno a un ID nuevo con sus referencias, para que `tasks review` y `tasks refs` lo confirmen. El caso no debe fusionar las dos identidades.

Relacionadas: `20261004-121432-coordinar-dos` (requisito `aislamiento_y_sincronizacion_explicitos`).
