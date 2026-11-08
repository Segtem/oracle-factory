# Capability: despliegue

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: los_destinos_los_declara_el_proyecto
Origen: 20261106-205202-8od-destinos · despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto
Tipo: funcional
El sistema DEBE leer los destinos de despliegue de `.factory/destinos.json` —cada uno con nombre, tipo, comandos de construir, desplegar, probar, versión y volver, las dependencias con otros destinos y los nombres de los secretos que necesita—, sin conocer ninguna tecnología concreta, y DEBE rechazar una declaración inválida nombrando el destino y el campo.

#### Scenario: un destino declarado se ve
- DADO un proyecto con un VPS, una app y un ESP32 declarados
- CUANDO se lista con `oracle-factory destinos`
- ENTONCES aparecen los tres con su tipo, sus dependencias y su estado «sin desplegar»

#### Scenario: una declaración que no sirve
- DADO un destino sin comando de desplegar, una dependencia de un destino que no existe, un ciclo de dependencias o un secreto escrito con valor
- CUANDO se lee la declaración
- ENTONCES falla nombrando el destino y qué está mal, y no ejecuta nada

### Requirement: un_despliegue_es_un_plan_que_autoriza_una_persona
Origen: 20261106-205202-8od-destinos · despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona
Tipo: funcional
El sistema DEBE armar el plan de despliegue de un commit de la rama de despliegue —los destinos en el orden de sus dependencias— y mostrarlo antes de ejecutar algo, DEBE negarse si la puerta local no está en verde o si el commit no está en esa rama, y DEBE ejecutarlo sólo cuando una persona lo autoriza: un agente puede armarlo y simularlo, pero no autorizarlo, y ningún despliegue arranca solo.

#### Scenario: simular no ejecuta nada
- DADO un plan con tres destinos
- CUANDO un agente corre `desplegar --simular`
- ENTONCES se imprime el orden y los comandos de cada destino y no se ejecuta ninguno

#### Scenario: un agente no autoriza
- DADO un plan armado
- CUANDO un agente intenta `desplegar --autorizar`
- ENTONCES se niega, no cambia ningún destino y dice que lo autoriza una persona

#### Scenario: la puerta en rojo
- DADA la puerta local con una falla
- CUANDO se arma el plan
- ENTONCES se niega nombrando la falla

### Requirement: se_prueba_cada_destino_y_el_conjunto
Origen: 20261106-205202-8od-destinos · despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto
Tipo: funcional
El sistema DEBE ejecutar, por destino y en orden, comprobar que se alcanza, construir, desplegar, verificar que corre la versión del plan y correr su prueba de humo, y DEBE correr al final la prueba de conjunto declarada; DEBE decir «todo quedó funcionando» sólo cuando cada destino del plan quedó probado con la versión del plan y la prueba de conjunto pasó, y un destino que no se alcanzó DEBE quedar «inalcanzable», nunca verde.

#### Scenario: todo anda
- DADOS tres destinos que despliegan, corren la versión del plan y pasan su prueba de humo, y una prueba de conjunto que pasa
- CUANDO una persona autoriza el plan
- ENTONCES los tres quedan «probado» y el resultado es «todo quedó funcionando»

#### Scenario: un destino apagado
- DADO un destino cuyo comando de alcanzar falla
- CUANDO se ejecuta el plan
- ENTONCES queda «inalcanzable», no se despliega y el resultado no es «todo quedó funcionando»

#### Scenario: desplegó pero corre otra versión
- DADO un destino cuyo comando de versión devuelve otro commit que el del plan
- CUANDO se ejecuta
- ENTONCES queda «fallido» y no se corre su prueba de humo como si estuviera bien

#### Scenario: el conjunto falla
- DADOS todos los destinos probados y una prueba de conjunto que falla
- CUANDO termina la corrida
- ENTONCES el resultado es «fallido», dice que fue la prueba de conjunto, y los destinos conservan su estado «probado»

### Requirement: un_fallo_deja_cada_destino_en_un_estado_dicho
Origen: 20261106-205202-8od-destinos · despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho
Tipo: funcional
El sistema DEBE, ante el fallo de un destino, cortar la corrida (o seguir con los destinos que no dependen del caído, si el proyecto lo declara), volver atrás con su comando los destinos desplegados en esa corrida, y dejar cada uno en un estado dicho —sin desplegar, desplegado, probado, fallido, revertido o inalcanzable—, avisando de los que quedaron desplegados sin poder volverse atrás; DEBE calcular «desactualizado» comparando la versión que el destino dice que corre con la punta de la rama, mostrándolo «desconocido» si no se alcanza.

#### Scenario: falla el segundo destino
- DADO un plan de api, app y nodo donde la app falla su prueba de humo
- CUANDO termina la corrida con la política de cortar
- ENTONCES el nodo no se toca, la api se vuelve atrás y queda «revertido», la app queda «fallido» y el resultado lo dice

#### Scenario: un destino que no se puede volver atrás
- DADO un destino sin comando de volver que se desplegó antes de un fallo
- CUANDO termina la corrida
- ENTONCES queda «desplegado» con el aviso «sin poder volver atrás»

#### Scenario: desactualizado
- DADO un destino que corre un commit anterior a la punta de la rama
- CUANDO se consulta
- ENTONCES figura desactualizado, y si no se alcanza figura «desconocido»

### Requirement: cada_ejecucion_deja_evidencia_sin_secretos
Origen: 20261106-205202-8od-destinos · despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos
Tipo: funcional
El sistema DEBE guardar en `.factory/despliegues/` un registro de cada corrida con el commit, quién planeó y quién autorizó, y por destino los estados, las versiones antes y después, los comandos, su salida y los tiempos, DEBE tapar en cualquier salida registrada el valor de los secretos declarados, y DEBE exponer el estado de todos los destinos como `oracle-factory destinos --json` para el tablero.

#### Scenario: la salida con un secreto
- DADO un comando que imprime el valor de un secreto declarado
- CUANDO se registra la corrida
- ENTONCES el registro no contiene ese valor y marca dónde estaba

#### Scenario: el estado para el tablero
- DADA una corrida terminada
- CUANDO se corre `destinos --json`
- ENTONCES cada destino trae su estado, su versión desplegada, la esperada, su última prueba y si está desactualizado

### Requirement: sirve_para_cualquier_proyecto
Origen: 20261106-205202-8od-destinos · despliegue_c1f413032a7a55aa1.sirve_para_cualquier_proyecto
Tipo: funcional
El sistema DEBE funcionar para cualquier mezcla de destinos sin código propio de ninguno, y DEBE traer plantillas de ejemplo copiables (servidor por SSH, contenedor, firmware de microcontrolador, app) que una prueba ejecuta contra destinos simulados con scripts locales, sin red ni dispositivos reales.

#### Scenario: una mezcla que nadie previó
- DADO un proyecto con un destino declarado de un tipo que Factory nunca vio
- CUANDO se despliega
- ENTONCES se trata igual que cualquier otro: sus comandos, sus estados y su registro

#### Scenario: las plantillas funcionan
- DADAS las plantillas copiadas a un proyecto de prueba con destinos simulados
- CUANDO se despliega
- ENTONCES el resultado es «todo quedó funcionando»

### Requirement: un_destino_declara_su_alcance_opcional
Origen: 20261108-020932-3t5-alcance · despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional
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
Origen: 20261108-020932-3t5-alcance · despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados
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
Origen: 20261108-020932-3t5-alcance · despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada
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
Origen: 20261108-020932-3t5-alcance · despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance
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
