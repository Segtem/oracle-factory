# Capability: web

## ADDED Requirements

### Requirement: la portada es una fábrica viva
Tipo: funcional
La portada SHALL mostrar en pixel art una escena por sección y un sprite por herramienta, y SHALL presentar a la persona, el agente, los revisores, Oracle y Clue como personajes con nombre que dicen en globitos qué hace cada uno. Las escenas SHALL animarse al entrar en pantalla; con movimiento reducido SHALL NOT animarse y SHALL mostrar su estado final. La página SHALL funcionar sin red ni recursos externos y SHALL NOT desbordar horizontalmente entre 320 y 1440 px.

#### Scenario: recorrer la portada
- GIVEN la portada abierta en Chromium sin red, a 1440 px
- WHEN se baja hasta el final
- THEN cada sección tiene su escena de pixel art, que se anima al entrar; aparecen los personajes con su nombre y su globito; y no hay pedidos a la red ni errores de la página

#### Scenario: movimiento reducido y pantalla chica
- GIVEN la portada con movimiento reducido, a 320 px
- WHEN se baja hasta el final
- THEN ninguna escena se anima, todas muestran su estado final y nada desborda horizontalmente

### Requirement: el minijuego enseña las decisiones de verdad
Tipo: funcional
La portada SHALL tener un minijuego en el que quien visita decide como persona sobre un pedido que el agente construye, con las reglas de la CLI. Con un hallazgo medio o más abierto, «Aprobar» SHALL NOT estar disponible y SHALL decir por qué. Aceptar un riesgo SHALL registrar su motivo. Unas medidas sin acordar SHALL dejar el requisito sin juicio. Al terminar, el juego SHALL mostrar el registro de quién decidió cada cosa y por qué Oracle dio verde, rojo o sin juicio. SHALL jugarse entero con teclado.

#### Scenario: una partida que cierra en verde
- GIVEN el minijuego al empezar
- WHEN se acepta el alcance, se acuerdan las medidas, se acepta el riesgo del hallazgo con su motivo y se aprueba
- THEN el registro muestra cada decisión a nombre de la persona, el riesgo aceptado con su motivo, y Oracle en verde

#### Scenario: aprobar con un hallazgo abierto, y medidas sin acordar
- GIVEN el minijuego con un hallazgo medio abierto, o con las medidas sin acordar
- WHEN se intenta aprobar, o se llega al juicio
- THEN aprobar no está disponible y dice por qué, o el requisito queda sin juicio y el final lo explica

#### Scenario: jugar sólo con teclado
- GIVEN la portada en Chromium
- WHEN se juega una partida entera con Tab, Enter y las flechas
- THEN se llega al registro final sin usar el mouse

### Requirement: los easter eggs no tapan nada
Tipo: funcional
La portada SHALL esconder al menos tres easter eggs (la chimenea, el gato de la fábrica y el código Konami). Activarlos SHALL NOT tapar texto, cambiar lo que dice la página ni romper el teclado, y con movimiento reducido SHALL NOT animar.

#### Scenario: encontrar los tres
- GIVEN la portada en Chromium
- WHEN se hace clic en la chimenea, en el gato y se teclea el código Konami
- THEN cada uno responde, el texto de la página sigue igual y visible, y el foco sigue donde estaba
