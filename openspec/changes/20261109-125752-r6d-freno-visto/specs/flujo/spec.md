# Capability: flujo

## ADDED Requirements

### Requirement: el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada
Tipo: funcional
El sistema DEBE dejar de declarar el freno `prueba_existente_editada` cuando hay una revisión aprobada y vigente del cambio (decisión `aprobar`, del mismo producto que el candidato actual y sin problemas), y declararlo cuando hay tests existentes editados y no la hay; los avisos de tests editados siguen mostrándose en ambos casos, y los demás frenos no cambian.

#### Scenario: sin revisión aprobada
- DADO un candidato que editó un test que ya existía y ninguna revisión aprobada vigente
- CUANDO se calculan los frenos
- ENTONCES `prueba_existente_editada` figura entre ellos

#### Scenario: con revisión aprobada vigente
- DADO el mismo candidato con una revisión aprobada y vigente
- CUANDO se calculan los frenos
- ENTONCES `prueba_existente_editada` no figura, y el aviso de test editado sigue en `avisos`

#### Scenario: la revisión deja de ser vigente
- DADO una revisión aprobada de un candidato anterior
- CUANDO se calculan los frenos del candidato nuevo
- ENTONCES `prueba_existente_editada` vuelve a figurar

#### Scenario: otros frenos
- DADO una revisión aprobada vigente y dos juicios de Oracle rojos
- CUANDO se calculan los frenos
- ENTONCES `juicios_rojos` sigue figurando
