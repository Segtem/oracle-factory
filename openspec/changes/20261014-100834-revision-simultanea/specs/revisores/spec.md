# Capability: revisores

## ADDED Requirements

### Requirement: pedidos de revisión simultáneos sobre el mismo candidato
Tipo: funcional
Dos `pedir-revision` lanzados a la vez sobre el mismo candidato SHALL terminar los dos: el checkout de revisión se crea una sola vez, cada pedido usa un paquete y un número propios, y el registro del cambio guarda el evento de cada uno.

#### Scenario: dos revisores distintos a la vez
- GIVEN un candidato sin checkout de revisión y dos revisores configurados
- WHEN se piden las dos revisiones al mismo tiempo
- THEN las dos guardan su informe y el registro tiene los dos eventos

#### Scenario: el mismo revisor dos veces a la vez
- GIVEN un revisor configurado
- WHEN se le piden dos revisiones del mismo candidato al mismo tiempo
- THEN quedan dos paquetes y dos informes con números distintos

### Requirement: un pedido interrumpido no traba los siguientes
Tipo: funcional
El turno entre pedidos SHALL soltarse cuando el proceso que lo tiene termina, de cualquier forma: un pedido interrumpido no SHALL dejar nada que haya que retirar a mano.

#### Scenario: un bloqueo de un pedido que murió
- GIVEN el archivo de bloqueo de un pedido anterior que se cortó
- WHEN se pide una revisión
- THEN el pedido termina sin esperar ni pedir que se borre el bloqueo
