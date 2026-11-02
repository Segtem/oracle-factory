# Un camino ligero de revisión para los cambios chicos

## Por qué

Todos los cambios de Factory pasan hoy por el mismo recorrido de revisión, sea una línea de documentación o una regla de decisión. Nuestros datos y esta semana lo confirman: `alarmas-flujo` (unas 150 líneas) cerró en 2 rondas; `verificador-generico` (una herramienta de unas 250 líneas que lee entradas de otros) necesitó 7. Los cambios chicos y mecánicos pagan la misma ceremonia (dos revisores, varias rondas, evidencia de 7 minutos por ronda) que los que de verdad la necesitan, y los estudios que revisamos critican justamente el exceso de ceremonia. Lo que no queremos aflojar son las decisiones humanas ni los controles de lo que decide quién puede hacer qué.

## Qué cambia

- `oracle-factory estado ID` (y su JSON, clave `camino`) dice si el candidato califica para el **camino ligero**: agrega **150 líneas de producto o menos** (las mismas que cuenta la alarma de tamaño) y **no toca las reglas de decisión**, que son `oracle_factory/cli.py`, `modos.py`, `flujo_revision.py`, `flujo_medidas.py`, `revision.py`, `preparacion.py`, `puerta.py` y `unir.py`. Si no califica, dice por qué (cuántas líneas y qué archivos de decisión toca).
- La guía para agentes (`oracle-factory agentes`, bloque de `AGENTS.md`) explica el camino ligero: **un revisor y una ronda**; si esa ronda no trae hallazgos medios ni altos se pasa directo a preparar la revisión; si trae, el cambio sigue el camino completo.
- Nada de lo que decide una persona cambia, ni ningún paso pendiente: sigue siendo necesaria la aprobación de la spec, la confirmación de las medidas, la revisión humana y el cierre. El camino ligero sólo dice cuánta revisión independiente conviene pedir; no la reemplaza ni la bloquea.

## Fuera de alcance

- Exigir o impedir el camino ligero: es una orientación calculada, no un gate. Un cambio que califica puede igual pedir más revisión, y uno que no califica no puede usar el ligero.
- Cambiar el modo de trabajo del cambio, las decisiones de una persona o los pasos que `estado` marca como pendientes.
- Decidir por Brian qué archivos son reglas de decisión: la lista es una propuesta que él aprueba con la spec.
- Un camino aún más corto (sin revisor): no.

## Decisiones humanas

- Los umbrales: 150 líneas de producto y sin tocar las reglas de decisión.
- La lista de archivos que cuentan como reglas de decisión (incluye `cli.py` entero por prudencia: un cambio chico en `cli.py` pasa por el camino completo).
- Que sea una orientación y no un gate.
