# Un comando que avance el flujo con el próximo paso correcto según el modo

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: flujo, cli, modos, autoproduccion


## Origen

Análisis del video «IDE vs CLI» (IBM Technology, 2026-10-05) contra Factory: el video pide ejecución de varios pasos sin que la persona cargue el contexto de un paso al siguiente. Hoy Factory tiene las fases y un «próximo paso», pero cada una se corre a mano y `estado` sugirió un paso equivocado más de una vez (después de `medir`, después de `juzgar`, y con medidas sin decisión).

## Objetivo

- `oracle-factory avanzar ID`: muestra el siguiente paso real del cambio y el comando exacto, y quién lo da según el modo (persona desde su terminal, agente con `--agente`, o una persona que confirma una propuesta).
- Si el siguiente paso lo puede dar quien lo invoca, lo ejecuta tras mostrarlo; si es una decisión de persona, se detiene y lo dice. Nunca salta un gate.
- `siguiente()` y `estado` usan la misma lógica, para que dejen de sugerir pasos ya hechos.

Relacionadas: `20261005-105254-cli-piloto` (la parte de `estado`), `20261005-112955-cli-humana` y `20261005-105331-modos-de-trabajo`. Depende de que los modos estén integrados.

### Nota (2026-10-07 11:47:31 UTC)

Parte del objetivo «Factory se construye a sí misma» (2026-10-07).

- 2026-10-07 (cambio 20261007-192608-revisores): confirmar medidas reescribe `requisitos/*.requisito`, que es producto; si se hace después de la última vuelta de revisión y de la evidencia, el candidato queda viejo y `revision-preparar` sale vacía. El orden que funciona es medir (propuesta y confirmación) → vueltas de revisión → evidencia → revision-preparar. `avanzar` debería guiar ese orden, y `revision-preparar` avisar cuando no hay candidato vigente en vez de dejar el informe vacío en silencio.
