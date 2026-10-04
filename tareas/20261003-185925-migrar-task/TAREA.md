# Migrar a Oracle Task 0.2.0

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 


## Pedido

El usuario pidió el 2026-10-03 migrar todos los consumidores de trackertast a oracle-task y
luego retirar el paquete anterior de PyPI. Coordinación: tarea 20261003-183936-migrar-task del
repositorio Segtem/oracle. Se conservan IDs, documentos de tareas y el alias tasks.


## Verificación

Oracle Task 0.2.0 en la dependencia y resolución del comando tasks. Suite Python: 23 tests verdes. Chromium: 11 comprobaciones, 0 errores y 0 peticiones externas. Wheel instalado fuera del checkout, sin comandos Oracle/tasks globales: init, ejemplo, nueva tarea, importación, revisión, juicio y cierre fixture pasaron. Twine validó wheel/sdist 0.1.0a2.


### Nota (2026-10-03 23:44:40 UTC)

Main empujado, tag v0.1.0a2 y release GitHub publicados con wheel/sdist/SHA256SUMS: https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a2. CI exitoso. En Factory, web publicada verificada HTTP 200 e idéntica a main; en MCP, herramienta global actualizada desde release con hash y sin trackertast.

### Nota (2026-10-04 00:52:01 UTC)

PyPI oracle-factory 0.1.0a2 verificado: hashes wheel/sdist coinciden con el release, dependencias sin trackertast, y ejemplo completo en entorno aislado fuera del checkout hasta cierre fixture. Evidencia en Oracle 20261003-183936-migrar-task. La nueva revisión de la web se sigue en 20261003-235610-web-rigurosa.

## Próximo paso

Ninguno en este consumidor. El retiro de trackertast se coordina en Oracle, tarea 20261003-183936-migrar-task.
