# Capability: practicas

## ADDED Requirements

### Requirement: pedir_revision_muestra_la_lista_previa_sin_bloquear
Tipo: funcional
El sistema DEBE mostrar la lista previa a la revisión cuando se pide una revisión, antes de lanzar al revisor, sin cambiar el pedido que recibe el revisor ni impedir que la revisión se pida.

#### Scenario: se pide una revisión
- DADO un cambio con un candidato listo para revisar y un revisor configurado
- CUANDO se pide la revisión
- ENTONCES la salida muestra la lista previa antes de la línea que anuncia el lanzamiento del revisor, y el revisor se lanza igual

#### Scenario: el pedido no cambia
- DADO el mismo cambio y el mismo candidato
- CUANDO se pide la revisión
- ENTONCES el texto del pedido que recibe el revisor es el mismo que sin la lista

### Requirement: la_lista_previa_tiene_una_sola_fuente
Tipo: funcional
El sistema DEBE tener la lista previa en un solo lugar de código, con una pregunta por cada clase de problema y la regla de reusar lo existente y arreglar la clase, y DEBE tener un documento docs/lista-previa.md que contenga cada pregunta tal cual, de modo que el mensaje y el documento no puedan divergir.

#### Scenario: el documento y el mensaje dicen lo mismo
- DADO la lista previa del código y el documento docs/lista-previa.md
- CUANDO se comparan
- ENTONCES cada pregunta de la lista aparece en el documento con el mismo texto

#### Scenario: se agrega una pregunta sin actualizar el documento
- DADO una pregunta nueva en la lista del código que el documento no tiene
- CUANDO se corre la comprobación
- ENTONCES la comprobación falla nombrando la pregunta que falta

### Requirement: la_guia_para_agentes_nombra_la_lista_previa
Tipo: funcional
El sistema DEBE decir en la guía para agentes que genera oracle-factory agentes que existe la lista previa y que se mira antes de pedir una revisión, y DEBE detectar como vieja una guía que no lo dice.

#### Scenario: la guía generada
- DADO un proyecto con Factory inicializado
- CUANDO se genera la guía con oracle-factory agentes
- ENTONCES nombra docs/lista-previa.md y dice que se mira antes de pedir una revisión

#### Scenario: una guía vieja
- DADO una guía para agentes sin esa mención
- CUANDO se verifica con oracle-factory agentes --verificar
- ENTONCES se detecta como vieja
