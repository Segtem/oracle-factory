# Capability: practicas

## ADDED Requirements

### Requirement: la_medicion_reparte_los_hallazgos_de_la_primera_ronda_segun_se_pudieran_ver_en_la_spec
Tipo: funcional
El sistema DEBE ofrecer en `tools/medir_rondas.py` una opción `--origen` que reparta los hallazgos altos y medios de la primera ronda de los cambios cerrados en «atrapable al leer la spec» (rutas y enlaces, valores raros, falsos avisos o silencios, paridad con otra herramienta), «solo con el código» (pruebas débiles, verificador y evidencia, documentos y mensajes contra el código), «mixto» (clases de los dos grupos) y «sin clase», contando cada hallazgo una sola vez, y NO DEBE cambiar la salida sin esa opción.

#### Scenario: un hallazgo por grupo
- DADO una primera ronda con un hallazgo medio de rutas, uno medio de pruebas débiles, uno medio de las dos clases y uno medio sin clase
- CUANDO se mide con `--origen`
- ENTONCES cada grupo cuenta uno y el total es cuatro

#### Scenario: solo la primera ronda y solo altos y medios
- DADO hallazgos bajos, e hijos de una segunda ronda
- CUANDO se mide con `--origen`
- ENTONCES no se cuentan

#### Scenario: sin la opción nada cambia
- DADO los mismos registros
- CUANDO se mide sin `--origen`
- ENTONCES la salida es la que producía antes

### Requirement: la_salida_dice_la_regla_y_su_limite
Tipo: funcional
El sistema DEBE decir en la salida de `--origen` qué clases componen cada grupo y que el reparto es una aproximación por el texto del hallazgo y no un juicio humano.

#### Scenario: la regla a la vista
- DADO cualquier medición con `--origen`
- CUANDO se lee la salida
- ENTONCES nombra las clases de cada grupo y avisa que es una aproximación por texto

### Requirement: una_muestra_permite_comprobar_la_regla
Tipo: funcional
El sistema DEBE listar con `--muestra N` hasta N hallazgos de cada grupo, con el cambio, la ronda y el título, en un orden que no dependa de la máquina, y NO DEBE modificar ningún archivo del proyecto medido.

#### Scenario: la muestra es fija
- DADO más hallazgos que N en un grupo
- CUANDO se mide dos veces con `--muestra N`
- ENTONCES se listan los mismos N, ordenados por cambio y título

#### Scenario: solo lectura
- DADO un proyecto con registros
- CUANDO se mide con `--origen --muestra 3`
- ENTONCES ningún archivo del proyecto cambia
