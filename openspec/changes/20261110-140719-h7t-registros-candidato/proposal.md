# Registros fuera del repo del producto, etapa 3: el candidato y la huella con dos fuentes

## Por qué

Con las etapas 1 y 2 un equipo ya puede conectar su producto a un almacén de registros aparte, pero no puede revisar, juzgar ni cerrar: esos comandos se niegan («etapa 3 de 6»). Hoy el candidato vigente y la huella de lo revisado salen de un solo repo, donde conviven el código y los registros, y todas las llamadas a git corren sobre esa raíz. Con almacén aparte, esas llamadas corren sobre el almacén, que no es el producto. Esta etapa hace que el ciclo completo funcione con los registros fuera del repo del producto.

Decisiones de Brian (2026-11-10): la huella es el producto más sólo este cambio del almacén; el candidato es el ancestro más cercano de HEAD con evidencia en el almacén; no se instala ningún hook en el producto.

## Qué cambia (sólo con almacén aparte; sin él, nada cambia)

- **Candidato vigente**: el commit del producto más cercano a HEAD que tiene carpeta de evidencia en el almacén para el cambio, siempre que el producto no haya cambiado desde ese commit y no tenga cambios locales.
- **Huella de lo revisado** (lo que decide si una revisión o un juicio siguen vigentes): el producto (su HEAD y sus archivos no ignorados) más los archivos de este cambio en el almacén: su propuesta y su spec, sus requisitos y los catálogos de las medidas que tiene elegidas. Un cambio en otro cambio del almacén ya no invalida la revisión ni el juicio de este.
- **Lo que mira el producto** (diferencias, base del candidato, paquete y copia para los revisores, trazabilidad, alarmas, `log`, `por-que`, `ruta`, `procedencia`) corre sobre el repo del producto, sin escribir nada en él: ni en su árbol de trabajo ni en su `.git` (índice, refs, hooks, configuración ni objetos sueltos).
- `pedir-revision`, `revision-preparar`, `revision`, `revisar`, `juzgar` y `cerrar` dejan de negarse con almacén aparte.
- `hooks` no instala nada en el producto con almacén aparte: lo dice, y los commits de un cambio se deducen de sus candidatos.

## Fuera de alcance

- Commitear en el almacén tras cada decisión, clonar el almacén desde una URL, sincronizar y bloquear entre personas (etapa 4); la puerta de salida y los hooks del almacén (etapa 4).
- La guía de agentes, la skill y la extensión de VS Code fuera del repo (etapa 5); la migración (etapa 6).

## Decisiones humanas

Las tres de arriba, ya tomadas por Brian; se confirman al aprobar la spec.
