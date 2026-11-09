# El registro tolera eventos que no son objetos

## Por qué

Si el registro de un cambio (`factory.json`) trae en `eventos` algo que no es un objeto (un número, un texto, `null`), `estado` falla con un `AttributeError` (en `aviso_revision`, `quien_del_cambio` y `commits_del_cambio`), y lo mismo pasa con cualquier otro lector que haga `e.get(...)`. Lo vio codex al revisar `frenos` y quedó anotado como seguimiento. Un registro roto por una mala unión de ramas o una edición a mano no debería dejar a nadie sin poder ver el estado de su cambio.

## Qué cambia

`cli.leer`, por donde pasan `estado`, `estado --json`, `kb`, `tablero`, `log` y el resto de los lectores, ignora los eventos que no son objetos y avisa una vez por la salida de error (cuántos ignoró y de qué cambio). Un `eventos` que no es una lista se trata como vacío, con el mismo aviso. No toca el archivo al leer, y un registro sano no cambia en nada: sin aviso, mismos datos.

## Fuera de alcance

Reparar el registro: los eventos inválidos no se reescriben. Validar los campos de los eventos que sí son objetos. Cualquier lector que no pase por `cli.leer`.

## Decisiones humanas

Una para Brian: cuando otro comando guarda el registro (por ejemplo `mensaje`), los eventos que no eran objetos **no se vuelven a escribir**, es decir, desaparecen del archivo. Es lo más simple y evita arrastrar basura, pero es perder lo que había. La alternativa es guardarlos aparte para que no se pierdan, a cambio de más código.
