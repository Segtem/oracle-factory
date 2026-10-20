# Capability: ide

## ADDED Requirements

### Requirement: el tablero muestra quién está en la sesión
Tipo: funcional
Cuando hay una sesión de Live Share, el tablero SHALL mostrar quién está conectado (la propia persona y las demás) con su rol de anfitrión o invitado, y SHALL actualizarse cuando alguien entra o sale. Sin la extensión de Live Share, o sin sesión, el tablero SHALL funcionar como sin esta capacidad y decirlo en una línea.

#### Scenario: una sesión con un invitado que entra y sale
- GIVEN el tablero abierto por la persona anfitriona de una sesión de Live Share
- WHEN un invitado entra a la sesión y después sale
- THEN el tablero muestra a los dos con su rol mientras el invitado está, y sólo a la anfitriona cuando se fue

#### Scenario: sin Live Share
- GIVEN VS Code sin la extensión de Live Share
- WHEN se abre el tablero
- THEN se ve como antes, con una línea que dice que no hay sesión de Live Share

### Requirement: el invitado ve el tablero de quien comparte
Tipo: funcional
En una sesión de Live Share, el tablero del anfitrión SHALL publicarse a los invitados: un invitado SHALL ver el mismo tablero aunque no tenga Factory instalado, y SHALL verlo rehecho cuando cambia un registro del anfitrión. Sus enlaces SHALL abrir los archivos compartidos, y el botón de un comando SHALL pedirle al anfitrión que lo escriba en su terminal «Factory» sin ejecutarlo, con la misma validación que el panel local. El tablero SHALL NOT tomar decisiones.

#### Scenario: un invitado sin Factory
- GIVEN una sesión de Live Share con un invitado que no tiene oracle-factory
- WHEN el invitado abre el tablero, cambia un registro del anfitrión y el invitado elige un hallazgo y un comando
- THEN ve el tablero del anfitrión, lo ve rehecho, se abre el archivo compartido en su línea y el comando aparece sin Enter en la terminal «Factory» del anfitrión

### Requirement: el chat queda en el cambio
Tipo: funcional
`oracle-factory mensaje ID "texto"` SHALL guardar el mensaje en el registro del cambio con su autor (una persona desde su terminal o un agente con `--agente`), y SHALL negarse sin terminal ni `--agente` salvo que lo envíe la extensión por Live Share con el nombre que da Live Share. En una sesión, el tablero de cada cambio SHALL tener un chat: un mensaje SHALL llegar a todos los conectados, y el anfitrión SHALL guardarlo en el registro. Los mensajes SHALL verse en la línea de tiempo del cambio y SHALL NOT contar como decisiones.

#### Scenario: un mensaje desde la terminal y uno desde el chat
- GIVEN un cambio abierto y una sesión de Live Share con un invitado
- WHEN una persona corre oracle-factory mensaje ID "hola" y el invitado escribe «revisá el hook» en el chat del cambio
- THEN el registro tiene los dos mensajes con su autor, el del invitado con su nombre de Live Share, los dos se ven en el tablero de los dos, y las métricas de decisiones no cambian

#### Scenario: un mensaje sin autor
- GIVEN un cambio abierto
- WHEN alguien corre oracle-factory mensaje ID "x" sin terminal ni --agente
- THEN se niega y el registro no cambia
