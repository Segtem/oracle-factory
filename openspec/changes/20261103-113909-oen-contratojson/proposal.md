# Pruebas de contrato entre la CLI y la extensión de VS Code

## Por qué

La extensión de VS Code no tiene lógica propia sobre el proyecto: lee cuatro salidas JSON de la CLI (`resumen --json`, `estado ID --json`, `donde ID --json` y `tablero --json`) y las muestra. Cada cambio nuevo de Factory agrega claves a esos JSON —esta tanda sumó `bucle_de_revision`, `cambio_grande` y `camino` al de `estado`—, y hoy nada protege la unión entre las dos puntas: si la CLI renombra o quita una clave que la extensión lee, la extensión se rompe sin que ninguna prueba lo note (las pruebas de la extensión usan la CLI de verdad, pero sólo miran lo que muestran en los casos que cubren, no qué claves leen). Y al revés: si la extensión empieza a leer una clave nueva, nadie en la CLI se entera de que ahora tiene que mantenerla. Es la cuarta idea del informe de Shift Left que estudiamos: pruebas de contrato de lo que consume un cliente.

## Qué cambia

- Un archivo `editores/vscode/contrato.json` declara, por comando, qué claves lee la extensión y con qué tipos (`string`, `number`, `boolean`, `null`, `array`, `object`); las que sólo existen en algunos estados llevan `null` entre sus tipos o se marcan como opcionales.
- Una prueba corre el modelo y el tablero de la extensión en node sobre la salida JSON real de la CLI, en proyectos temporales con cambios en varios estados, y registra cada clave que la extensión lee. Falla, nombrando comando y clave, si la extensión lee algo que el contrato no declara.
- Otra prueba comprueba que la CLI entrega cada clave declarada, con un tipo permitido, en esos mismos proyectos. Falla, nombrando comando, clave, tipo esperado y tipo encontrado, si la CLI renombra, quita o cambia el tipo de una clave declarada.
- Un cambio nuevo de la CLI que sólo agrega claves no rompe nada: el contrato no prohíbe claves de más.
- `docs/` explica cómo actualizar el contrato cuando la extensión pasa a leer algo nuevo.

## Fuera de alcance

- Cambiar la extensión, el formato de los JSON o la versión del paquete de la extensión.
- Lo que la extensión recibe por Live Share ni la salida de texto de `mensaje`, `por-que` y `preguntar`: no son JSON de la CLI.
- Declarar el contrato para clientes que todavía no existen.
- Exigir que el contrato no tenga claves que la extensión ya no lee: con los estados de las pruebas no se cubren todas las ramas, y un falso aviso costaría más que una clave de sobra.

## Decisiones humanas

- Que el contrato viva en `editores/vscode/contrato.json` y que sus fallas rompan la suite (no sean un aviso).
- Que no se prohíban claves de más en el JSON de la CLI.
