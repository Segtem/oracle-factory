# Decisiones de implementación

El ejemplo se planifica y copia antes de crear la tarea; conflictos se detectan antes de esa creación. Una falla de E/S informa los destinos conservados y, si ya se creó la tarea, su ID real. No se prometen transacciones entre tracker, documentos y ejemplo.

Oracle publicado valida los requisitos y el catálogo efectivo. La asociación cambia solamente medido_por/sin_medir. Se conservan límites salvo elección explícita. Se comparan entradas y se usa bloqueo entre operaciones medir; editores externos no participan del bloqueo. Primero se invalida evidencia anterior; el reemplazo del requisito es atómico, sin prometer atomicidad entre archivos.

tools/verify_contracts.py ejecuta casos reales y publica hechos de los nombres enumerados. Las medidas cuentan resultados; su pertinencia, identidad y suficiencia se revisan en el sensor. El alcance es Linux/casos seleccionados: no equivale a revisión humana, piloto de principiante ni prueba de otras plataformas.
