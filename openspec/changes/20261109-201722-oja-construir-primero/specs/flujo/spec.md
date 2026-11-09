# Capability: flujo

## ADDED Requirements

### Requirement: ante_medir_listar_el_conductor_manda_construir_antes_de_elegir_medidas
Tipo: funcional
El sistema DEBE, ante el próximo paso `medir ID --listar`, mantener la acción `delegar_al_agente` y entregar una instrucción que diga, en este orden: primero construir lo que falte (las pruebas de cada escenario antes que el código, y los catálogos de medidas de los requisitos) sin correr todavía la evidencia completa, después elegir las medidas de cada requisito y proponerlas con `oracle-factory medir ... --requisito R --medida M`, y que confirmarlas es de una persona y que la evidencia se hace después de su confirmación; el motivo, el paso siguiente y el resto de las decisiones del conductor no cambian.

#### Scenario: instrucción completa y en orden
- DADO el próximo paso `medir ID --listar`
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente` y la instrucción nombra construir lo que falte (pruebas primero y catálogos, sin la evidencia completa todavía), proponer las medidas, y que confirmarlas es de una persona y que la evidencia va después, en ese orden

#### Scenario: nada más cambia
- DADO el próximo paso `medir ID --confirmar`, o un freno
- CUANDO el conductor decide
- ENTONCES la decisión es la de siempre (`pedir_a_persona`, o `frenar`)
