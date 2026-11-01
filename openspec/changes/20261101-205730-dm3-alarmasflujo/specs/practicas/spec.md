# Capability: practicas

## ADDED Requirements

### Requirement: el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, cuando se pidió revisión para cuatro o más candidatos distintos, sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: cuatro candidatos revisados
- DADO un cambio al que se pidió revisión para cuatro candidatos distintos
- CUANDO se pide el estado
- ENTONCES el aviso nombra la cantidad de rondas y los pendientes y el próximo paso no cambian

#### Scenario: menos de cuatro
- DADO un cambio con tres candidatos revisados, uno de ellos con dos revisores
- CUANDO se pide el estado
- ENTONCES no hay aviso de bucle: los revisores de un mismo candidato son una ronda

#### Scenario: registro ilegible
- DADO un cambio cuyo registro de eventos no se puede leer
- CUANDO se pide el estado
- ENTONCES no hay aviso y el estado no falla

### Requirement: el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, cuando el candidato vigente agrega más de 450 líneas en archivos de producto, sin contar los archivos de pruebas, y sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: un candidato grande
- DADO un candidato que agrega 600 líneas a un archivo de producto
- CUANDO se pide el estado
- ENTONCES el aviso nombra las líneas agregadas y sugiere partir el cambio

#### Scenario: las pruebas no cuentan
- DADO un candidato que agrega 100 líneas de producto y 800 líneas en un archivo de pruebas
- CUANDO se pide el estado
- ENTONCES no hay aviso de cambio grande

#### Scenario: justo en el umbral
- DADO un candidato que agrega exactamente 450 líneas de producto
- CUANDO se pide el estado
- ENTONCES no hay aviso

#### Scenario: sin candidato vigente
- DADO un cambio sin candidato vigente
- CUANDO se pide el estado
- ENTONCES no hay aviso y el JSON indica que no se pudo calcular

### Requirement: el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado
Tipo: funcional
El sistema DEBE documentar en `docs/tests.md` los dos avisos con sus umbrales (4 rondas, 450 líneas) tal como están en el código, y DEBE aclarar que el conteo de aserciones quitadas es aproximado.

#### Scenario: el documento coincide con el código
- DADO los umbrales del código y el texto de `docs/tests.md`
- CUANDO se comparan
- ENTONCES el documento nombra los dos números del código y la palabra «aproximado» junto al conteo de aserciones
