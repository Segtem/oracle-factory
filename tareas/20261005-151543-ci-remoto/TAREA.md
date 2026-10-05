# Chequeo de Factory para CI y trabajo entre máquinas

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: flujo, ci, colaboracion


## Origen

Análisis del video «IDE vs CLI» (2026-10-05): lo más débil de Factory frente a lo que pide es el acceso a otros entornos. Todo es local, en una máquina y en Linux; Factory no tiene CI, y el trabajo entre máquinas distintas quedó declarado sin medir en el piloto de colaboración.

## Objetivo

- `oracle-factory verificar` (apto para CI): comprueba de sólo lectura, sin terminal ni decisiones, que cada cambio esté consistente: spec vigente, medidas con decisión vigente (hash del `.requisito`), revisión y juicio sobre el contexto actual, evidencia con sus huellas. Sale con código distinto de cero y dice qué falta.
- Un ejemplo de workflow de CI y del hook `pre-push` para un proyecto Factory.
- Medir el trabajo entre dos máquinas: el piloto de colaboración con clones y remoto en máquinas distintas, hoy sin medir (requisito `aislamiento_y_sincronizacion_explicitos`).

Un CI que corre `verificar` no confirma ni cierra nada: eso sigue siendo de una persona o, en modo autónomo, de un agente identificado. Relacionadas: `20261004-121432-coordinar-dos`, `20261005-105254-hechos-varios`.
