# Avisar de los bucles de revisión y de los cambios demasiado grandes

## Por qué

Nuestros propios datos (20 cambios cerrados, medidos con `tools/medir_rondas.py`) muestran que el tamaño del cambio se asocia con más rondas de revisión (Spearman +0,62 sin el movimiento mecánico de `cli.py`): hasta unas 450 líneas la mediana es de 2 rondas, y por encima, 3. Y los cambios que llegaron a 5 o 6 rondas fueron bucles en los que se parchaba la misma clase de problema caso por caso. Hoy nada de eso se ve: hay que contar rondas y líneas a mano. Las skills de pair programming que estudiamos lo tratan como condiciones de parada (un paso de más de ~50 líneas se parte; dos intentos fallidos son un bucle). Factory ya sabe cuántas rondas hubo (los eventos de revisión) y cuántas líneas cambió el candidato (Git), así que puede avisar sin que nadie cuente.

## Qué cambia

- `oracle-factory estado ID` avisa, sin bloquear nada, cuando el cambio lleva **4 o más rondas de revisión** (candidatos distintos a los que se pidió revisión): sugiere parar a arreglar la clase del problema entera y mirar la lista previa antes de pedir otra.
- `estado` avisa cuando el candidato vigente agrega **más de 450 líneas de producto** (sin contar archivos de pruebas ni los generados por Factory): sugiere partir el cambio. Las 450 son una referencia sacada de 20 cambios, no una ley.
- Los dos avisos salen también en el JSON de `estado` (claves `bucle_de_revision` y `cambio_grande`) y no alteran los pasos pendientes ni el próximo paso.
- `docs/tests.md` aclara que el conteo de aserciones quitadas de los tests editados es aproximado (se reconocen por patrones de lenguaje).

## Fuera de alcance

- Bloquear nada: son avisos para quien decide.
- La alarma de cambio de alcance (archivos del diff que la propuesta no menciona): da demasiados falsos avisos con lo que hoy tenemos; queda para después.
- Avisar de una spec grande (más de N requisitos o escenarios): no tenemos datos todavía.
- Que el pedido al revisor lleve estos avisos.

## Decisiones humanas

- Los umbrales: 4 rondas y 450 líneas de producto.
- Que sean avisos y no bloqueos.
