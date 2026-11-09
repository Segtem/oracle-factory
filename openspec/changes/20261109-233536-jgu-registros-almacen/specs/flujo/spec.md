# Capability: flujo

## ADDED Requirements

### Requirement: conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto
Tipo: funcional
El sistema DEBE, con `conectar RUTA` desde una carpeta del producto, guardar en la configuración personal del usuario (`$XDG_CONFIG_HOME/oracle-factory/almacenes.json`, o `~/.config/oracle-factory/almacenes.json`) que el producto usa el almacén RUTA, con el directorio común de Git del producto como clave; DEBE rechazar con un mensaje, sin escribir nada, una RUTA que no exista, que no sea un repo Git, que contenga al producto o esté dentro de él, o una configuración personal ilegible; DEBE preparar la estructura de Factory en el almacén si le falta, sin tocar nunca el repo del producto; y DEBE ser idempotente (conectar dos veces al mismo almacén no cambia nada).

#### Scenario: conectar un almacén nuevo
- DADO un repo de producto limpio y un repo Git vacío como almacén
- CUANDO se corre `conectar ALMACEN`
- ENTONCES el producto queda conectado en la configuración personal, el almacén tiene la estructura de Factory y `git status` del producto sigue limpio

#### Scenario: una ruta que no sirve
- DADO una ruta inexistente, o una carpeta que no es un repo Git, o una carpeta dentro del producto, o una que lo contiene
- CUANDO se corre `conectar` con esa ruta
- ENTONCES falla con un mensaje claro y no cambia nada

#### Scenario: la configuración personal ilegible
- DADO un `almacenes.json` que no se puede leer
- CUANDO se corre `conectar ALMACEN`
- ENTONCES falla sin sobrescribirlo

#### Scenario: conectar dos veces
- DADO un producto ya conectado a ALMACEN
- CUANDO se corre `conectar ALMACEN` otra vez
- ENTONCES no cambia nada y lo dice

### Requirement: con_el_producto_conectado_los_comandos_usan_el_almacen
Tipo: funcional
El sistema DEBE, con el producto conectado, usar el almacén en todos los comandos sin `--registros`, corran desde cualquier subcarpeta del producto o desde cualquiera de sus worktrees, con el mismo comportamiento que `--registros ALMACEN` (etapa 1); `--registros` explícito DEBE mandar sobre la conexión; sin conexión DEBE comportarse exactamente como antes; y una configuración personal ilegible DEBE avisarse y tratarse como «no conectado» sin romper el comando.

#### Scenario: desde una subcarpeta y desde un worktree
- DADO un producto conectado y un worktree del mismo repo
- CUANDO se corre `listar` desde una subcarpeta del producto y desde el worktree
- ENTONCES los dos ven los cambios del almacén y no se crea ningún archivo de Factory en el producto

#### Scenario: la opción explícita manda
- DADO un producto conectado a ALMACEN y otro almacén OTRO
- CUANDO se corre un comando con `--registros OTRO`
- ENTONCES usa OTRO

#### Scenario: sin conexión
- DADO un proyecto Factory de los de hoy, sin conexión
- CUANDO se corre cualquier comando
- ENTONCES se comporta como siempre

### Requirement: conectar_sin_argumentos_y_desconectar
Tipo: funcional
El sistema DEBE, con `conectar` sin argumentos, decir a qué almacén está conectado el producto o que no lo está; DEBE, con `desconectar`, quitar la conexión del producto de la configuración personal sin tocar el almacén ni el producto (y decir que no estaba conectado si no lo estaba); y DEBE negar `conectar` y `desconectar` con `--agente` sin escribir nada, y hacer que el conductor los trate como decisiones de una persona.

#### Scenario: ver y quitar la conexión
- DADO un producto conectado
- CUANDO se corre `conectar` y después `desconectar`
- ENTONCES el primero dice el almacén y el segundo lo quita, dejando el almacén y el producto intactos

#### Scenario: un agente no conecta
- DADO el mismo producto
- CUANDO se corre `conectar ALMACEN` o `desconectar` con `--agente claude-code`
- ENTONCES se niega, no cambia nada, y `autopilot` lo clasifica como paso de persona

### Requirement: un_producto_con_su_propio_factory_conectado_se_niega
Tipo: funcional
El sistema DEBE negarse, con un mensaje que explique el conflicto y sin escribir nada, a correr un comando cuando el producto tiene su propia carpeta `.factory/` y además está conectado a un almacén (sin `--registros` explícito).

#### Scenario: los dos a la vez
- DADO un proyecto Factory de los de hoy que además se conectó a un almacén
- CUANDO se corre `estado`
- ENTONCES se niega con un mensaje que dice que hay que desconectar o migrar, y no cambia nada
