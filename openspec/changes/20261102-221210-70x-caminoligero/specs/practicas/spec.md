# Capability: practicas

## ADDED Requirements

### Requirement: el_estado_dice_si_el_candidato_califica_para_el_camino_ligero
Tipo: funcional
El sistema DEBE decir en el estado de un cambio, y en su JSON, si el candidato vigente califica para el camino ligero: cuando agrega 150 líneas de producto o menos y no toca ninguna regla de decisión. Cuando no califica DEBE decir por qué, y cuando no se puede calcular DEBE decirlo en vez de afirmar un camino.

#### Scenario: un cambio chico
- DADO un candidato que agrega 40 líneas de producto y no toca ninguna regla de decisión
- CUANDO se pide el estado
- ENTONCES el estado dice camino ligero y el JSON lo marca como ligero con las 40 líneas

#### Scenario: un cambio grande
- DADO un candidato que agrega 151 líneas de producto
- CUANDO se pide el estado
- ENTONCES el estado dice camino completo y nombra las líneas y el umbral

#### Scenario: justo en el umbral
- DADO un candidato que agrega exactamente 150 líneas de producto y no toca reglas de decisión
- CUANDO se pide el estado
- ENTONCES el estado dice camino ligero

#### Scenario: toca una regla de decisión
- DADO un candidato de 10 líneas que modifica `oracle_factory/modos.py`, o que renombra un archivo desde `oracle_factory/flujo_revision.py`
- CUANDO se pide el estado
- ENTONCES el estado dice camino completo y nombra el archivo de decisión tocado

#### Scenario: las pruebas no cuentan
- DADO un candidato con 100 líneas de producto y 800 líneas en un archivo de pruebas
- CUANDO se pide el estado
- ENTONCES el estado dice camino ligero

#### Scenario: sin candidato vigente
- DADO un cambio sin candidato vigente
- CUANDO se pide el estado
- ENTONCES el estado no afirma un camino y el JSON indica que no se pudo calcular

### Requirement: el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente
Tipo: funcional
El sistema NO DEBE cambiar por el camino ligero los pasos pendientes, el próximo paso ni quién decide cada paso: la aprobación de la spec, la confirmación de las medidas, la revisión humana y el cierre siguen siendo los mismos, y un candidato que no califica sigue pudiendo cerrarse.

#### Scenario: los pendientes son iguales
- DADO el mismo cambio con un candidato ligero y con uno completo
- CUANDO se pide el estado de cada uno
- ENTONCES los pendientes y el próximo paso no dependen del camino

### Requirement: la_guia_para_agentes_explica_el_camino_ligero
Tipo: funcional
El sistema DEBE explicar en la guía para agentes que el camino ligero consiste en un revisor y una ronda, con los dos umbrales y la lista de reglas de decisión tal como están en el código, y que si esa ronda trae hallazgos medios o altos el cambio sigue el camino completo; y DEBE detectar con `agentes --verificar` que la guía quedó vieja si cambian esos datos.

#### Scenario: la guía coincide con el código
- DADO el código con sus umbrales y su lista de reglas de decisión
- CUANDO se genera la guía
- ENTONCES nombra las 150 líneas, cada archivo de la lista y el criterio de la ronda

#### Scenario: la guía quedó vieja
- DADO un cambio en el umbral o en la lista sin regenerar la guía
- CUANDO se verifica
- ENTONCES `agentes --verificar` falla
