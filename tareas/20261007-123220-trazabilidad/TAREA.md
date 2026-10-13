# Trazabilidad por candidato: requisito, casos y líneas de código

- ESTADO: CERRADA
- PRIORIDAD: 12
- ETIQUETAS: revision, ide


## Objetivo

Correr los casos de contrato de cada requisito con cobertura por prueba (coverage.py, contextos dinámicos) y producir trazabilidad.json en la carpeta del candidato: requisito → medidas → casos → líneas ejecutadas; cruzado con el diff del candidato, qué líneas cambiadas respaldan cada requisito y cuáles no toca ningún caso. Vuelve verificable «archivos revisados» (riesgo G-03). Límite a declarar: cobertura de ejecución no es corrección.

Parte del plan de revisión en el IDE (tarea 20261005-112955-revision-ide, Brian 2026-10-07): unir requisitos, medidas, veredicto y código para que una persona revise el código hecho por IA por promesa, no por archivo. Las decisiones siguen siendo humanas y pasan por la terminal.

### Nota (2026-10-13 22:08:20 UTC)

Hecha por el cambio 20261013-180751-trazabilidad (integrado en 33a7077): oracle_factory.trazabilidad.trazar (biblioteca estándar, traza encadenada, hilos) deja trazabilidad.json en la evidencia, y oracle-factory trazabilidad ID [--json] [--base] cruza los casos con el diff del candidato: por requisito, sin respaldo, corren al importar, no rastreables y borrados. Cinco vueltas de revisión; la 5 dejó un riesgo aceptado (guards __main__ compuestos).
