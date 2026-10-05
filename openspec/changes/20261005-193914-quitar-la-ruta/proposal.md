# Quitar la ruta privada de los registros ya publicados

## Why

El repositorio `Segtem/oracle-factory` es público y `main` contiene la ruta `/home/workstation/…` en **110 archivos (609 apariciones)**. Casi toda llegó porque Oracle escribe la `fuente` de cada requisito con la ruta de la máquina, y `juzgar` guardaba la ruta absoluta de los hechos. El cambio de portabilidad (`20261005-184427-los-registros-de`) corrige eso hacia adelante; este cambio limpia lo ya escrito.

No es una filtración grave: la ruta sólo muestra el nombre de usuario del sistema y la disposición de las carpetas. Pero es lo mismo que el hallazgo A-04, y Brian pidió limpiarla.

## What changes

Los 110 archivos no son iguales. Se separan según lo que son:

| Grupo | Archivos | Qué se hace |
|---|---|---|
| **Registros que Factory lee:** `fuente` de `requisitos/*.requisito` y de `requisitos-previos/*.txt`, y `hechos` de los `factory.json` de los cambios | **46** | Se reescriben con la ruta relativa al proyecto |
| **Evidencia histórica:** informes y revisiones, paquetes de Clue, salidas del sensor, reportes de agentes (`tareas/**`) | **64** | **No se tocan** |

La evidencia no se reescribe por dos razones. Está atada por hashes (los informes y las decisiones registrados, los hechos del juicio), y los paquetes de Clue *contienen* la ruta del checkout que revisaron, que es parte de lo que validan. Reescribirla rompería las comprobaciones que justamente la hacen confiable.

Detalles de la limpieza de los 46 registros:

1. **Una herramienta de una sola vez** (`tools/limpiar_rutas.py`), idempotente: correrla dos veces no cambia nada.
2. **Las decisiones de medidas conservan su integridad.** Cada decisión guarda el hash del `.requisito`. Al reescribir la `fuente` ese hash cambia, así que la herramienta actualiza el hash de cada decisión afectada y deja un evento `rutas_limpiadas` con el hash anterior y el nuevo, para que `estado` de los cambios cerrados no pase a mostrar pendientes.
3. **Un verificador** (`tools/verify_limpieza.py`) comprueba que ningún registro conserva la ruta, que `tareas/**` no cambió byte a byte, y que `estado` de cada cambio dice lo mismo antes y después.

## Out of scope

- **Reescribir la historia de Git.** Los commits anteriores seguirán conteniendo la ruta en el repositorio público. Quitarla de ahí exige reescribir la historia y forzar el push sobre un repositorio público: rompe todos los clones, no se puede deshacer, y para una ruta que sólo muestra un nombre de usuario no se justifica. Se recomienda no hacerlo.
- La evidencia histórica de `tareas/**` (64 archivos).
- Cambiar cómo Factory escribe las rutas hacia adelante: lo hace el cambio de portabilidad.

## Human decisions

Pendiente de aceptación de proposal.md y spec.md. Preguntas abiertas para Brian:

1. **La historia de Git:** ¿se deja como está (lo recomendado) o se reescribe?
2. **La evidencia de `tareas/**`:** ¿se deja intacta por estar atada a hashes y a paquetes de Clue (lo recomendado)?
3. **Actualizar los hashes de las decisiones** de los cambios cerrados, con un evento que lo documente: ¿de acuerdo? Es reescribir un registro de decisión, aunque sea de forma mecánica y trazable.
4. **Orden:** este cambio modifica requisitos del producto, así que deja desactualizadas las revisiones abiertas. Se propone hacerlo cuando entre a `main` el cambio de portabilidad, que ya reescribe los suyos.

Preparar esta propuesta no acepta el cambio ni autoriza implementarlo.
