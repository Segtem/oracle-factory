# Capability: practicas

## ADDED Requirements

### Requirement: el_verificador_no_pide_casos_para_un_requisito_exceptuado
Tipo: funcional
El sistema DEBE tratar el requisito que la spec marca con «Pruebas: no aplica — motivo» como un requisito que no necesita casos: el verificador DEBE derivar el contrato sin él, conservar la numeración de los demás (`test_<letras><n>_…` sigue siendo el requisito `n` de la spec) y NO DEBE aceptar un caso que nombre un requisito exceptuado.

#### Scenario: un requisito exceptuado sin casos
- DADO una spec de tres requisitos donde el segundo declara «Pruebas: no aplica — motivo» y un módulo con casos sólo para el primero y el tercero
- CUANDO se deriva el contrato
- ENTONCES el contrato tiene el primero y el tercero con sus casos y no menciona al segundo

#### Scenario: un caso para el requisito exceptuado
- DADO la misma spec y un caso `test_xx2_…`
- CUANDO se deriva el contrato
- ENTONCES falla nombrando el caso y el requisito exceptuado

#### Scenario: los demás requisitos siguen exigiendo casos
- DADO la misma spec y un módulo sin casos para el tercero
- CUANDO se deriva el contrato
- ENTONCES falla nombrando el tercero como requisito sin casos

### Requirement: la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos
Tipo: funcional
El sistema DEBE producir la evidencia y escribir los catálogos de un cambio con requisitos exceptuados sin hechos ni catálogo de medida para el exceptuado, con la corrida completa contando sólo los casos de los demás, y DEBE retirar el catálogo que un requisito ya tenía si pasa a estar exceptuado.

#### Scenario: la evidencia sin el exceptuado
- DADO un cambio de tres requisitos con el segundo exceptuado y casos que pasan para los otros dos
- CUANDO se produce la evidencia
- ENTONCES hay éxito, los hechos nombran sólo al primero y al tercero y la corrida cuenta sus casos

#### Scenario: los catálogos sin el exceptuado
- DADO el mismo cambio
- CUANDO se escriben los catálogos
- ENTONCES hay un catálogo para el primero, uno para el tercero y la corrida completa, y ninguno para el segundo

#### Scenario: un requisito que pasa a estar exceptuado
- DADO un catálogo ya escrito para un requisito
- CUANDO la spec lo exceptúa y se escriben los catálogos otra vez
- ENTONCES su catálogo se retira y los demás no cambian

### Requirement: una_excepcion_mal_escrita_no_se_ignora
Tipo: funcional
El sistema DEBE rechazar, al derivar el contrato, una línea «Pruebas:» mal escrita (sin motivo, repetida o distinta de «no aplica — motivo») con el mensaje del lector de excepciones de Factory, en vez de ignorarla y pedir casos como si no existiera.

#### Scenario: una excepción sin motivo
- DADO una spec con «Pruebas: no aplica» sin motivo
- CUANDO se deriva el contrato
- ENTONCES falla con el error del lector de excepciones

#### Scenario: una línea «Pruebas:» con otra cosa
- DADO una spec con «Pruebas: manuales»
- CUANDO se deriva el contrato
- ENTONCES falla con el error del lector de excepciones

#### Scenario: todos los requisitos exceptuados
- DADO una spec cuyos requisitos están todos exceptuados
- CUANDO se deriva el contrato
- ENTONCES falla porque no hay ningún caso que verificar
