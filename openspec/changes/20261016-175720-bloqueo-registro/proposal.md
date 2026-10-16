# Dos procesos que escriben el mismo registro no se pisan

## Why

La revisión de revisar-cancelada (codex CXL2-1, 2026-10-16) mostró que el registro de un cambio (`factory.json`) se puede pisar entre procesos. Pasa de dos maneras:

- Las escrituras que comparan con lo leído (`escribir_atomico` con `esperado`) comparan y después reemplazan sin bloqueo, así que otro proceso puede escribir en el medio y su cambio se pierde.
- `guardar`, que usan casi todos los comandos, no compara nada: un proceso que leyó el registro antes que otro lo escribiera lo reemplaza con su copia vieja.

Con dos personas, o una persona y su agente, trabajando el mismo cambio, una decisión registrada (una revisión, una medida) puede desaparecer sin aviso. Tarea `20261016-161146-bloqueo-registro`.

## What changes

- **Se escribe sobre lo que se leyó**: `guardar` compara el registro con lo último que este proceso leyó o escribió de él. Si otro lo cambió entretanto, no lo reemplaza y dice «el archivo cambió durante la operación; volvé a leerlo». Las escrituras que ya pasan su `esperado` siguen igual.
- **Comparar y reemplazar no se separan**: mientras un proceso compara y reemplaza un archivo con `escribir_atomico`, otro que escribe en la misma carpeta espera. Es un `flock` sobre la carpeta, que el sistema suelta si el proceso muere, y no crea archivos de bloqueo.

## Out of scope

- La migración del registro (`migrar`), que escribe por su cuenta y corre una sola vez.
- Fusionar cambios concurrentes: el segundo que escribe recibe el error y vuelve a correr su comando.

## Human decisions

- Brian eligió esta tarea el 2026-10-16, con prioridad 30.
