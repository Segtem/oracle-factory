# Capability: flujo

## ADDED Requirements

### Requirement: autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona
Tipo: funcional
El sistema DEBE ofrecer `oracle-factory autopilot ID --ejecutar` solo con `--agente`: sin él, DEBE fallar con un error claro sin correr ni escribir nada. El bucle NUNCA DEBE correr un comando de decisión de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `abandonar`, `modo`, `autonomia`, `soltar`, `decidir-union`), aunque la decisión llegue mal clasificada; y DEBE detenerse sin ejecutar nada cuando la decisión es `terminado`, `frenar` o `pedir_a_persona`, mostrando en el último caso el comando listo para pegar.

#### Scenario: sin agente
- DADO que se corre `autopilot ID --ejecutar` sin `--agente`
- CUANDO se ejecuta
- ENTONCES falla con un error que pide `--agente` y no corre ni escribe nada

#### Scenario: una decisión de persona
- DADO un cambio cuyo próximo paso es `cerrar`
- CUANDO corre el bucle
- ENTONCES se detiene sin ejecutar nada y muestra el comando de la persona

#### Scenario: una decisión de persona mal clasificada
- DADO una decisión `actuar` cuyo comando es uno de persona
- CUANDO el bucle va a ejecutarla
- ENTONCES se detiene sin correrla y lo dice

### Requirement: el_bucle_observa_decide_actua_y_vuelve_a_observar
Tipo: funcional
El sistema DEBE, en cada vuelta, observar el estado, decidir con `autopilot.decidir`, y si la acción es `actuar` correr el comando de Factory con `--agente NOMBRE` en un proceso aparte, o si es `delegar_al_agente` lanzar el comando de `--lanzar` con la instrucción como último argumento (sin `--lanzar`, detenerse diciendo que falta), y volver a observar después de cada paso.

#### Scenario: un comando mecánico
- DADO una decisión `actuar` con `oracle-factory juzgar ID`
- CUANDO corre el bucle con `--agente a`
- ENTONCES corre `juzgar` con `--agente a`, vuelve a observar y sigue con lo que venga

#### Scenario: trabajo creativo con agente
- DADO una decisión `delegar_al_agente` y `--lanzar COMANDO`
- CUANDO corre el bucle
- ENTONCES lanza COMANDO con la instrucción como último argumento y vuelve a observar

#### Scenario: trabajo creativo sin agente
- DADO una decisión `delegar_al_agente` y sin `--lanzar`
- CUANDO corre el bucle
- ENTONCES se detiene diciendo que falta `--lanzar` y deja la instrucción

### Requirement: el_bucle_tiene_topes_y_se_frena_solo
Tipo: funcional
El sistema DEBE detener el bucle cuando se llega al tope de pasos o de minutos (10 y 120 por defecto, `--max-pasos` y `--max-minutos`), cuando la misma decisión con el mismo comando se repite dos veces seguidas (sin progreso), cuando un comando o el agente lanzado terminan con error o no arrancan, o cuando los datos no se pueden leer; en todos los casos DEBE decir el motivo y no volver a actuar.

#### Scenario: el tope de pasos
- DADO un estado que siempre pide actuar con comandos distintos
- CUANDO se llega a `--max-pasos`
- ENTONCES se detiene y lo dice

#### Scenario: sin progreso
- DADO que la misma decisión con el mismo comando aparece dos veces seguidas
- CUANDO corre el bucle
- ENTONCES se detiene por falta de progreso

#### Scenario: un comando falla
- DADO que el comando de un paso termina con error o el agente lanzado no arranca
- CUANDO corre el bucle
- ENTONCES se detiene con el error y no sigue

### Requirement: cada_paso_deja_su_porque_en_el_registro
Tipo: funcional
El sistema DEBE dejar, antes de cada paso, un `mensaje` en el registro del cambio, a nombre del agente, con la acción, el motivo y el comando o la instrucción; y al final, otro con el motivo de la detención, y DEBE mostrar un resumen de los pasos (en texto y con `--json`) con el resultado de cada uno.

#### Scenario: el porqué
- DADO un paso `actuar`
- CUANDO se ejecuta
- ENTONCES el registro tiene antes un mensaje del agente con la acción, el motivo y el comando

#### Scenario: el final
- DADO que el bucle se detuvo
- CUANDO termina
- ENTONCES el registro tiene un mensaje con el motivo de la detención y la salida muestra el resumen de los pasos
