# Oracle Clue como dependencia fija de Factory

## Why

Oracle Clue ya es una pieza central de la revisión: `pedir-revision` arma con él el paquete del candidato y valida el informe del revisor, y `revision-preparar` valida cada informe antes de usarlo. Pero hoy es opcional: Factory lo busca en el `PATH` y, si no lo encuentra, `pedir-revision` no funciona y los informes de revisores entran marcados «sin validar». Ese límite apareció como hallazgo en las revisiones de revisores, decisiones-guiadas y cli-humana, y hubo que aceptarlo cada vez.

Brian decidió (2026-10-12) que Clue pase a ser dependencia fija, como `oracle-metalenguaje` y `oracle-task`.

## What changes

- **`oracle-factory` depende de `oracle-clue`**, fijado con `==` como las otras dos.
- **Factory usa el Clue de su propio entorno**, igual que con `oracle` y `tasks`, y no el que esté en el `PATH`. Una instalación con `uv tool install oracle-factory` funciona sin instalar Clue aparte.
- **Los informes de revisores siempre se validan con Clue.** Desaparece el caso «sin validar». Un informe que no se puede validar se avisa y no se usa, como hoy cuando Clue está instalado.
- **`importar` deja afuera lo que la spec retira.** Es la primera spec con `## REMOVED Requirements`, y el importador de Oracle trajo el requisito retirado como uno nuevo, sin cuerpo y sin poder medirse. Factory lo saca de la importación. Decidido por Brian al aparecer, el 2026-10-12, con una tarea para que el importador de Oracle entienda las secciones.
- **Docs y web**: la instalación nombra a Clue entre las dependencias y deja de tratarlo como algo aparte.

## Out of scope

- **Cambios en oracle-clue.** Excluir rutas, partir el paquete y no guardar rutas absolutas siguen en sus tareas.
- **`trackertast` en PyPI.** El nombre definitivo es `oracle-task`, que Factory, oracle-mcp y commander ya usan. Retirar el paquete viejo se hace en PyPI, fuera de este cambio.

## Human decisions

Decidida por Brian el 2026-10-12, con un menú: la instalación documentada expone también el comando `oracle-clue`, opcional como `oracle` y `tasks` (`--with-executables-from oracle-metalenguaje,oracle-task,oracle-clue`). Factory no lo necesita en el `PATH`, porque usa el de su entorno, pero así quien revisa puede correr `oracle-clue validar` a mano.
