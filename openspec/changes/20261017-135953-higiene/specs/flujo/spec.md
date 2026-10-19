# Capability: flujo

## ADDED Requirements

### Requirement: un pedido de revisión cortado queda a la vista
Tipo: funcional
`pedir-revision` SHALL registrar el lanzamiento del revisor (revisor y candidato) antes de correrlo y su resultado al terminar, también si se interrumpe. Mientras un lanzamiento no tenga resultado, `estado` y `estado --json` (en `avisos`) SHALL avisar qué revisor se lanzó, cuándo y sobre qué candidato, y que no dejó resultado.

#### Scenario: un revisor que se corta sin terminar
- GIVEN un cambio con un candidato
- WHEN se lanza un revisor y el proceso de pedir-revision termina antes de que el revisor deje resultado
- THEN el registro tiene el lanzamiento, y estado avisa que ese revisor se lanzó sobre ese candidato y no dejó resultado

#### Scenario: un revisor que termina, o se interrumpe con Ctrl-C
- GIVEN un cambio con un candidato
- WHEN un revisor termina, o el pedido se interrumpe con Ctrl-C
- THEN queda su resultado (o «interrumpido») y estado no avisa de un lanzamiento sin resultado

### Requirement: las acciones sin autor se avisan
Tipo: funcional
Si el registro de un cambio tiene acciones sin autor identificado, `estado` y `estado --json` SHALL avisar cuántas y cuáles, y que un agente las hace con `--agente NOMBRE`.

#### Scenario: un agente que se olvidó de --agente
- GIVEN un cambio creado e importado sin --agente y sin una persona identificada
- WHEN se pide estado
- THEN avisa que esas acciones quedaron sin autor y cómo identificarlo la próxima vez

### Requirement: init no deja carpetas que Factory no usa
Tipo: funcional
`init` SHALL NOT dejar en el proyecto carpetas de Oracle vacías que Factory no usa (`corpus`, `relaciones`, `diferencial`) si las creó al inicializar, y SHALL NOT tocar las que ya existían. El bloqueo de `medir` SHALL vivir dentro de `.factory/local/` y el `.gitignore` que arma `init` SHALL NOT nombrar `.factory-demo/`.

#### Scenario: un proyecto nuevo
- GIVEN una carpeta vacía
- WHEN se corre init y después se miden requisitos con medir
- THEN no quedan corpus, relaciones ni diferencial vacíos, el bloqueo de medir se tomó en .factory/local/locks, y el .gitignore no nombra .factory-demo

#### Scenario: un proyecto con carpetas de Oracle propias
- GIVEN un proyecto que ya tiene corpus/ con casos
- WHEN se corre init
- THEN corpus/ y sus casos siguen igual
