# El tablero de comando en VS Code: qué te necesita, la línea de tiempo, los hallazgos y las métricas

## Why

Brian probó Factory desde cero en `~/Proyectos/CLab/Chess` (2026-10-17) y vio todo estático: en la vista de VS Code no podía abrir los requisitos ni las medidas, los hallazgos de la revisión no aparecían, no había forma de ver qué pasó y cuándo, ni números del proceso. Pidió que Factory sea «un dashboard de comando, con acceso a todo, la trazabilidad de todo y métricas», que viva **sólo en VS Code** y que el tablero llegue antes que unir commits al cambio y que «¿por qué existe esta línea?» (que después se le suman como secciones). El registro de cada cambio ya guarda casi todo: quién decidió qué y cuándo, cada pedido de revisión con sus hallazgos, cada juicio y el cierre.

## What changes

- **`oracle-factory tablero --json`**: un esquema versionado que junta, por cambio abierto, lo que necesita una decisión de la persona y su comando, la línea de tiempo (cada evento con quién, cómo y cuándo), los hallazgos de los revisores del candidato vigente (archivo, línea, severidad, revisor y qué se decidió), los requisitos con sus medidas y los archivos que los definen, los avisos, y las métricas del cambio; y del proyecto, las métricas generales. La CLI ya tiene `estado`, `donde` y `resumen` en JSON: éste los junta y suma lo que faltaba.
- **El tablero en VS Code**: un panel «Tablero de Factory» en la extensión que muestra eso con el estilo de la web. Arriba, lo que te necesita ahora, con el botón que escribe el comando en la terminal sin ejecutarlo; la línea de tiempo; los hallazgos, que se abren en su `archivo:línea`; los requisitos, que abren su `.requisito` y el catálogo de sus medidas; y las métricas. Se actualiza solo cuando cambia un registro. No decide nada.
- **Métricas**, todas contadas del registro: por cambio, el tiempo en cada fase y hasta el cierre, las vueltas de revisión, los hallazgos por severidad y por revisor, los riesgos aceptados, las decisiones de persona y de agente, y los requisitos medidos y cumplidos; del proyecto, los cambios abiertos, cerrados y abandonados, la mediana de tiempo hasta el cierre, la proporción de cambios que cerraron en la primera vuelta de revisión y qué revisor encontró qué.

## Out of scope

- Unir commits al cambio y «¿por qué existe esta línea?»: los dos cambios siguientes, que suman secciones al tablero.
- Una web local fuera de VS Code (Brian eligió sólo VS Code).
- Decidir desde el tablero: las decisiones siguen en la terminal.

## Human decisions

- Brian pidió el tablero de comando y eligió el 2026-10-17 que viva sólo en VS Code y que llegue antes que commits y «¿por qué?».
