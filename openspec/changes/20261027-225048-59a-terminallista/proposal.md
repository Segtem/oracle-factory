# Esperar a que la terminal de Factory esté lista antes de escribir un comando

## Why

En el piloto, el botón «Escribir en la terminal» del tablero mostró un `^C` tres veces, siempre en el primer envío, seguido de la línea de activación del entorno (`source …/activate`). Brian lo describió así: «me sale ^C … source …/activate». La hipótesis, que sólo se confirma en un VS Code real: la extensión crea la terminal «Factory» y escribe el comando en el mismo instante, antes de que el shell termine de arrancar; VS Code (o su extensión de Python) activa el entorno después, y ese paso limpia la línea con un `^C`, así que el comando escrito se pierde o sale mezclado.

## What changes

- Cuando un comando va a una terminal «Factory» que acaba de crearse, la extensión espera a que la terminal avise que su shell está listo (integración de shell) o a que pase un plazo, lo que ocurra primero, y recién entonces escribe el comando.
- El plazo es de 3 segundos por defecto y se cambia con `factory.esperaTerminalMs` (0 escribe de inmediato).
- Una terminal «Factory» que ya existía, o que ya informa su integración de shell, recibe el comando enseguida.
- Varios comandos pedidos mientras la terminal arranca se escriben todos, en orden y una sola vez.
- La salida «Oracle Factory» deja constancia de cuánto se esperó y por qué se escribió (terminal lista, plazo o ya existía), sin el texto del comando.

## Out of scope

- Ejecutar el comando: se sigue escribiendo sin Enter.
- Cambiar la configuración de Python o de VS Code del usuario.
- Garantizar que el `^C` desaparezca en todos los entornos: se confirma mirando el botón en el VS Code de Brian.

## Human decisions

- El plazo por defecto (propongo 3 segundos: un shell lento tarda menos, y esperar de más sólo retrasa la primera vez).
- Si la constancia en la salida está bien así (sólo cuánto y por qué, sin el comando).
