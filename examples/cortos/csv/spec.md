# Capability: csv

## ADDED Requirements

### Requirement: cantidades válidas
Tipo: funcional
El lector DEBE sumar filas sin encabezado con dos campos, código no vacío y cantidad entera positiva, y rechazar la primera fila inválida.

#### Scenario: fila negativa o incompleta
- DADAS filas A,3 y B,4, o una variante B,-4 o B sin cantidad
- CUANDO se lee el CSV
- ENTONCES el total es 7 o se informa un error, respectivamente
