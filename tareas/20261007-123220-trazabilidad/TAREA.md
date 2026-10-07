# Trazabilidad por candidato: requisito, casos y líneas de código

- ESTADO: ABIERTA
- PRIORIDAD: 12
- ETIQUETAS: revision, ide


## Objetivo

Correr los casos de contrato de cada requisito con cobertura por prueba (coverage.py, contextos dinámicos) y producir trazabilidad.json en la carpeta del candidato: requisito → medidas → casos → líneas ejecutadas; cruzado con el diff del candidato, qué líneas cambiadas respaldan cada requisito y cuáles no toca ningún caso. Vuelve verificable «archivos revisados» (riesgo G-03). Límite a declarar: cobertura de ejecución no es corrección.

Parte del plan de revisión en el IDE (tarea 20261005-112955-revision-ide, Brian 2026-10-07): unir requisitos, medidas, veredicto y código para que una persona revise el código hecho por IA por promesa, no por archivo. Las decisiones siguen siendo humanas y pasan por la terminal.
