# Partir cli.py en módulos para alejarlo del límite de Oracle Clue

## Why

`oracle_factory/cli.py` mide 253.965 bytes y Oracle Clue no acepta archivos de más de 256.000 bytes: al agregar la CLI de la procedencia el archivo pasó del límite y la revisión independiente no pudo ni empezar hasta que se sacó código de ahí. Hoy cualquier mejora mediana de la CLI vuelve a chocar con ese tope, y una revisión que no puede empaquetar el producto no se puede pedir. No hay una función enorme: son 246 definiciones juntas, así que el remedio es repartirlas por tema.

## What changes

- Tres grupos de `cli.py` pasan a módulos propios, sin cambiar lo que hacen: la construcción del parser de argumentos (`parser.py`), el flujo de pedir y revisar (`flujo_revision.py`) y el flujo de elegir y confirmar medidas (`flujo_medidas.py`).
- `oracle_factory.cli` sigue exportando todos los nombres que exportaba, con las mismas firmas, y el comando `oracle-factory` se comporta igual.
- Un cambio hecho a un valor de `cli` (por ejemplo, la raíz del proyecto en las pruebas) sigue valiendo para lo movido: el código movido lee `cli` en el momento de usarlo, no una copia.
- `cli.py` queda por debajo de 160.000 bytes, y una prueba impide que cualquier archivo fuente del paquete pase de 200.000, con margen respecto del tope de Clue.
- Se guardan, antes de mover nada, la ayuda de cada subcomando y la lista de nombres con sus firmas, y se comprueba contra ellas.

## Out of scope

- Cambiar el comportamiento, los mensajes o las opciones de cualquier comando.
- Mover clases, o dividir los demás módulos del paquete.
- Reordenar o renombrar funciones, o reescribir su lógica.

## Human decisions

- El tope de 160.000 bytes para `cli.py` y 200.000 para el resto (se proponen para dejar margen amplio bajo los 256.000 de Clue).
- Los tres grupos a mover: parser, pedir y revisar, y medidas. Se puede mover más si querés más margen, a costa de un diff más grande.
