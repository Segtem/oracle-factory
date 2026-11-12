# Capability: flujo

## ADDED Requirements

### Requirement: conectar_dice_la_conexion_como_json
Tipo: funcional
El sistema DEBE, con `conectar --json` sin ruta desde una carpeta del producto, imprimir un objeto JSON con `conectado` (verdadero o falso), `almacen` (la ruta del almacén, o `null`) y `producto` (la raíz del repo del producto, o `null` si no es un repo Git), sin escribir nada; y DEBE rechazar `--json` junto con una ruta o URL.

#### Scenario: conectado y sin conectar
- DADO un producto conectado a un almacén y otro sin conectar
- CUANDO se corre `conectar --json` en cada uno
- ENTONCES el primero dice `conectado: true` con la ruta del almacén y el segundo `conectado: false` con `almacen: null`, y nada cambia en el disco

### Requirement: la_extension_reconoce_y_vigila_un_producto_conectado
Tipo: funcional
El sistema DEBE hacer que la extensión de VS Code se active también con `onStartupFinished` y trate como proyecto de Factory una carpeta con `.factory/` o un producto conectado a un almacén (según `conectar --json`): con un producto conectado DEBE mostrar los cambios y sus pasos como con `.factory/` en la carpeta, leer `destinos.json` del almacén y vigilar los `factory.json` de los cambios y los registros de despliegue en el almacén; sin `.factory/` ni conexión DEBE seguir diciendo que la carpeta no es un proyecto de Factory.

#### Scenario: un producto conectado
- DADO un producto conectado a un almacén con un cambio abierto
- CUANDO la extensión arma su vista sobre la carpeta del producto
- ENTONCES muestra el cambio y su próximo paso, y vigila los registros en el almacén

#### Scenario: una carpeta sin Factory
- DADO una carpeta sin `.factory/` y sin conexión
- CUANDO la extensión arma su vista
- ENTONCES dice que la carpeta no es un proyecto de Factory, como hoy

#### Scenario: la activación
- DADO el `package.json` de la extensión
- CUANDO se miran sus eventos de activación
- ENTONCES incluye `onStartupFinished` además de `workspaceContains:.factory`
