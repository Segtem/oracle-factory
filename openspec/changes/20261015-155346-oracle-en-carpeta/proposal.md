# El proyecto Oracle puede estar en una carpeta del proyecto

## Why

Brian decidió el 2026-10-15 mudar Jam y LyraGASP para que consuman Factory. Los dos tienen su proyecto Oracle en `medidas/` (`medidas/oracle.json`, `medidas/requisitos/`, `medidas/catalogos/`), con sensores, sombras con cota y hooks `pre-push` que dependen de esa ruta. Factory supone que el proyecto Oracle es la raíz del repositorio: lee y escribe `requisitos/` y `catalogos/` ahí, y corre Oracle con `--proyecto` en la raíz. Además, los dos tienen `escalares.py`, que Oracle sólo ejecuta con `--confiar-escalares`, y Factory nunca lo pasa. Brian eligió que Factory lo haga configurable en vez de mover las carpetas de los consumidores.

Los consumidores ya usan Oracle 0.38.2 y Factory fija 0.38.1; como cada uno fija sus dependencias con `==`, Factory sube a 0.38.2.

## What changes

- **`"oracle": "medidas"` en `.factory/config.json`** dice dónde está el proyecto Oracle (una carpeta del proyecto, relativa a su raíz; por defecto, la raíz). Factory importa los requisitos ahí, los mide, los quita al abandonar, los busca y los lista en `donde`, y corre Oracle (importar, cobertura, juzgar) con ese proyecto.
- **`oracle-factory init --oracle medidas`** adopta un proyecto Oracle que ya existe: no crea `oracle.json`, `requisitos/` ni catálogos en la raíz, guarda la carpeta en la configuración y respeta el `tareas/` que haya.
- **`"confiar_escalares": true`** en la configuración hace que Factory corra Oracle con `--confiar-escalares`. Es una decisión del proyecto: ejecuta su `escalares.py` (Oracle lo aísla). Sin la clave, Factory no lo pasa.
- **Una configuración inválida se rechaza** con la causa: una ruta absoluta, que sale del proyecto o que no tiene `oracle.json`.
- **Factory fija `oracle-metalenguaje==0.38.2`.**

## Out of scope

- Mudar Jam y LyraGASP: es lo que sigue, en sus repositorios, después de publicar esta versión.
- Que los requisitos que esos proyectos ya tienen pasen por Factory: Brian decidió que queden como están.

## Human decisions

- Brian, 2026-10-15: Factory configura la carpeta (no se mueve `medidas/`) y los requisitos existentes quedan como están.
