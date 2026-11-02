# Capability: practicas

## ADDED Requirements

### Requirement: el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica
Tipo: funcional
El sistema DEBE atribuir cada prueba `test_<letras><n>_…` de un módulo al requisito número `n` de la spec del cambio, en el orden en que la spec los lista, y DEBE negarse a declarar éxito si algún requisito no tiene casos, si un caso nombra un número sin requisito, o si el módulo no tiene casos.

#### Scenario: cada caso en su requisito
- DADO un módulo con casos af1, af1 y af2, y una spec de dos requisitos
- CUANDO se deriva el contrato
- ENTONCES el primer requisito tiene dos casos y el segundo uno, con su clase y su método

#### Scenario: un requisito sin casos
- DADO una spec de tres requisitos y un módulo con casos sólo para el primero y el segundo
- CUANDO se deriva el contrato
- ENTONCES falla nombrando el requisito sin casos

#### Scenario: un caso sin requisito
- DADO una spec de dos requisitos y un caso `test_af3_…`
- CUANDO se deriva el contrato
- ENTONCES falla nombrando el caso

#### Scenario: un nombre dentro de una cadena no es un caso
- DADO un módulo que nombra `def test_af9_x` dentro de un texto
- CUANDO se deriva el contrato
- ENTONCES ese texto no cuenta como caso

### Requirement: el_verificador_produce_la_evidencia_completa_del_cambio
Tipo: funcional
El sistema DEBE correr la suite y producir `suite.txt`, `hechos.json`, `trazabilidad.json` y `resultado.json`, y DEBE declarar éxito sólo si todos los casos pasan, la corrida es exactamente la esperada, las fuentes no cambiaron mientras corría y la trazabilidad es ok.

#### Scenario: un cambio completo
- DADO un cambio cuyos casos pasan
- CUANDO se produce la evidencia
- ENTONCES los cuatro archivos existen, el resultado dice éxito y los hechos nombran cada caso con su requisito y su código

#### Scenario: un caso falla
- DADO un cambio con un caso que falla
- CUANDO se produce la evidencia
- ENTONCES el resultado no dice éxito y el hecho de ese caso lleva un código distinto de cero

#### Scenario: las fuentes cambian durante la corrida
- DADO un archivo del producto que cambia mientras corre la suite
- CUANDO se produce la evidencia
- ENTONCES el resultado dice que las fuentes no estuvieron quietas y no declara éxito

### Requirement: el_verificador_escribe_los_catalogos_del_cambio
Tipo: funcional
El sistema DEBE escribir, con `--catalogos`, el catálogo de la corrida completa y uno por requisito, cada uno contando exactamente los casos de ese requisito, y escribirlos de nuevo con los mismos casos no DEBE cambiar ningún archivo.

#### Scenario: los catálogos del cambio
- DADO un cambio con dos requisitos de dos y tres casos
- CUANDO se escriben los catálogos
- ENTONCES hay tres archivos, los umbrales son 2 y 3, y la corrida completa cuenta 5

#### Scenario: escribirlos de nuevo
- DADO los catálogos ya escritos
- CUANDO se escriben otra vez sin cambiar los casos
- ENTONCES ningún archivo cambia
