# Capability: flujo

## ADDED Requirements

### Requirement: leer_ignora_los_eventos_que_no_son_objetos
Tipo: funcional
El sistema DEBE ignorar, al leer el registro de un cambio, los elementos de `eventos` que no son objetos y tratar un `eventos` que no es una lista como vacío; DEBE avisar una vez por cambio, por la salida de error, cuántos ignoró; NO DEBE tocar el archivo al leer; y para un registro sano NO DEBE cambiar nada ni avisar.

#### Scenario: un evento que no es un objeto
- DADO un registro cuyos `eventos` traen un número, un texto y `null` además de los eventos de siempre
- CUANDO se lee el cambio
- ENTONCES los datos traen solo los eventos que son objetos, y sale un aviso con la cantidad ignorada

#### Scenario: eventos que no es una lista
- DADO un registro con `eventos` en un texto o un número
- CUANDO se lee el cambio
- ENTONCES `eventos` es una lista vacía y sale el aviso

#### Scenario: un registro sano
- DADO un registro sin eventos raros
- CUANDO se lee el cambio
- ENTONCES los datos son los mismos que antes y no sale ningún aviso

#### Scenario: leer no escribe
- DADO un registro con un evento raro
- CUANDO se lee el cambio
- ENTONCES el archivo queda con los mismos bytes

### Requirement: los_comandos_de_lectura_siguen_funcionando_con_eventos_raros
Tipo: funcional
El sistema DEBE seguir mostrando `estado`, `estado --json` y el conocimiento generado (`kb`) de un cambio cuyo registro tiene eventos que no son objetos, con los demás eventos intactos, sin fallar.

#### Scenario: estado
- DADO un cambio con un evento que no es un objeto
- CUANDO se pide `estado` y `estado --json`
- ENTONCES muestran el estado del cambio con sus eventos válidos, sin error

#### Scenario: kb
- DADO un proyecto con un cambio cuyo registro tiene un evento que no es un objeto
- CUANDO se genera `kb`
- ENTONCES termina sin error y la nota del cambio refleja sus eventos válidos
