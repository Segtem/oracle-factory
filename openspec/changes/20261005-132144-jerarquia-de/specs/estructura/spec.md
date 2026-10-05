# Capability: estructura

## ADDED Requirements

### Requirement: estructura documentada
Tipo: funcional
La documentación SHALL describir dónde va cada artefacto de un proyecto Factory: `.factory/cambios/<ID>/` con una carpeta por candidato (`candidatos/<sha7>/` con evidencia, paquete de Clue y revisión), `.factory/local/revisiones/<sha7>/` para los checkouts de revisión, el acuerdo humano en `openspec/changes/<ID>/`, y las carpetas de Task y de Oracle en la raíz.

#### Scenario: una persona busca la evidencia de un candidato
- GIVEN un cambio con evidencia producida sobre un commit
- WHEN la persona consulta la documentación de estructura
- THEN sabe en qué carpeta está esa evidencia sin conocer la historia del cambio

### Requirement: carpeta propia de Factory
Tipo: funcional
`init` SHALL crear `.factory/` en la raíz del proyecto con `cambios/` y `local/` y dejar en ella un archivo versionado que la explique (Git no versiona carpetas vacías), SHALL agregar `.factory/local/` al `.gitignore` sin sobrescribir lo existente, SHALL rechazar con un mensaje claro y antes de crear nada un `.factory` que no sea una carpeta, y SHALL avisar cuando la carpeta está dentro de otro proyecto Factory.

#### Scenario: proyecto nuevo
- GIVEN una carpeta sin `.factory/`
- WHEN se ejecuta init
- THEN existen `.factory/cambios/` y `.factory/local/`, y `.factory/local/` está ignorada por Git

#### Scenario: proyecto ya inicializado
- GIVEN un proyecto Factory existente sin `.factory/` y con un `.gitignore` propio
- WHEN se ejecuta init
- THEN se agrega `.factory/` y la línea de ignore, y el resto del `.gitignore` queda intacto

#### Scenario: clon de un proyecto
- GIVEN un proyecto inicializado con `.factory/` y commiteado
- WHEN se clona
- THEN el clon tiene `.factory/` y los comandos la descubren desde una subcarpeta del clon

#### Scenario: .factory que no es una carpeta
- GIVEN un archivo llamado `.factory` en la raíz
- WHEN se ejecuta init
- THEN Factory lo rechaza con un mensaje claro y no crea ninguna otra carpeta

#### Scenario: init dentro de otro proyecto
- GIVEN una subcarpeta de un proyecto Factory
- WHEN se ejecuta init en ella
- THEN se crea un proyecto anidado y se avisa que los comandos usarán el más cercano

### Requirement: descubrir la raíz del proyecto
Tipo: funcional
Los comandos SHALL buscar `.factory/` subiendo desde la carpeta actual hasta la raíz del sistema de archivos y usar la primera que encuentren; `--proyecto` SHALL tener prioridad y, sin `.factory/` en ningún ancestro, SHALL conservarse el comportamiento actual de usar la carpeta actual. Un proyecto Factory anterior sin `.factory/` (con `oracle.json` y `openspec/changes/`) SHALL ser una frontera: no hereda el proyecto de afuera. La carpeta personal del usuario y un enlace simbólico llamado `.factory` SHALL NOT contar como raíz. Cuando la raíz usada no es la carpeta actual, SHALL informarlo.

#### Scenario: comando desde una subcarpeta
- GIVEN un proyecto con `.factory/` y una subcarpeta del producto
- WHEN se ejecuta estado desde la subcarpeta
- THEN Factory usa la raíz del proyecto e informa cuál es

#### Scenario: proyecto explícito
- GIVEN un directorio dentro de un proyecto y otro proyecto indicado con --proyecto
- WHEN se ejecuta un comando con --proyecto
- THEN se usa el proyecto indicado y no el del ancestro

#### Scenario: sin carpeta de Factory
- GIVEN un proyecto anterior sin `.factory/` en ningún ancestro
- WHEN se ejecuta un comando desde su raíz
- THEN se comporta como hasta ahora

#### Scenario: proyecto anterior dentro de otro
- GIVEN un proyecto sin `.factory/` dentro de otro que sí la tiene
- WHEN se ejecuta un comando desde el proyecto de adentro
- THEN se usa el de adentro y no el de afuera

#### Scenario: carpeta personal
- GIVEN una `.factory/` en la carpeta personal del usuario y un proyecto debajo de ella sin `.factory/` propia
- WHEN se ejecuta un comando en ese proyecto
- THEN la carpeta personal no se usa como raíz

#### Scenario: enlace simbólico
- GIVEN un enlace simbólico llamado `.factory`
- WHEN los comandos buscan la raíz
- THEN no lo cuentan como marcador de proyecto

### Requirement: lo versionado y lo local
Tipo: no funcional
Lo que Factory guarda bajo `.factory/` fuera de `local/` SHALL ser versionable y portátil, sin rutas absolutas, y lo que es de una máquina SHALL ir en `.factory/local/`, ignorada por Git.

