# Salidas en JSON de estado, donde y resumen

## Why

Lo que Factory sabe de un cambio hoy sólo se lee como texto para una persona. Un IDE, un panel o `factory-mcp` tendrían que parsear esas líneas, que cambian cada vez que mejoramos un mensaje. Es lo que Docker resuelve con una API estable del motor, con la CLI, Docker Desktop y los IDE como clientes. Esta es esa API para Factory: el primer paso del plan de revisión en el IDE, para revisar el código hecho por IA por promesa (requisito, medidas, veredicto) y no por archivo.

Tarea de origen: `20261007-123220-cli-json` (prioridad subida a 45 por Brian el 2026-10-12, con la comparación con Docker). Brian eligió seguir con ésta el 2026-10-13.

## What changes

- **`oracle-factory estado ID --json`** imprime un objeto JSON con esquema versionado (`"esquema": "oracle-factory.estado/1"`): fase, modo, candidato vigente, requisitos con sus medidas y quién las decidió, pendientes, próximo paso, cada decisión (spec, revisión, cierre, abandono) con quién, cómo, cuándo y motivo, la revisión y el juicio con el commit al que se refieren y si siguen vigentes, y los riesgos aceptados. No ofrece ejecutar nada ni pregunta.
- **`oracle-factory donde ID --json`** imprime los artefactos del cambio (`oracle-factory.donde/1`): gate, ruta, si existe o es histórico o no válido, y nota.
- **`oracle-factory resumen --json`** imprime el resumen del proyecto (`oracle-factory.resumen/1`): lo vigente por capacidad, los cambios abiertos con sus pendientes, los abandonados, las carpetas sin registro, los riesgos aceptados y los límites. No escribe `.factory/resumen.md`. Las mismas entradas dan los mismos bytes, como el resumen en texto.
- **La salida de texto no cambia.** Con `--json`, los errores siguen yendo a stderr con código 1 y stdout queda vacío, para que un cliente no lea un JSON a medias.

## Out of scope

- Decidir desde un cliente (aprobar, revisar, cerrar): sigue siendo de una persona en su terminal.
- JSON del resto de los comandos y una gramática sustantivo + verbo: se suman cuando un cliente los necesite.
- La extensión de VS Code, el panel y `factory-mcp`: son los clientes de esta API, en sus tareas.

## Human decisions

- Brian eligió seguir con cli-json (2026-10-13).
- Las claves van en español, como `factory.json`; el número de esquema sube sólo si se quita o cambia el sentido de una clave (sumar claves no lo sube).
