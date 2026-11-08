# Capability: modos

## ADDED Requirements

### Requirement: la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona
Tipo: funcional
El sistema DEBE admitir en `.factory/config.json` una clave opcional `autonomia` con las etapas `integracion`, `publicacion` y `produccion`, cada una en `confirmacion` o `autonomo`, DEBE tratar como `confirmacion` toda etapa no declarada, DEBE rechazar con un error que nombre el archivo y el valor una etapa o un modo desconocidos, y NO DEBE cambiar nada para un proyecto sin esa clave.

#### Scenario: sin la clave
- DADO un proyecto sin `autonomia` en su configuración
- CUANDO se lee la configuración
- ENTONCES las tres etapas son `confirmacion`

#### Scenario: una etapa declarada
- DADO `autonomia` con `produccion` en `autonomo`
- CUANDO se lee la configuración
- ENTONCES `produccion` es `autonomo` y las otras dos siguen en `confirmacion`

#### Scenario: una etapa o un modo desconocidos
- DADO `autonomia` con una etapa que no existe, o `produccion` en `funcional`
- CUANDO se lee la configuración
- ENTONCES falla nombrando `.factory/config.json` y el valor

### Requirement: un_agente_solo_decide_en_una_etapa_autonoma
Tipo: funcional
El sistema DEBE permitir que un agente decida en una etapa posterior a la construcción únicamente cuando el modo de esa etapa es `autonomo`; en cualquier otro caso DEBE rechazarlo y dejar la decisión a una persona, que decide siempre.

#### Scenario: autónoma
- DADO la etapa `produccion` en `autonomo`
- CUANDO se pregunta quién decide por la vía de agente
- ENTONCES decide el agente

#### Scenario: con confirmación
- DADO la etapa `publicacion` en `confirmacion`
- CUANDO se pregunta quién decide por la vía de agente
- ENTONCES se rechaza

### Requirement: autonomia_muestra_las_etapas_y_quien_decide_en_cada_una
Tipo: funcional
El sistema DEBE ofrecer `oracle-factory autonomia`, de solo lectura y con `--json`, que muestre las cuatro etapas (la construcción con el modo por defecto del proyecto), el modo de cada una, quién decide por la vía de agente, y si hoy existe un comando de Factory que la aplique.

#### Scenario: el estado por defecto
- DADO un proyecto sin `autonomia`
- CUANDO se corre `autonomia`
- ENTONCES muestra construcción con el modo del proyecto y las otras tres en `confirmacion` con una persona como quien decide

#### Scenario: la salida estructurada
- DADO `produccion` en `autonomo`
- CUANDO se corre `autonomia --json`
- ENTONCES el JSON lista las cuatro etapas con su modo y quién decide, y no modifica ningún archivo

### Requirement: solo_una_persona_cambia_la_autonomia_de_una_etapa
Tipo: funcional
El sistema DEBE permitir cambiar la autonomía de una etapa con `oracle-factory autonomia ETAPA MODO` únicamente a una persona desde su terminal, con una confirmación, y DEBE negárselo a un agente con `--agente`, sin modificar el archivo; el cambio DEBE conservar el resto de la configuración.

#### Scenario: un agente lo intenta
- DADO un agente
- CUANDO corre `autonomia produccion autonomo --agente claude-code`
- ENTONCES falla diciendo que lo decide una persona y la configuración no cambia

#### Scenario: una persona lo cambia
- DADO una persona en su terminal que confirma
- CUANDO corre `autonomia produccion autonomo`
- ENTONCES la configuración declara `produccion` en `autonomo` y conserva las demás claves

#### Scenario: una persona cancela
- DADO una persona que elige cancelar
- CUANDO corre `autonomia produccion autonomo`
- ENTONCES la configuración no cambia

### Requirement: desplegar_autorizar_respeta_la_autonomia_de_produccion
Tipo: funcional
El sistema DEBE permitir que un agente ejecute `desplegar --autorizar` solo cuando la etapa `produccion` está en `autonomo`, registrando la autorización a nombre del agente, y DEBE seguir negándoselo en cualquier otro caso con el mismo mensaje de hoy; el plan, la puerta y la simulación se siguen exigiendo igual.

#### Scenario: producción con confirmación
- DADO `produccion` en `confirmacion`
- CUANDO un agente corre `desplegar --autorizar`
- ENTONCES falla diciendo que lo hace una persona y no se ejecuta nada

#### Scenario: producción autónoma
- DADO `produccion` en `autonomo` y un plan que pasa
- CUANDO un agente corre `desplegar --autorizar`
- ENTONCES se ejecuta y la corrida queda registrada con el agente como quien autorizó

#### Scenario: producción autónoma con un plan negado
- DADO `produccion` en `autonomo` y un plan que la puerta niega
- CUANDO un agente corre `desplegar --autorizar`
- ENTONCES no se ejecuta nada
