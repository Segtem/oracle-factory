# Capability: procedencia

## ADDED Requirements

### Requirement: sin_autorizacion_de_red_no_se_consulta_osv
Tipo: funcional
El sistema DEBE negarse a consultar OSV.dev si la persona no pasó la bandera explícita de red, sin abrir ninguna conexión ni guardar archivo alguno.

#### Scenario: sin la bandera de red
- DADO inventarios guardados y un servidor de avisos que registra cada conexión
- CUANDO se pide consultar OSV sin la bandera de red
- ENTONCES el comando falla pidiendo la autorización, el servidor no recibe ninguna conexión y no se crea archivo de avisos

### Requirement: la_consulta_a_osv_guarda_avisos_validos_y_audita
Tipo: funcional
El sistema DEBE consultar OSV, por cada nombre y versión distintos de los inventarios guardados, enviando sólo nombre, versión y ecosistema; guardar los avisos recibidos en un archivo OSV válido, y listar los cambios y candidatos que usaron una versión afectada.

#### Scenario: una dependencia afectada
- DADO un candidato cuyo inventario tiene una versión que el servidor de avisos declara afectada
- CUANDO se consulta OSV con la bandera de red
- ENTONCES el archivo guardado es un aviso OSV válido y el resultado nombra ese cambio y candidato como expuesto

#### Scenario: nada de más sale hacia el servicio
- DADO inventarios guardados de varios cambios y candidatos
- CUANDO se consulta OSV con la bandera de red
- ENTONCES las consultas recibidas contienen sólo nombre, versión y ecosistema de cada dependencia distinta, una vez cada una

#### Scenario: sin avisos
- DADO inventarios cuyas dependencias el servidor no reconoce como afectadas
- CUANDO se consulta OSV con la bandera de red
- ENTONCES el resultado dice cuántas dependencias se consultaron y que no hay expuestos, y no se guarda archivo porque no hay avisos que guardar

### Requirement: un_fallo_de_consulta_no_se_lee_como_sin_afectados
Tipo: funcional
El sistema DEBE terminar con error, indicando el motivo y sin guardar archivo, ante cualquier fallo de la consulta, y nunca informar «sin afectados» por no haber podido consultar.

#### Scenario: el servicio no responde o responde mal
- DADO un servidor que cierra la conexión, responde con error HTTP, responde algo que no es JSON o devuelve un aviso OSV inválido
- CUANDO se consulta OSV con la bandera de red
- ENTONCES el comando falla con el motivo, no dice «sin afectados» y no deja un archivo de avisos nuevo ni parcial

#### Scenario: no hay inventarios guardados
- DADO un proyecto sin inventarios de procedencia guardados
- CUANDO se consulta OSV con la bandera de red
- ENTONCES el comando falla diciendo que no hay nada que consultar, sin conectarse
