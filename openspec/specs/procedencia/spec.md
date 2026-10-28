# Capability: procedencia

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: el_inventario_dice_que_hay_y_de_donde_viene
Origen: 20261028-150627-lva-procedencia · procedencia_c3331f4b36e5b7938.el_inventario_dice_que_hay_y_de_donde_viene
Tipo: funcional
El sistema DEBE producir un inventario CycloneDX de las dependencias de Python del proyecto que diga, de cada componente, su nombre, su versión, su enlace pkg:pypi, su índice de origen, los hashes de sus archivos, si la versión está fijada y de dónde sale cada dato.

#### Scenario: un proyecto con lock
- DADO un proyecto con un lock que registra dos dependencias con su origen y los hashes de sus archivos
- CUANDO se corre `oracle-factory procedencia`
- ENTONCES el inventario lista los dos componentes con su versión, su enlace pkg:pypi, su índice, los hashes del lock y la marca de que el dato sale del lock

#### Scenario: un proyecto sin lock
- DADO un proyecto con dependencias instaladas y sin lock
- CUANDO se corre `oracle-factory procedencia`
- ENTONCES los componentes salen del entorno instalado, sin hashes ni origen verificables, y el inventario lo dice

#### Scenario: una versión corregida por Lightwell
- DADO una dependencia cuya versión lleva el sufijo de una corrección de Lightwell
- CUANDO se arma el inventario
- ENTONCES el componente se marca como corregido por Lightwell y conserva la versión tal como está

### Requirement: un_lock_desactualizado_se_declara_no_confiable
Origen: 20261028-150627-lva-procedencia · procedencia_c3331f4b36e5b7938.un_lock_desactualizado_se_declara_no_confiable
Tipo: funcional
El sistema DEBE declarar no confiable el inventario, listando las diferencias, cuando el lock no coincide con lo que pide el proyecto o con lo que está instalado.

#### Scenario: el lock difiere de lo que pide el proyecto
- DADO un lock que fija una versión distinta de la que `pyproject.toml` exige
- CUANDO se corre `oracle-factory procedencia`
- ENTONCES el inventario se declara no confiable y nombra la dependencia, la versión del lock y la exigida

#### Scenario: el lock difiere de lo instalado
- DADO un entorno con una versión instalada distinta de la del lock
- CUANDO se corre `oracle-factory procedencia`
- ENTONCES se declara no confiable y nombra la versión instalada y la del lock

#### Scenario: todo coincide
- DADO un lock, un `pyproject.toml` y un entorno que coinciden
- CUANDO se corre `oracle-factory procedencia`
- ENTONCES el inventario se declara confiable y sin diferencias

### Requirement: el_inventario_queda_en_el_candidato
Origen: 20261028-150627-lva-procedencia · procedencia_c3331f4b36e5b7938.el_inventario_queda_en_el_candidato
Tipo: funcional
El sistema DEBE guardar el inventario en la carpeta del candidato de un cambio cuando se indica su identificador, y dejar en el registro un evento con su huella, sin pisar un inventario anterior de otro candidato.

#### Scenario: guardar el inventario de un cambio
- DADO un cambio con un candidato vigente
- CUANDO se corre `oracle-factory procedencia ID`
- ENTONCES el inventario queda en la carpeta del candidato y el registro suma un evento con la huella del archivo

#### Scenario: un segundo candidato
- DADO un cambio que ya tiene un inventario guardado de un candidato anterior
- CUANDO se guarda el inventario de un candidato nuevo
- ENTONCES el inventario anterior se conserva sin cambios

### Requirement: se_busca_quien_uso_una_dependencia
Origen: 20261028-150627-lva-procedencia · procedencia_c3331f4b36e5b7938.se_busca_quien_uso_una_dependencia
Tipo: funcional
El sistema DEBE decir, con `procedencia --buscar`, qué candidatos y qué cambios tienen en su inventario guardado un paquete y, si se indica, una versión.

#### Scenario: un paquete y una versión
- DADO dos candidatos con inventarios guardados que difieren en la versión de un paquete
- CUANDO se busca ese paquete con una versión
- ENTONCES se listan solo los candidatos y cambios que usaron esa versión

#### Scenario: un paquete que nadie usó
- DADO inventarios guardados que no incluyen un paquete
- CUANDO se lo busca
- ENTONCES el resultado dice que ningún candidato lo usó

### Requirement: se_audita_contra_avisos_sin_red
Origen: 20261028-150627-lva-procedencia · procedencia_c3331f4b36e5b7938.se_audita_contra_avisos_sin_red
Tipo: funcional
El sistema DEBE cruzar los inventarios guardados con un archivo de avisos en formato OSV, sin acceder a la red, y listar los componentes afectados, sus versiones corregidas y los candidatos y cambios afectados.

#### Scenario: un aviso que afecta a un candidato
- DADO un archivo de avisos que declara afectada una versión de un paquete y un candidato que la usó
- CUANDO se corre `oracle-factory procedencia --auditar --avisos ARCHIVO`
- ENTONCES se listan el aviso, el componente, la versión corregida y el candidato afectado

#### Scenario: un aviso que no afecta
- DADO un archivo de avisos sobre versiones que ningún candidato usó
- CUANDO se audita
- ENTONCES el resultado dice que no hay candidatos afectados

#### Scenario: un archivo de avisos inválido
- DADO un archivo de avisos que no es OSV válido
- CUANDO se audita
- ENTONCES falla diciendo qué está mal, sin informar un resultado vacío como si fuera limpio
