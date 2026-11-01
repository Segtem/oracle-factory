# Capability: calidad

## ADDED Requirements

### Requirement: la_puerta_detecta_secretos_en_todos_los_commits_que_se_publican
Tipo: funcional
El sistema DEBE buscar claves privadas, claves de AWS, tokens de GitHub, PyPI y Slack, claves de Google y claves tipo sk-, y asignaciones sospechosas de un valor largo a un nombre como token, secret, password o api_key, en las líneas agregadas por cada commit del rango que se va a publicar, mostrar archivo, línea, commit y tipo con el valor tapado, y fallar si encuentra alguno.

#### Scenario: un secreto agregado y quitado después
- DADO un rango de dos commits donde el primero agrega un token de GitHub y el segundo lo quita
- CUANDO se corre la puerta sobre el rango
- ENTONCES falla nombrando el archivo, la línea y el commit que lo agregó, sin imprimir el token entero

#### Scenario: palabras que no son secretos
- DADO un rango cuyas líneas agregadas dicen «secreto», «token» o «password» como palabras, sin un valor con forma de credencial
- CUANDO se corre la puerta
- ENTONCES no se encuentra ningún secreto

#### Scenario: una línea con la marca de exención
- DADO una línea agregada con un valor con forma de token y la marca factory:secreto-ok
- CUANDO se corre la puerta
- ENTONCES esa línea no cuenta

### Requirement: la_puerta_corre_las_verificaciones_del_proyecto
Tipo: funcional
El sistema DEBE correr agentes --verificar, kb --verificar y resumen --verificar, informar cuál falló y por qué, y fallar si alguna falla.

#### Scenario: todo al día
- DADO un proyecto con la guía para agentes, el conocimiento y el resumen al día
- CUANDO se corre la puerta
- ENTONCES las tres verificaciones pasan y la puerta sale con éxito

#### Scenario: una guía vieja
- DADO un proyecto cuya guía para agentes está vieja
- CUANDO se corre la puerta
- ENTONCES la puerta falla nombrando la verificación de la guía y las demás se informan igual

### Requirement: el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja
Tipo: funcional
El sistema DEBE instalar con oracle-factory hooks un hook pre-push que corre la puerta sobre los commits que se van a empujar, que bloquea el push si la puerta falla, que no hace nada al borrar una rama remota, que no pisa un hook pre-push ajeno, y que deja pasar con un aviso si el intérprete de Factory no está.

#### Scenario: un push con un secreto
- DADO el hook instalado y un commit con un token en una rama
- CUANDO se empuja esa rama
- ENTONCES el push se bloquea y el mensaje nombra el archivo y el tipo

#### Scenario: un push limpio y una rama nueva
- DADO el hook instalado y una rama nueva sin secretos
- CUANDO se empuja
- ENTONCES el push pasa, y se miran sólo los commits que el remoto todavía no tiene

#### Scenario: un hook ajeno y un intérprete que falta
- DADO un hook pre-push que no es de Factory, o un intérprete que ya no existe
- CUANDO se corre oracle-factory hooks, o se empuja con el intérprete borrado
- ENTONCES no se pisa el hook ajeno, y con el intérprete borrado el push pasa con un aviso
