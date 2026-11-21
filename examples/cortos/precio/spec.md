# Capability: precio

## ADDED Requirements

### Requirement: descuento limitado
Tipo: funcional
El total DEBE calcularse en centavos enteros, truncar hacia abajo la rebaja y rechazar descuentos fuera de 0 a 50 por ciento.

#### Scenario: descuento 50 y 51
- DADO un precio de 1001 centavos
- CUANDO se aplica 50 por ciento o se intenta 51 por ciento
- ENTONCES el total es 501 centavos o se rechaza el descuento, respectivamente
