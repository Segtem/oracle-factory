# Design

- La huella es el SHA-256 de los bytes del archivo de cada medida en el catálogo efectivo de Oracle (`entradas[id].ruta`), guardada como `catalogos: {id: sha256}` junto al `sha256` del `.requisito`, en la decisión (`medidas[rid]`) y en la propuesta (`medidas_pendientes[rid]`).
- Una decisión o propuesta sin `catalogos` (anterior a este cambio) no se compara, como hoy una sin `sha256`.
- Cualquier cambio en el archivo cuenta, también uno de formato o de un comentario: es el lado seguro y se resuelve volviendo a decidir.
- Una medida que ya no está en el catálogo efectivo también cuenta como cambio.
