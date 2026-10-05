# Registrar en el cambio lo que se decide en la conversación

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: flujo, modos, contexto


## Origen

Análisis del video «IDE vs CLI» (2026-10-05): el contexto —el «por qué»— se pierde en los traspasos. Factory lo guarda bien en la spec y en los registros, pero lo que se decide en la conversación entre persona y agente no queda en el repositorio. En esta sesión hubo que escribir a mano «canal: conversación» y el texto de Brian para la aceptación de colaboración y de modos.

## Objetivo

- Un comando, por ejemplo `oracle-factory nota-decision ID`, que adjunta al cambio una decisión tomada fuera de la CLI: quién, cuándo, canal, texto literal y a qué gate o documento afecta. Queda como evento con `forma: referido`, nunca como decisión del gate.
- `estado` y `donde` las muestran junto al gate, con la advertencia de que no sustituyen la decisión en la CLI.
- Reglas: una decisión referida no cuenta como confirmación de persona. Sólo informa por qué se hizo algo.

Relacionadas: `20261005-105331-modos-de-trabajo` (quién decidió) y `20261005-132144-jerarquia-de` (dónde se guarda).
