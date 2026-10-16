# Bloqueo del registro: las escrituras de factory.json no se pisan entre procesos

- ESTADO: CERRADA
- PRIORIDAD: 30
- ETIQUETAS: flujo, colaboracion

### Nota (2026-10-16 16:11:46 UTC)

De la revisión de revisar-cancelada (codex CXL2-1, 2026-10-16): toda escritura del registro compara con lo leído y reemplaza (escribir_atomico con esperado) sin bloqueo, así que otro proceso puede escribir entre la comparación y el os.replace y perderse su cambio (por ejemplo una revision_registrada pisada por una revision_cancelada). Propuesta: un bloqueo por cambio con fcntl.flock, como turno_de_pedidos, que tomen guardar y las escrituras con esperado; el sistema lo suelta si el proceso muere.

### Nota (2026-10-16 20:01:24 UTC)

Hecho en el cambio 20261016-175720-bloqueo-registro (merge 5a3971f): guardar compara con lo último que el proceso leyó o escribió del registro y escribir_atomico compara y reemplaza con flock sobre la carpeta; pruebas bl1–bl3 con un segundo proceso real; tres vueltas de codex y agy, la tercera sin hallazgos.
