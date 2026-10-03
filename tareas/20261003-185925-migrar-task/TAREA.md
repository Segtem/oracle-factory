# Migrar a Oracle Task 0.2.0

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 


## Pedido

El usuario pidió el 2026-10-03 migrar todos los consumidores de trackertast a oracle-task y
luego retirar el paquete anterior de PyPI. Coordinación: tarea 20261003-183936-migrar-task del
repositorio Segtem/oracle. Se conservan IDs, documentos de tareas y el alias tasks.


## Verificación

Oracle Task 0.2.0 en la dependencia y resolución del comando tasks. Suite Python: 23 tests verdes. Chromium: 11 comprobaciones, 0 errores y 0 peticiones externas. Wheel instalado fuera del checkout, sin comandos Oracle/tasks globales: init, ejemplo, nueva tarea, importación, revisión, juicio y cierre fixture pasaron. Twine validó wheel/sdist 0.1.0a2.

## Próximo paso

Publicar el corte 0.1.0a2 en PyPI; verificar una instalación limpia antes de retirar trackertast. La aceptación de cambios reales sigue siendo humana.
