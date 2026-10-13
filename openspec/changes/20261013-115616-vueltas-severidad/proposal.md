# Vueltas de revisión proporcionales y riesgos aceptados que persisten

## Why

La regla de las vueltas de revisión es «hasta que no queden hallazgos». Medido en los 62 candidatos revisados de este repo, 14 vueltas trajeron sólo hallazgos bajos: 6 en `revisores`, 3 en `cli-humana`, 2 en `autoproduccion`, 2 en `clue-dependencia` y 1 en `decisiones-guiadas`. Cada vuelta cuesta un candidato nuevo y unos diez minutos de revisores. Pero el corte no puede ser automático: en `revisores`, después de tres vueltas con sólo bajos, vino un hallazgo medio real. Por eso Factory sólo sugiere; lo que corta es la persona.

Además, aceptar un riesgo vale hoy para un candidato. Cuando el mismo hallazgo vuelve en la vuelta siguiente, la persona lo decide otra vez, y el agente escribe a mano en cada `--pedir` «límites asumidos, no los reportes».

Tareas de origen: `20261007-212700-vueltas-severidad` y `20261008-120645-aceptados`. Brian eligió hacerlas juntas el 2026-10-13, con un menú.

## What changes

- **Corte por severidad.** `pedir-revision` cuenta los hallazgos del informe por severidad. Si en el candidato no queda ningún hallazgo medio o alto sin aceptar, dice que no hace falta otra vuelta y que los bajos los decide la persona en `revisar`. Si queda alguno, pide corregirlo y pedir otra vuelta. `estado` sugiere lo mismo como próximo paso. Una severidad desconocida o ausente cuenta como media.
- **Riesgos aceptados que persisten.** Cuando la persona acepta un riesgo en `revisar`, queda en el registro del cambio con su motivo, quién y cuándo, y sigue vigente para los candidatos siguientes. `pedir-revision` los incluye solo en el pedido a cada revisor. Si un hallazgo vuelve (mismo archivo y mismo título normalizado), `revisar` lo muestra como ya aceptado y la persona elige entre mantenerlo, con el mismo motivo, o revocarlo y decidirlo de nuevo.

## Out of scope

- Configurar el corte (por ejemplo, cortar también en bajos). El corte fijo en «medio o más» alcanza para lo medido; se agrega si un proyecto lo necesita.
- Riesgos aceptados para todo el proyecto. Valen para el cambio; al cerrarlo, siguen en sus decisiones y en el resumen como hoy.
- Que el agente proponga aceptar un riesgo. Sigue siendo sólo de la persona.
- Reconocer un hallazgo reescrito con otras palabras: no coincide y se decide como nuevo, que es el lado seguro.

## Human decisions

- Brian eligió el alcance (2026-10-13): las dos tareas en un cambio, y que el corte sólo sugiera.
