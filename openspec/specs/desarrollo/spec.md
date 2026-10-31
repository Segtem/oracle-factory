# Capability: desarrollo

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: paso_de_tests_primero
Origen: 20261030-185728-0w1-tests · desarrollo_cb4e5e98f60cb24f1.paso_de_tests_primero
Tipo: funcional
El sistema DEBE incluir, en las tareas de cada cambio nuevo, en español y en inglés, el paso de escribir primero los tests de cada escenario de la spec cuando sea posible y de comprobar que fallan antes de implementar.

#### Scenario: un cambio nuevo en español
- DADO un proyecto sin `idioma` declarado
- CUANDO se crea un cambio con `oracle-factory nuevo`
- ENTONCES `tasks.md` tiene el paso de escribir primero los tests, antes del paso de implementar

#### Scenario: un cambio nuevo en inglés
- DADO un proyecto con `"idioma": "en"`
- CUANDO se crea un cambio con `oracle-factory nuevo`
- ENTONCES `tasks.md` tiene el mismo paso en inglés, antes del paso de implementar, sin frases en español

#### Scenario: el paso no bloquea
- DADO un cambio cuyo `tasks.md` tiene el paso sin marcar
- CUANDO se corren `importar`, `medir`, `revisar`, `juzgar` y `cerrar`
- ENTONCES ninguno se niega por ese paso

### Requirement: guia_de_tests_para_agentes
Origen: 20261030-185728-0w1-tests · desarrollo_cb4e5e98f60cb24f1.guia_de_tests_para_agentes
Tipo: funcional
El sistema DEBE decir en la guía para agentes que los tests unitarios son parte del desarrollo y no suplantan a Oracle, y que un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa.

#### Scenario: la guía generada
- DADO un proyecto con Factory
- CUANDO se genera la guía con `oracle-factory agentes`
- ENTONCES incluye el paso de escribir tests primero y la guarda sobre los tests existentes

#### Scenario: la guía vigente
- DADO una guía generada antes de este cambio
- CUANDO se corre `oracle-factory agentes --verificar`
- ENTONCES dice que quedó vieja y cómo regenerarla

### Requirement: documento_de_la_practica
Origen: 20261030-185728-0w1-tests · desarrollo_cb4e5e98f60cb24f1.documento_de_la_practica
Tipo: funcional
El sistema DEBE tener un documento `docs/tests.md` que explique la práctica de los tests unitarios frente a Oracle y las mutaciones, cuándo escribirlos primero, qué hacer cuando no se puede y la guarda sobre tests existentes, con sus fuentes.

#### Scenario: el documento existe y cita
- DADO el repositorio de Factory
- CUANDO se lee `docs/tests.md`
- ENTONCES explica las tres capas (tests, mutaciones, Oracle), la guarda y cita las fuentes por su identificador

#### Scenario: el documento no se contradice con la práctica
- DADO el documento y la plantilla de tareas
- CUANDO se comparan
- ENTONCES ambos dicen que el paso es «cuando sea posible» y que no bloquea
