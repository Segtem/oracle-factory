# Registros fuera del repo del producto, etapa 4a: Factory commitea en el almacén tras cada comando que escribe registros

## Por qué

Con almacén aparte (etapas 1–3) el ciclo completo funciona, pero los registros que escribe cada comando quedan sin commitear en el almacén: alguien tiene que acordarse de commitearlos a mano, y si no lo hace se pierde la historia y no hay nada que compartir con el equipo. Brian decidió (2026-11-09) que Factory commitea en el almacén tras cada decisión; esta etapa lo hace para todo comando que escribe registros. Compartir entre personas (`conectar URL`, `sincronizar`) es la etapa 4b.

## Qué cambia (sólo con almacén aparte; sin él, nada cambia)

- Al terminar un comando de Factory que cambió archivos del almacén, Factory hace un commit en el almacén con exactamente esos archivos: los que ya estaban modificados antes del comando no entran.
- El mensaje del commit nombra el comando y el cambio, y lleva líneas finales `Cambio: ID`, `Comando: NOMBRE` y `Actor: NOMBRE (persona|agente)`.
- El autor y quien commitea son la identidad de Git que ya tiene configurada el almacén (o la persona): Factory no escribe ninguna configuración de Git.
- Un comando que no cambió nada del almacén (por ejemplo `estado` o `listar`) no hace commit.
- Si el commit no se puede hacer (por ejemplo, Git no tiene identidad configurada, o un hook del almacén lo rechaza), el comando no falla: avisa qué pasó y los registros quedan escritos en el disco.
- No sube nada al remoto.

## Fuera de alcance

- `conectar URL`, `sincronizar` y la unión de registros escritos a la vez por dos personas (etapa 4b).
- Commitear el producto: eso sigue siendo de quien construye.

## Decisiones humanas

Ninguna nueva: es la decisión de Brian del 2026-11-09 (Factory commitea en el almacén) y la regla de no escribir configuración de Git.
