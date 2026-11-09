# Registros fuera del repo del producto, etapa 1: dos raíces (producto y registros)

## Por qué

Un equipo que usa Factory no quiere que el repo de su producto reciba los archivos de Factory (`.factory/`, `tareas/`, `openspec/`, `requisitos/`, `catalogos/`, `kb/`). Hoy hay una sola raíz (`ROOT`) que es a la vez la del producto (donde se corre git) y la de los registros. Esta es la primera de seis etapas (ver la memoria `factory-registros-locales`): separar las dos raíces en el código, sin cambiar nada de lo que ya funciona.

Decisiones de Brian (2026-11-09): el almacén es un repo Git propio del equipo, Factory commitea en él tras cada decisión (publicarlo sigue pasando por su menú) y cada persona lo conecta con `oracle-factory conectar` (etapa 2).

## Qué cambia

- Una opción global `--registros RUTA`: la carpeta del almacén de registros. Sin ella, la raíz de los registros es la del producto, y todo funciona exactamente como hoy.
- Con `--registros`, todo lo que Factory guarda como registro (la configuración y las carpetas de los cambios en `.factory/`, `tareas/`, `openspec/`, `kb/`, y el proyecto Oracle con `requisitos/` y `catalogos/`) vive bajo esa carpeta, con las mismas rutas relativas que hoy bajo la raíz del proyecto. La raíz del producto es `--proyecto` o la carpeta actual, y Factory no escribe nada en ella.
- `init --registros RUTA` prepara el almacén en RUTA y no toca el repo del producto (ni su `.gitignore`).
- Los comandos que dependen del candidato (`pedir-revision`, `revision-preparar`, `revision`, `revisar`, `juzgar`, `cerrar`) todavía no se admiten con registros aparte: fallan con un mensaje claro que dice que es la etapa 3 y no escriben nada. `estado` funciona y muestra el cambio sin candidato.
- La opción se documenta como experimental, etapa 1 de 6.

## Fuera de alcance

- Cómo se encuentra el almacén sin `--registros` (`conectar`, etapa 2), el candidato y la huella con dos fuentes (etapa 3), la sincronización y el bloqueo entre personas (etapa 4), la guía de agentes, la skill y la extensión de VS Code (etapa 5) y la migración (etapa 6).
- Commitear dentro del almacén.

## Decisiones humanas

Ninguna nueva: es la etapa 1 del plan que Brian aprobó.
