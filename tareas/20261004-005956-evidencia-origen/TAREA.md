# Vincular la ejecución del sensor con la versión observada

- ESTADO: ABIERTA
- PRIORIDAD: 10
- ETIQUETAS:

## Hallazgo y alcance

contexto_producto y juzgar capturan versión y huellas actuales, pero juzgar solo consume un JSON suministrado: no ejecuta el sensor ni demuestra que los hechos provengan de esa versión. Un JSON antiguo puede registrarse contra otra versión tras renovar la revisión. La web ya declara el límite. Proponer ejecución explícita del sensor con comando, entradas, contexto antes/después, salida, código de retorno y huella de hechos. Mantener compatibilidad y rechazo claro si cambia el producto durante ejecución. Esto mejora procedencia registrada, no garantiza la corrección del sensor, casos completos ni ausencia de falsificación.

Origen: auditoría 20261003-235610-web-rigurosa, informes agy1/agy2 y lectura directa de la CLI. Esta tarea es una propuesta pendiente, no autorización para implementar una funcionalidad nueva.

### Nota (2026-10-04 00:59:56 UTC)

Registrada como mejora necesaria/propuesta a partir del pedido de revisar la web para principiantes. No se implementó ni simuló aprobación del producto.

## Próximo paso

Reproducir el caso de JSON antiguo en fixture aislado y diseñar una captura de evidencia con límites explícitos; presentar propuesta al usuario antes de implementar.
