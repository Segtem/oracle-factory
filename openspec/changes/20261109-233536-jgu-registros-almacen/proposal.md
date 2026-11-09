# Registros fuera del repo del producto, etapa 2: el almacén y `conectar`

## Por qué

La etapa 1 separó las dos raíces, pero obliga a pasar `--registros RUTA` en cada comando. Para que un equipo use Factory sin ensuciar el repo del producto, cada persona tiene que conectar una vez el producto con su almacén de registros y después trabajar como siempre. Brian eligió (2026-11-09): el almacén es un repo Git propio del equipo, y cada integrante lo conecta con `oracle-factory conectar` (configuración personal del usuario, nunca en el repo del producto).

## Qué cambia

- `oracle-factory conectar RUTA` (desde cualquier carpeta del producto): guarda en la configuración personal del usuario (`$XDG_CONFIG_HOME/oracle-factory/almacenes.json`, o `~/.config/oracle-factory/almacenes.json`) que ese producto usa el almacén RUTA. La clave es el directorio común de Git del producto (`git rev-parse --git-common-dir`), así todos los worktrees del mismo repo comparten el almacén. RUTA tiene que ser un repo Git, no puede contener al producto ni estar dentro de él, y si todavía no tiene la estructura de Factory, `conectar` la prepara (como `init --registros`).
- Con el producto conectado, cualquier comando sin `--registros` usa el almacén, corra donde corra dentro del producto o de sus worktrees. `--registros` explícito manda sobre la conexión.
- `conectar` sin argumentos dice a qué almacén está conectado el producto (o que no lo está); `desconectar` quita la conexión sin tocar el almacén ni el producto.
- `conectar` y `desconectar` son sólo de una persona (con `--agente` se niegan).
- Si el producto tiene su propia carpeta `.factory/` y además está conectado, los comandos se niegan con un mensaje que lo explica (migrar es la etapa 6): no se adivina dónde escribir.
- Una configuración personal ilegible no rompe nada (se avisa y se trata como «no conectado»), pero `conectar` y `desconectar` no la sobrescriben.

## Fuera de alcance

- Clonar el almacén desde una URL, subirlo y bajarlo, commitear dentro de él tras cada decisión y el bloqueo entre personas (etapa 4).
- El candidato y la huella con dos fuentes (etapa 3); la guía de agentes, la skill y la extensión de VS Code (etapa 5); la migración (etapa 6).

## Decisiones humanas

Tomé estas por defecto y se confirman al aprobar la spec: la clave de la conexión es el directorio común de Git; `conectar` y `desconectar` no los puede correr un agente; un producto con `.factory/` propio conectado a un almacén es un error y no una preferencia.
