# Capability: tablero

## ADDED Requirements

### Requirement: el_tablero_muestra_cada_destino_con_su_estado
Tipo: funcional
El tablero DEBE mostrar una sección «Destinos» con, por cada destino, su nombre, tipo, estado, versión desplegada y esperada, si está al día, desactualizado o con versión desconocida, de qué otros depende y su última prueba, más el resumen de la última corrida (quién la autorizó, resultado y motivo), todo escapado como texto.

#### Scenario: tres destinos con estados distintos
- DADO un proyecto con un VPS probado, una app desplegada y un ESP32 fallido
- CUANDO se arma el tablero
- ENTONCES los tres aparecen con su estado, y el de versión desconocida no se muestra como «al día»

#### Scenario: texto con marcas
- DADO un destino cuyo nombre o motivo trae `<script>` o comillas
- CUANDO se dibuja la sección
- ENTONCES se ve como texto y no se interpreta

### Requirement: el_tablero_no_consulta_los_destinos_sin_que_se_pida
Tipo: funcional
El tablero DEBE armar la sección con lo registrado, sin correr los comandos `version` de los destinos, y DEBE consultarlos sólo cuando la persona aprieta «Consultar ahora».

#### Scenario: repintar no toca los destinos
- DADO un destino cuyo comando `version` deja una marca en disco cuando corre
- CUANDO el tablero se arma o se repinta varias veces
- ENTONCES la marca no aparece

#### Scenario: consultar a pedido
- DADO el mismo destino
- CUANDO la persona aprieta «Consultar ahora»
- ENTONCES el comando corre una vez y el tablero muestra la versión que respondió

### Requirement: el_tablero_no_despliega_ni_autoriza
Tipo: funcional
El tablero DEBE ofrecer los pasos de despliegue sólo como comandos que se escriben en la terminal sin ejecutarlos, y NUNCA debe desplegar ni autorizar un despliegue por sí mismo; ni quien se une por Live Share puede hacerlo desde su panel.

#### Scenario: los botones sólo escriben
- DADO la sección Destinos dibujada
- CUANDO se miran sus botones
- ENTONCES cada uno es «escribir en la terminal» con `oracle-factory desplegar --simular` o `oracle-factory desplegar --autorizar`, o «Consultar ahora» que sólo lee

#### Scenario: el invitado no consulta
- DADO una sesión de Live Share en la que el panel es de un invitado
- CUANDO se dibuja la sección
- ENTONCES no tiene «Consultar ahora» y los comandos se escriben en la terminal de quien comparte

### Requirement: sin_destinos_o_con_error_el_tablero_sigue
Tipo: funcional
El tablero DEBE seguir mostrando los cambios, y no fallar, cuando el proyecto no tiene destinos declarados (y decir cómo declararlos) o cuando la declaración es inválida (y decir el motivo).

#### Scenario: proyecto sin destinos
- DADO un proyecto sin `.factory/destinos.json`
- CUANDO se arma el tablero
- ENTONCES la sección dice cómo declarar destinos y los cambios se ven

#### Scenario: declaración inválida
- DADO un `destinos.json` con un destino sin comando de desplegar
- CUANDO se arma el tablero
- ENTONCES la sección muestra el motivo de la CLI y los cambios se ven

### Requirement: el_contrato_de_la_extension_cubre_destinos
Tipo: funcional
El contrato entre la CLI y la extensión DEBE declarar las claves de `destinos --json` que lee la extensión, y la suite DEBE fallar si la extensión lee una no declarada o la CLI deja de entregar una declarada.

#### Scenario: la CLI cambia una clave
- DADO el contrato de `destinos`
- CUANDO la CLI entrega `destinos --json` sin una clave declarada, o con otro tipo
- ENTONCES la comprobación nombra el comando y la clave

#### Scenario: la extensión lee de más
- DADO el código de `tablero.js`
- CUANDO lee una clave de destinos que el contrato no declara
- ENTONCES la comprobación del código la nombra
