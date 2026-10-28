# Preparar la distribución 0.1.0a15

## Why

La versión 0.1.0a14 ya está publicada en PyPI, pero Factory siguió mejorando después de prepararla: el tablero dice qué falta, quién lo hace y a quién necesita cada cambio; `preguntar` cuenta y lista las specs; `nuevo` crea la plantilla en español o en inglés; el bloqueo de `aprobar-spec` nombra la línea que falta; y la terminal del tablero espera a estar lista. Brian quiere probar Factory fuera de su máquina, en la escuela, y para eso necesita una versión instalable desde PyPI que tenga todo eso.

## What changes

- La versión pasa a 0.1.0a15 en los metadatos del paquete, en la CLI, en el README, en las notas de versión y en la guía y la web.
- Las notas dejan de decir que la 0.1.0a14 está en preparación: está publicada, con su tag y su release. La 0.1.0a15 queda declarada como preparada, no como publicada, hasta que Brian la suba.
- Se construye el wheel y el sdist, se instalan en un entorno nuevo y se comprueban desde fuera del checkout: versión, origen de importación, las consultas de siempre y lo nuevo de esta versión.
- Se corre la suite y se registra la evidencia, con sus hashes y sus límites.

## Out of scope

- Publicar en PyPI, crear el tag o la release de GitHub de la 0.1.0a15: lo hace Brian, o yo por su pedido explícito y después de la revisión y el cierre.
- Cambiar versiones de Oracle, Oracle Task u Oracle Clue.
- Empaquetar la extensión de VS Code en una versión nueva.

## Human decisions

- Que la 0.1.0a15 salga con `bloqueo-causa` (el bloqueo de aprobar-spec que nombra la línea) si ya está integrado cuando se prepare.
