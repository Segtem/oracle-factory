# Capability: flujo

## ADDED Requirements

### Requirement: con_almacen_cada_comando_que_escribe_deja_su_commit
Tipo: funcional
El sistema DEBE, con almacén aparte, hacer un commit en el repo del almacén al terminar cada comando que cambió archivos del almacén, con exactamente los archivos que ese comando creó, modificó o borró (los que ya estaban cambiados antes del comando NO DEBEN entrar), y con un mensaje que nombre el comando y el cambio y que termine con las líneas `Cambio: ID` (cuando el comando es de un cambio), `Comando: NOMBRE` y `Actor: NOMBRE (persona|agente)`; un comando que no cambió nada del almacén NO DEBE hacer commit; y sin almacén aparte NO DEBE hacer ningún commit.

#### Scenario: un comando que escribe
- DADO un producto conectado a un almacén
- CUANDO un agente corre `nuevo` y después `mensaje` sobre ese cambio
- ENTONCES el almacén tiene un commit por cada comando, con sus archivos y con `Cambio`, `Comando` y `Actor: claude-code (agente)` en el mensaje, y `git status` del almacén queda limpio

#### Scenario: lo que ya estaba cambiado no entra
- DADO un archivo del almacén modificado a mano antes de un comando
- CUANDO se corre un comando que escribe otros archivos
- ENTONCES el commit no incluye ese archivo y sigue modificado sin commitear

#### Scenario: un comando que sólo lee
- DADO el mismo almacén
- CUANDO se corren `estado` y `listar`
- ENTONCES no se crea ningún commit

#### Scenario: sin almacén aparte
- DADO un proyecto Factory de los de hoy
- CUANDO se corre un comando que escribe
- ENTONCES no se crea ningún commit

### Requirement: el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar
Tipo: funcional
El sistema DEBE hacer el commit del almacén con la identidad de Git que ya está configurada, sin escribir ninguna configuración de Git en ningún repositorio y sin subir nada al remoto; y si el commit no se puede hacer (sin identidad de Git, un hook que lo rechaza u otro error de Git), el comando NO DEBE fallar por eso: DEBE avisar qué pasó y dejar los registros escritos en el disco.

#### Scenario: sin identidad de Git
- DADO un almacén sin identidad de Git configurada
- CUANDO se corre un comando que escribe
- ENTONCES el comando termina bien, avisa que no pudo commitear y por qué, los archivos quedan en el disco, y la configuración de Git del almacén no cambió

#### Scenario: un hook que rechaza
- DADO un almacén con un hook que rechaza los commits
- CUANDO se corre un comando que escribe
- ENTONCES el comando termina bien y avisa del rechazo

#### Scenario: no sube nada
- DADO un almacén con un remoto
- CUANDO se corre un comando que escribe
- ENTONCES el remoto no recibe nada