#### Scenario: otra máquina
- GIVEN un clon de un proyecto en otra ruta absoluta
- WHEN se consultan los artefactos de `.factory/cambios/`
- THEN las rutas que contienen son relativas a la raíz y se resuelven en el clon

### Requirement: la huella del producto excluye lo que Factory produce
Tipo: funcional
La huella de archivos del producto SHALL excluir `.factory/` entera, y SHALL NOT excluir `openspec/changes/<ID>/` salvo los registros que ya excluye.

#### Scenario: nueva evidencia no invalida la revisión
- GIVEN una revisión registrada
- WHEN se agrega evidencia o un paquete de Clue bajo `.factory/cambios/<ID>/`
- THEN la huella del producto no cambia y la revisión sigue vigente

#### Scenario: el acuerdo sigue siendo producto
- GIVEN una revisión registrada
- WHEN cambia la spec en `openspec/changes/<ID>/`
- THEN la revisión queda desactualizada

### Requirement: donde esta cada artefacto
Tipo: funcional
`oracle-factory donde ID` SHALL listar cada artefacto del cambio con su ruta, si existe y qué gate respalda; con `--candidato SHA` SHALL limitarse a ese candidato y SHALL marcar como históricos los artefactos con nombres anteriores a esta estructura.

#### Scenario: cambio con revisión registrada
- GIVEN un cambio con spec aceptada, evidencia y una revisión registrada
- WHEN se ejecuta donde con su ID
- THEN aparecen la propuesta, la spec, los requisitos, la evidencia y el informe de revisión, cada uno con su gate y su ruta

#### Scenario: artefacto ausente
- GIVEN un registro de Factory que referencia un informe que ya no existe
- WHEN se ejecuta donde
- THEN el artefacto aparece marcado como ausente, sin ocultarlo

#### Scenario: cambio anterior a la estructura
- GIVEN un cambio con carpetas como evidencia-mapeo o revision-pendiente
- WHEN se ejecuta donde
- THEN esos artefactos aparecen como históricos y no se mueven

#### Scenario: registro con valores no válidos
- GIVEN un registro de cambio con valores que no son rutas de texto
- WHEN se ejecuta donde
- THEN se listan los artefactos válidos y los no válidos se marcan, sin un error interno

### Requirement: ruta canonica para producir artefactos
Tipo: funcional
`oracle-factory ruta ID TIPO` SHALL imprimir la ruta canónica para producir un artefacto de ese tipo (evidencia, clue, revision o checkout) sobre el HEAD actual, nombrando la carpeta del candidato con los 7 primeros caracteres del hash completo del commit, sin crear ni modificar archivos.

#### Scenario: sensor que escribe su evidencia
- GIVEN un cambio abierto y un HEAD
- WHEN se usa ruta con el tipo evidencia como salida del sensor
- THEN la ruta es `.factory/cambios/<ID>/candidatos/<sha7>/evidencia` y donde la encuentra

#### Scenario: checkout de revisión
- GIVEN un HEAD
- WHEN se usa ruta con el tipo checkout
- THEN imprime `.factory/local/revisiones/<sha7>` y no crea nada

#### Scenario: tipo desconocido
- GIVEN un tipo que no está en la estructura
- WHEN se ejecuta ruta
- THEN Factory lo rechaza nombrando los tipos válidos

### Requirement: buscar en todo el proyecto
Tipo: funcional
`oracle-factory buscar TEXTO` SHALL buscar en propuestas, specs, requisitos, tareas y registros de Factory, y SHALL mostrar por resultado la ruta, la línea y el cambio al que pertenece.

#### Scenario: texto presente en varios cambios
- GIVEN un texto que aparece en la spec de un cambio y en la tarea de otro
- WHEN se busca
- THEN aparecen los dos resultados, cada uno con su cambio, ruta y línea

#### Scenario: archivos que no se pudieron leer
- GIVEN un archivo de texto que supera el tamaño máximo de búsqueda y contiene el texto
- WHEN se busca
- THEN el resultado informa cuántos archivos se omitieron por tamaño

#### Scenario: mayúsculas y formas equivalentes
- GIVEN un texto con «Straße» en un archivo
- WHEN se busca «STRASSE»
- THEN aparece el resultado

### Requirement: listar con filtros
Tipo: funcional
`oracle-factory listar` SHALL aceptar filtros por fase y por estado abierto o cerrado, sin cambiar su salida cuando no se usan filtros.

#### Scenario: cambios abiertos
- GIVEN cambios abiertos y cerrados
- WHEN se lista con el filtro de abiertos
- THEN sólo aparecen los abiertos

### Requirement: respetar lo existente
Tipo: no funcional
Factory SHALL NOT mover, renombrar ni borrar artefactos existentes al adoptar la estructura, y `donde`, `ruta`, `buscar` y `listar` SHALL ser de sólo lectura.

#### Scenario: proyecto con cambios anteriores
- GIVEN un proyecto con cambios creados antes de la estructura
- WHEN se usan donde, ruta, buscar y listar
- THEN ningún archivo del proyecto cambia
