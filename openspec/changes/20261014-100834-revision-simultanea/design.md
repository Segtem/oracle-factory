# Design

- Un bloqueo por cambio con `fcntl.flock` sobre `.factory/local/locks/<id>.pedir.lock`, de espera (no falla como `bloqueo_medidas`): el segundo pedido espera unos segundos a que el primero termine lo corto. El kernel lo suelta cuando el proceso termina, así que un pedido interrumpido no deja nada que retirar.
- Dentro del bloqueo: el checkout, el número del paquete y `oracle-clue preparar` (que crea el archivo con ese número), y al final releer el registro, agregar el evento y guardarlo. Fuera: el revisor y la validación.
