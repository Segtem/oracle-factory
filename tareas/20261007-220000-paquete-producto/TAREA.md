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
- El `.pedido.md` que se guarda en `revision/` lleva rutas absolutas de la máquina (checkout, paquete, informe, y lo que se escriba en `--pedir`). Brian aceptó publicarlas en el cambio revisores (2026-10-07), igual que la ruta del repo en los informes de Clue; el pedido guardado debería usar rutas relativas al repo.
- 2026-10-07, cambio decisiones-guiadas: el límite saltó en la primera vuelta. El diff de producto suma ~1,1 MB, porque el paquete lleva el texto completo, antes y después, de cli.py (240 KB) y de 17 pruebas migradas de forma mecánica. Se revisó en dos partes. La base fue un commit aparte (`refs/factory/base-mecanica-decisiones`): main más la migración mecánica, que cubre la suite. Así el paquete bajó a ~506 KB. Excluir rutas de registro no alcanza: Clue debería poder mandar sólo el patch con contexto en los archivos grandes, o partir el paquete.
- Los límites que escriben los revisores en sus informes («Corrí PATH=/tmp/… /home/…/python …») llevan rutas absolutas de la máquina y pasan al informe preparado y a `.factory/resumen.md`. El pedido podría indicar que los límites usen rutas relativas al repo, o Factory relativizarlas al copiar.
