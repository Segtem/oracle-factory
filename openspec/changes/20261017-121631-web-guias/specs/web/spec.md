# Capability: web

## ADDED Requirements

### Requirement: las guías tienen su escena y su elenco
Tipo: funcional
Cada guía (desde cero, modos y en equipo) SHALL abrir con una escena de pixel art propia que se anima al entrar en pantalla, y SHALL mostrar personajes con nombre y globito en al menos tres de sus secciones. Con movimiento reducido las escenas SHALL NOT animarse y SHALL mostrar su estado final. Las guías SHALL funcionar sin red y SHALL NOT desbordar horizontalmente entre 320 y 1440 px.

#### Scenario: recorrer cada guía
- GIVEN cada una de las tres guías abierta en Chromium sin red, a 1440 px
- WHEN se baja hasta el final
- THEN su escena se anima al entrar, al menos tres secciones tienen un personaje con nombre y globito, y no hay pedidos a la red ni errores

#### Scenario: movimiento reducido y pantalla chica
- GIVEN cada guía con movimiento reducido, a 320 px
- WHEN se baja hasta el final
- THEN ninguna escena se anima, todas muestran su estado final y nada desborda horizontalmente

### Requirement: el texto y los comandos de las guías no cambian
Tipo: funcional
Lo que las guías dicen y los comandos que dan SHALL ser los mismos que antes del cambio; los personajes y las escenas SHALL agregarse sin reemplazar ni mover texto.

#### Scenario: comparar con la versión anterior
- GIVEN cada guía antes y después del cambio
- WHEN se compara su texto y sus bloques de código, sin los personajes y escenas agregados
- THEN son idénticos
