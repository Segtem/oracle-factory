# Archivar al cerrar: la spec de cada cambio se fusiona en openspec/specs/

## Why

Para saber qué hace Factory hoy hay que leer 16 propuestas y sus specs, cada una con lo que ese cambio agregó. No existe un documento por capacidad con los requisitos vigentes: la estructura de carpetas, por ejemplo, está repartida entre `estructura` y `estructura2`. OpenSpec lo resuelve con un paso de archivo que fusiona la spec delta de cada cambio en `openspec/specs/<capacidad>/spec.md`, la fuente de verdad. Factory usa el formato de OpenSpec pero no tiene ese paso, así que lo que hay que leer sólo crece.

Es la primera pieza del plan «comprimir lo que se lee, no lo que se guarda» (tarea `20261006-160411-archivar`): el registro sigue append-only y atado a hashes, y encima hay vistas que la herramienta deriva de forma determinista.

## What changes

1. **Al cerrar, la spec del cambio se fusiona** en `openspec/specs/<capacidad>/spec.md`: `ADDED` agrega requisitos, `MODIFIED` reemplaza el requisito del mismo nombre, `REMOVED` lo quita; una spec sin encabezados de delta cuenta como `ADDED`. Cada requisito vigente dice de qué cambio viene y cuál es su requisito de Oracle.
2. **Un conflicto no se resuelve solo:** si la fusión no es posible (agregar un requisito que ya existe, modificar o quitar uno que no existe), `cerrar` lo dice y no cierra.
3. **Nada de lo cerrado se mueve ni se reescribe.** A diferencia de OpenSpec, la carpeta del cambio queda en `openspec/changes/<ID>/`: la citan la fuente de cada requisito, el registro y la huella del producto. El cambio queda marcado como archivado en su registro.
4. **Vigentes y reemplazados:** los requisitos de Oracle no se reimportan ni se tocan; de cada uno se puede saber si está vigente o fue reemplazado, y por qué cambio. Las medidas que confirmó una persona siguen valiendo.
5. **Los 7 cambios cerrados de este repositorio se archivan** en orden de cierre, con un mapeo de capacidades que acepta la persona junto con esta spec.
6. `listar`, `donde` y `buscar` muestran el archivo; la guía `docs/estructura.md` describe `openspec/specs/`.

## Out of scope

- Mover la carpeta de un cambio a `openspec/changes/archive/` (decidido: no se mueve).
- Reimportar requisitos en un dominio por capacidad.
- Los 9 cambios que nunca se cerraron (6 con registro abierto y 3 sin registro de Factory, de antes del flujo), aunque varios ya están en el release: archivarlos sin cierre saltearía el gate humano. Queda como tarea propia decidir, cambio por cambio, si se cierra o se abandona.
- El resumen del estado actual y el `factory-mcp` (tareas `resumen` y `factory-mcp`).

## Human decisions

Respondidas por Brian el 2026-10-06:

1. **La carpeta del cambio:** *no se mueve*; archivar es fusionar la spec y marcar el registro.
2. **Cuándo:** *al cerrar, automático*.
3. **Requisitos de Oracle:** *quedan como están*; se marca cuál es vigente y cuál reemplazado.
4. **Capacidades con dos nombres:** *se unen con un mapeo que confirma la persona*. El mapeo propuesto, a aceptar con esta spec:
   - `estructura2` → `estructura` (la fase 2 extiende la estructura de carpetas).
   - Las demás capacidades de los cambios cerrados conservan su nombre: `revision-guiada`, `modos`, `vigencia`, `portabilidad`, `limpieza`.
   - Para cuando se cierren: `distribution` → `distribucion`.
