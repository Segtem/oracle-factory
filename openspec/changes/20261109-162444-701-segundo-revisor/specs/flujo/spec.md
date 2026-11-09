# Capability: flujo

## ADDED Requirements

### Requirement: estado_dice_que_segundo_revisor_falta_en_el_camino_completo
Tipo: funcional
El sistema DEBE ofrecer en `estado --json` la clave `segundo_revisor`: el nombre de un revisor configurado cuyo proveedor todavía no informó, cuando el camino del candidato es completo y los informes de todos los candidatos del cambio cubren menos de dos proveedores distintos; en cualquier otro caso (camino ligero o sin calcular, ya hay dos proveedores, ningún revisor configurado de otro proveedor, configuración o informes ilegibles) DEBE ser `null`, sin cambiar ningún otro dato del estado.

#### Scenario: camino completo con un solo proveedor
- DADO un candidato de camino completo con un informe de `agy` y revisores configurados `agy`, `agy2` (mismo proveedor) y `codex`
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `codex`

#### Scenario: ya hay dos proveedores
- DADO informes de `agy` y de `codex`, aunque sean de candidatos distintos
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null`

#### Scenario: camino ligero
- DADO un candidato de camino ligero con un solo informe
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null`

#### Scenario: sin otro proveedor ni datos legibles
- DADO que sólo hay revisores de un proveedor, o una configuración que no se puede leer
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null` y `estado` no falla

### Requirement: el_conductor_pide_el_segundo_revisor_antes_de_la_revision
Tipo: funcional
El sistema DEBE, ante un próximo paso `revisar` con un `segundo_revisor` válido (texto no vacío de letras, dígitos, punto, guion y guion bajo), decidir `actuar` con el comando mecánico `oracle-factory pedir-revision ID --a ESE_REVISOR`, antes de delegar la propuesta de revisión o pedirle la revisión a una persona; con `segundo_revisor` ausente, `null` o inválido la decisión no cambia; y los frenos y los datos ilegibles siguen yendo primero.

#### Scenario: con segundo revisor
- DADO el próximo paso `revisar` con `segundo_revisor` `codex`
- CUANDO el conductor decide
- ENTONCES la acción es `actuar` y el comando es `oracle-factory pedir-revision ID --a codex`

#### Scenario: sin segundo revisor
- DADO el próximo paso `revisar` con `segundo_revisor` `null` o ausente
- CUANDO el conductor decide
- ENTONCES la decisión es la de siempre (delegar la propuesta o pedir a la persona)

#### Scenario: nombre inválido
- DADO un `segundo_revisor` con espacios o con un `;`
- CUANDO el conductor decide
- ENTONCES la decisión es la de siempre y no corre ese comando

#### Scenario: con un freno
- DADO el próximo paso `revisar` con `segundo_revisor` y un freno
- CUANDO el conductor decide
- ENTONCES la acción es `frenar`
