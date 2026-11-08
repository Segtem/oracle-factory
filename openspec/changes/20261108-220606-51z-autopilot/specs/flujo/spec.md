# Capability: flujo

## ADDED Requirements

### Requirement: el_conductor_decide_el_siguiente_paso_por_reglas
Tipo: funcional
El sistema DEBE decidir, solo con los datos de `estado` del cambio y por reglas fijas, una acción entre `terminado`, `frenar`, `pedir_a_persona`, `delegar_al_agente` y `actuar`, con el comando o la instrucción, quién actúa y el motivo de la regla. Un comando de decisión de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `abandonar`, `modo`, `autonomia`, `soltar`, `decidir-union`) DEBE ser siempre `pedir_a_persona`; un comando mecánico (`importar`, `juzgar`, `pedir-revision`, `revision-preparar`, `tomar`, `mensaje`) DEBE ser `actuar`; un paso escrito en prosa (corregir, commitear, resolver) o elegir medidas DEBE ser `delegar_al_agente`; y si un paso de revisión llega sin candidato, la acción es construir, también `delegar_al_agente`.

#### Scenario: una decisión de persona
- DADO un cambio cuyo próximo paso es `oracle-factory cerrar ID`
- CUANDO el conductor decide
- ENTONCES la acción es `pedir_a_persona`, con ese comando listo para pegar

#### Scenario: un comando mecánico
- DADO un cambio cuyo próximo paso es `oracle-factory juzgar ID`
- CUANDO el conductor decide
- ENTONCES la acción es `actuar` y el actor es un agente

#### Scenario: trabajo creativo
- DADO un próximo paso en prosa («corregí los hallazgos…») o `medir ID --listar`
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente`

#### Scenario: construir
- DADO un cambio sin candidato vigente cuyo próximo paso es pedir la revisión
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente` y la instrucción es construir primero

### Requirement: el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce
Tipo: funcional
El sistema DEBE frenar, antes de cualquier otra regla, cuando el cambio tiene algún freno de `estado`, cuando el próximo paso no es uno que el conductor reconoce, o cuando faltan archivos del cambio; y DEBE decir `terminado` cuando el cambio está cerrado o abandonado y no tiene próximo paso. Frenar nunca trae un comando para actuar.

#### Scenario: un freno
- DADO un cambio con un freno y un próximo paso mecánico
- CUANDO el conductor decide
- ENTONCES la acción es `frenar`, con los frenos y sin comando

#### Scenario: un paso desconocido o archivos faltantes
- DADO un próximo paso que no empieza con `oracle-factory` ni con un verbo conocido, o que dice que faltan archivos
- CUANDO el conductor decide
- ENTONCES la acción es `frenar` y el motivo lo dice

#### Scenario: un cambio terminado
- DADO un cambio cerrado
- CUANDO el conductor decide
- ENTONCES la acción es `terminado`

### Requirement: autopilot_solo_lee_y_lo_muestra
Tipo: funcional
El sistema DEBE ofrecer `oracle-factory autopilot ID`, de solo lectura, que muestre la decisión en texto y con `--json` (acción, quién, comando, instrucción, motivo y frenos), sin escribir nada en el proyecto ni en el registro del cambio, y que falle con un error claro si el cambio no existe.

#### Scenario: la decisión en texto y en JSON
- DADO un cambio con próximo paso
- CUANDO se corre `autopilot ID` y `autopilot ID --json`
- ENTONCES las dos dicen la misma acción y el mismo comando

#### Scenario: no escribe
- DADO un cambio
- CUANDO se corre `autopilot ID`
- ENTONCES el registro del cambio y el árbol de trabajo quedan idénticos

#### Scenario: un cambio que no existe
- DADO un identificador que no existe
- CUANDO se corre `autopilot ID`
- ENTONCES falla con un error que nombra el identificador
