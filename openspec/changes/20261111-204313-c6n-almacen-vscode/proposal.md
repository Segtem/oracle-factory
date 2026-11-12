# Registros fuera del repo del producto, etapa 5b: la extensión de VS Code reconoce un producto conectado a un almacén

## Por qué

La extensión de VS Code (`editores/vscode/`) se activa con `workspaceContains:.factory` y, antes de mostrar nada, comprueba que la carpeta abierta tenga `.factory/`. Un producto conectado a un almacén aparte (etapas 1–5a) no tiene `.factory/`: la extensión dice «Esta carpeta no es un proyecto de Factory» aunque el CLI, corrido desde esa misma carpeta, encuentra el almacén y funciona. Tampoco se entera de lo que cambia, porque vigila `.factory/` dentro de la carpeta abierta.

## Qué cambia

- `oracle-factory conectar --json` (sin ruta): dice, como JSON, si el producto está conectado y a qué almacén (`{"conectado", "almacen", "producto"}`); es de sólo lectura.
- La extensión se activa también al terminar de arrancar VS Code (`onStartupFinished`), y reconoce como proyecto de Factory una carpeta con `.factory/` o un producto conectado (lo pregunta con `conectar --json`).
- Con un producto conectado, la vista, los destinos y los comandos funcionan como con `.factory/` en la carpeta: el CLI ya resuelve el almacén solo; la extensión lee `destinos.json` del almacén y vigila los registros (`factory.json` de los cambios y de los despliegues) en el almacén, no en la carpeta abierta.
- Sin `.factory/` ni conexión, la extensión dice lo mismo que hoy.

## Fuera de alcance

- Empaquetar y publicar una versión nueva del `.vsix` (es una publicación: la decide una persona).
- La migración (etapa 6).

## Decisiones humanas

Ninguna nueva.
