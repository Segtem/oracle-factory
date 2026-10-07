# El paquete de Clue de pedir-revision deja afuera los registros de Factory

- ESTADO: ABIERTA
- PRIORIDAD: 9
- ETIQUETAS: revision, clue, autoproduccion


## Objetivo

`pedir-revision` arma el paquete de Clue con el diff contra `main`, y ese diff incluye los informes, pedidos y evidencia de cada vuelta en `.factory/cambios/…` y las notas en `tareas/`. El paquete lleva el texto completo de cada archivo y tiene un límite de 1 MB: en el cambio 20261007-192608-revisores, tras 17 vueltas, `oracle-clue preparar` falló con «contexto demasiado grande; dividí la revisión» (83 archivos en el diff, 28 de producto). Cuantas más vueltas, más crece, hasta que la revisión deja de ser posible.

## Notas

- Lo ideal es que Clue acepte excluir rutas (`--excluir PATRÓN`, que quedan en `omissions` con su motivo) y que Factory pase las de registros (`.factory/cambios/`, `tareas/`, las de `es_producto`). Es un cambio en oracle-clue (otro repo y release).
- Mientras tanto: `pedir-revision ID --a NOMBRE --base <último candidato revisado completo>` revisa sólo el delta (usado en ese cambio).
- Revisar también que el revisor no gaste contexto leyendo informes de vueltas anteriores que no son producto.
