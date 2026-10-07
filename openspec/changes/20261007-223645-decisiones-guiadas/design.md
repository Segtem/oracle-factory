# Design

- **Un solo punto de entrada.** `confirmar_persona` (hoy compara una frase) pasa a `elegir(pregunta, opciones)`, que imprime la pregunta y las opciones numeradas y devuelve la elegida. Sin tty, falla igual que hoy. Todas las decisiones de persona ya pasan por `confirmar_persona`, así que el cambio de interfaz es en un lugar.
- **Biblioteca estándar.** Se usa `input()` con números: nada de curses ni dependencias nuevas.
- **Motivo propuesto.** La propuesta del agente ya se guarda en `estado["propuestas"][decision]` con su firma. Se le agrega `motivo`. El registro guarda `motivo` y `origen_motivo` (`agente`, `armado` o `persona`).
- **`revisar`.** Reusa `preparar_revision`, `documentos_revision.validar` y `revisar_guiado`. Completa en memoria los campos que hoy edita la persona (revisor desde `git config user.name`, `completa`, el SHA del informe, las resoluciones de hallazgos) y escribe el par en `tareas/<ID>/revisiones/` como hoy, para que la evidencia no cambie de forma.
- **`medir --confirmar`.** Recorre las propuestas pendientes de medidas y para cada una llama al mismo camino que el comando repetido sin `--agente`.
- **Pruebas.** Los menús se prueban sustituyendo `input` y `terminal_interactiva`, como las pruebas actuales de confirmación.
