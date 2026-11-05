# Capability: web

## ADDED Requirements

### Requirement: la_simulacion_sigue_las_reglas
Tipo: funcional
El sistema DEBE modelar la concurrencia con un motor determinista en el que ninguna decisión de persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `decidir-union`) la tome un agente, en el que los registros de dos ramas se unan conservando los eventos de ambas, en el que lo decidido distinto por dos ramas quede sin elegir hasta que decida una persona, en el que un archivo de producto editado por dos ramas sea un conflicto, y en el que una revisión pierda su vigencia si el producto cambió después de hacerla.

#### Scenario: un agente intenta una decisión de persona
- DADO un escenario en curso con un agente
- CUANDO el agente intenta cerrar o aprobar
- ENTONCES la acción no se ejecuta, queda como propuesta pendiente y el registro lo dice con el nombre del agente

#### Scenario: la misma semilla, la misma traza
- DADO el mismo escenario y la misma semilla
- CUANDO se corre dos veces hasta el final
- ENTONCES las dos trazas son idénticas, y con otra semilla puede cambiar el orden de lo simultáneo pero nunca el resultado de las reglas

#### Scenario: una revisión vieja
- DADO una revisión aprobada sobre un producto
- CUANDO otra rama integra un cambio de ese producto
- ENTONCES la revisión figura vencida y el cambio vuelve a pedir revisión antes de cerrar

### Requirement: los_escenarios_cuentan_la_concurrencia
Tipo: funcional
El sistema DEBE ofrecer cinco escenarios (dos frentes que se unen solos, el mismo archivo editado por dos, dos ramas que decidieron distinto, una revisión que queda vieja, y un agente que intenta cerrar), cada uno con un final explicado en una frase y un registro donde cada decisión figura a nombre de quien la tomó.

#### Scenario: recorrer cada escenario hasta el final
- DADO cada uno de los cinco escenarios
- CUANDO se avanza paso a paso hasta el final
- ENTONCES el escenario termina, el final tiene su explicación y toda decisión del registro tiene actor y tipo (persona o agente)

#### Scenario: el conflicto lo resuelve una persona
- DADO el escenario del mismo archivo editado por dos
- CUANDO se llega al conflicto
- ENTONCES la escena lo marca, ningún agente lo resuelve y el avance sólo sigue cuando una persona elige

### Requirement: la_escena_se_controla_y_es_accesible
Tipo: funcional
El sistema DEBE mostrar en la página una escena de pixel art con sprites de `pixel.js` y controles para elegir escenario, avanzar un paso, reproducir, pausar, cambiar la velocidad y reiniciar, todos operables con teclado, con un registro anunciado por `aria-live`, con una descripción en texto de cada paso, y sin animación cuando la persona pide movimiento reducido.

#### Scenario: usar la página con teclado
- DADA la página abierta en Chromium
- CUANDO se recorre un escenario sólo con teclado
- ENTONCES cada control se alcanza y se activa, el registro crece paso a paso y el foco nunca queda atrapado

#### Scenario: movimiento reducido y pantalla chica
- DADA la preferencia de movimiento reducido y un ancho de 360 px
- CUANDO se abre la página
- ENTONCES nada se anima, cada escenario muestra su estado final con su texto, y no hay desplazamiento horizontal de la página

### Requirement: la_simulacion_dice_que_es_una_simulacion
Tipo: funcional
El sistema DEBE rotular la página como una simulación de las reglas (no ejecuta Factory), citar para cada regla el texto de `docs/colaboracion.md` que la respalda y nombrar sólo comandos que existen en la CLI, y DEBE enlazar la página desde la guía de colaboración y la portada.

#### Scenario: una cita o un comando que no existe
- DADA una regla cuya cita no está en `docs/colaboracion.md` o un comando inexistente
- CUANDO se corren las comprobaciones del sitio
- ENTONCES fallan nombrando la regla

#### Scenario: llegar a la simulación
- DADAS la portada y la guía de colaboración
- CUANDO se leen sus enlaces
- ENTONCES las dos enlazan a la página de la simulación y esa página enlaza de vuelta a la guía
