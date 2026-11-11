# Registros fuera del repo del producto, etapa 4b2: conectar desde una URL y sincronizar el almacén entre personas

## Por qué

Con las etapas 1 a 4b1, una persona puede trabajar con los registros fuera del repo de su producto, y Factory commitea en el almacén lo de cada comando. Para que un **equipo** comparta el almacén falta lo último: que cada integrante pueda obtenerlo desde la URL del repo del equipo y que los registros de todos se junten. Brian decidió (2026-11-10): el driver de unión se pasa en cada comando con `git -c` (no se escribe configuración de Git en ningún repo) y subir el almacén es sólo de una persona.

## Qué cambia (sólo con almacén aparte; sin él, nada cambia)

- **`conectar URL`**: si el argumento es una URL de Git (no una carpeta), Factory clona el almacén en una carpeta propia del usuario (`$XDG_DATA_HOME/oracle-factory/almacenes/NOMBRE`, o `~/.local/share/...`) y lo conecta como en la etapa 2. Si esa carpeta ya existe y es un clon de la misma URL, la reusa; si es otra cosa, se niega sin tocar nada.
- **`sincronizar`** (desde el producto conectado): trae lo del remoto del almacén y lo une con lo local. Usa los drivers de unión de Factory pasados con `git -c` en esa misma orden (el registro de un cambio editado por dos personas se une sin perder eventos; lo generado se rehace), con el `.gitattributes` del almacén, que Factory escribe si falta (es contenido versionado, no configuración). Después de unir, rehace lo generado y lo commitea. Si quien sincroniza es una persona, sube el resultado; con `--agente` sólo trae y une, y dice que no subió.
- Si el almacén tiene cambios sin commitear, o la unión deja un conflicto que los drivers no resuelven, `sincronizar` no deja nada a medias: se niega o deshace la unión, y dice qué archivos chocaron.
- `sincronizar` toma el bloqueo del almacén de la etapa 4b1 mientras une y commitea.

## Fuera de alcance

- La guía de agentes, la skill y la extensión de VS Code fuera del repo (etapa 5); la migración (etapa 6).
- Autenticación con el remoto: la de Git de cada persona.

## Decisiones humanas

Ninguna nueva: las de Brian del 2026-11-10 (driver por comando, subir sólo una persona).
