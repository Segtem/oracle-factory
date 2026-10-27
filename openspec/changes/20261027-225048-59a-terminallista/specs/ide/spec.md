# Capability: ide

## ADDED Requirements

### Requirement: la_terminal_nueva_espera_a_estar_lista
Tipo: funcional
El sistema DEBE escribir un comando en una terminal «Factory» recién creada sólo cuando la terminal avise que su shell está listo o cuando pase el plazo configurado, lo que ocurra primero, y nunca antes.

#### Scenario: la terminal avisa que está lista
- DADO que no hay una terminal «Factory»
- CUANDO el tablero pide escribir un comando y la terminal nueva avisa que su shell está listo
- ENTONCES el comando se escribe después del aviso y no antes

#### Scenario: la terminal nunca avisa
- DADO que no hay una terminal «Factory» y el plazo es de 3 segundos
- CUANDO el tablero pide escribir un comando y la terminal no avisa
- ENTONCES el comando se escribe al cumplirse el plazo y no antes

#### Scenario: un plazo de cero
- DADO el plazo configurado en 0
- CUANDO el tablero pide escribir un comando
- ENTONCES se escribe de inmediato

### Requirement: una_terminal_lista_recibe_el_comando_enseguida
Tipo: funcional
El sistema DEBE escribir el comando sin esperar cuando la terminal «Factory» ya existía o ya informa su integración de shell.

#### Scenario: la terminal ya existía
- DADO una terminal «Factory» abierta
- CUANDO el tablero pide escribir un comando
- ENTONCES se escribe sin esperar y no se crea otra terminal

#### Scenario: la terminal nueva ya informa su integración
- DADO una terminal nueva que ya informa su integración de shell
- CUANDO el tablero pide escribir un comando
- ENTONCES se escribe sin esperar

### Requirement: los_comandos_seguidos_se_escriben_en_orden_y_una_vez
Tipo: funcional
El sistema DEBE escribir, en el orden en que se pidieron y una sola vez cada uno, los comandos pedidos mientras la terminal nueva arranca.

#### Scenario: dos comandos mientras arranca
- DADO que no hay una terminal «Factory»
- CUANDO se piden dos comandos antes de que la terminal esté lista
- ENTONCES, ya lista, se escriben los dos, en ese orden, cada uno una vez, en una sola terminal

### Requirement: queda_constancia_en_la_salida
Tipo: funcional
El sistema DEBE dejar en la salida «Oracle Factory» cuánto se esperó y por qué se escribió el comando, sin incluir el texto del comando.

#### Scenario: la constancia
- DADO un comando escrito en una terminal nueva
- CUANDO se mira la salida «Oracle Factory»
- ENTONCES hay una línea con el motivo (lista, plazo o ya existía) y los milisegundos esperados, y no contiene el comando
