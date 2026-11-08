# Capability: despliegue

## ADDED Requirements

### Requirement: un_destino_declara_su_alcance_opcional
Tipo: funcional
El sistema DEBE aceptar en cada destino un campo opcional `alcance` con una lista no vacía de rutas de Git, y DEBE rechazar con un mensaje que nombre el destino un `alcance` que no sea una lista no vacía de textos no vacíos.

#### Scenario: un alcance válido
- DADO un destino con `alcance` igual a una lista de rutas
- CUANDO se carga la declaración
- ENTONCES el destino conserva su alcance

#### Scenario: un alcance inválido
- DADO un destino cuyo `alcance` es un texto, una lista vacía o una lista con un valor que no es texto
- CUANDO se carga la declaración
- ENTONCES se rechaza nombrando el destino y el campo

#### Scenario: sin alcance
- DADO un destino sin `alcance`
- CUANDO se carga la declaración
- ENTONCES se acepta como hasta ahora

### Requirement: cambios_elige_los_destinos_afectados
Tipo: funcional
El sistema DEBE ofrecer `desplegar --cambios`, que elige los destinos con archivos cambiados dentro de su `alcance` entre la última versión que Factory desplegó en ese destino y el commit del plan, DEBE incluir siempre los destinos sin `alcance`, los que nunca se desplegaron y aquellos cuya versión anterior no se puede comparar, y DEBE incluir también lo que los elegidos necesitan por `depende_de`.

#### Scenario: se cambia sólo lo de un destino
- DADOS dos destinos con alcances distintos, ambos desplegados antes, y un commit que sólo toca archivos del alcance del primero
- CUANDO se arma el plan con `--cambios`
- ENTONCES el plan incluye el primero y omite el segundo

#### Scenario: lo que no se puede descartar entra
- DADOS un destino sin alcance, otro nunca desplegado y otro cuya versión anterior no existe en el repositorio
- CUANDO se arma el plan con `--cambios`
- ENTONCES los tres entran, cada uno con su motivo

#### Scenario: un elegido arrastra lo que necesita
- DADO un destino afectado que depende de otro sin cambios
- CUANDO se arma el plan con `--cambios`
- ENTONCES el plan incluye también el destino del que depende, antes que él

### Requirement: el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada
Tipo: funcional
El sistema DEBE mostrar en el plan por qué entra cada destino y cuáles se omiten, y cuando ningún destino resulta afectado DEBE decir que no hay nada que desplegar y NO DEBE ejecutar nada, ni siquiera con `--autorizar`.

#### Scenario: el plan con motivos
- DADO un plan armado con `--cambios`
- CUANDO se muestra
- ENTONCES cada destino incluido trae su motivo y los omitidos figuran con el suyo

#### Scenario: nada que desplegar
- DADO un commit que no toca el alcance de ningún destino, todos desplegados antes y todos con alcance
- CUANDO se corre `desplegar --cambios --autorizar` como persona
- ENTONCES sale con 0, dice que no hay nada que desplegar y no ejecuta ningún comando ni crea un registro

### Requirement: sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance
Tipo: funcional
El sistema NO DEBE cambiar lo que hace `desplegar` sin `--cambios`, DEBE negar `--cambios` junto con `--destino`, y DEBE contar el campo `alcance`, la opción y sus límites en `docs/despliegue.md` y en la plantilla `docs/plantillas/destinos.json`.

#### Scenario: sin la opción
- DADA una declaración con alcances
- CUANDO se arma el plan sin `--cambios`
- ENTONCES incluye todos los destinos, como antes

#### Scenario: las dos opciones juntas
- DADO `desplegar --cambios --destino api`
- CUANDO se corre
- ENTONCES se niega diciendo que no se combinan

#### Scenario: la guía y la plantilla
- DADOS `docs/despliegue.md` y `docs/plantillas/destinos.json`
- CUANDO se leen
- ENTONCES nombran `alcance` y `--cambios`, y la guía dice que sólo se miran las rutas declaradas
