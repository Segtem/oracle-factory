# Capability: portabilidad

## ADDED Requirements

### Requirement: hechos con ruta relativa al proyecto
Tipo: funcional
`juzgar` SHALL guardar la ruta de los hechos relativa a la raíz del proyecto cuando están dentro de ella, y la verificación de los hechos SHALL resolver esa ruta desde la raíz del clon en que se ejecuta.

#### Scenario: hechos dentro del proyecto
- GIVEN unos hechos dentro del proyecto
- WHEN se juzga
- THEN el registro guarda una ruta relativa, sin la ruta de la máquina

#### Scenario: clon en otra ruta
- GIVEN un cambio juzgado y un clon del proyecto en otra ruta absoluta
- WHEN se consulta estado en el clon
- THEN los hechos se verifican por su huella y no figuran como ausentes

### Requirement: advertir cuando los hechos no viajan
Tipo: funcional
`juzgar` SHALL advertir, sin impedir el juicio, cuando los hechos están fuera de la raíz del proyecto o ignorados por Git, porque otra máquina no podrá verificarlos.

#### Scenario: hechos ignorados por Git
- GIVEN unos hechos dentro de una carpeta ignorada por Git
- WHEN se juzga
- THEN el juicio se registra y se advierte que los hechos no viajan con el repositorio

#### Scenario: hechos fuera del proyecto
- GIVEN unos hechos fuera de la raíz del proyecto
- WHEN se juzga
- THEN el juicio se registra con la ruta absoluta y se advierte que no será verificable en otra máquina

### Requirement: fuente de los requisitos relativa
Tipo: funcional
`importar` SHALL dejar la `fuente` de cada requisito importado relativa a la raíz del proyecto.

#### Scenario: requisito importado
- GIVEN una spec aceptada
- WHEN se importa
- THEN la fuente de cada requisito no contiene la ruta de la máquina

### Requirement: pendiente que explica cómo recuperarse
Tipo: funcional
Cuando faltan los hechos de un veredicto, el pendiente SHALL nombrar la ruta esperada y SHALL indicar que se recupera juzgando de nuevo con los hechos del clon.

#### Scenario: hechos ausentes
- GIVEN un veredicto cuyos hechos no existen en esta máquina
- WHEN se consulta estado
- THEN el pendiente nombra la ruta y dice cómo recuperarse

### Requirement: un cambio juzgado en una máquina se cierra desde otra
Tipo: funcional
Un cambio con spec aceptada, medidas, revisión y veredicto registrados en una máquina SHALL poder consultarse y cerrarse desde un clon en otra máquina, sin pendientes que dependan de rutas de la primera.

#### Scenario: dos máquinas con un remoto
- GIVEN una persona que juzga un cambio en una máquina y sube el repositorio, y otra que lo clona en otra máquina con otro usuario y otra ruta
- WHEN la segunda consulta estado y cierra el cambio
- THEN estado no tiene pendientes y el cierre se registra a nombre de la segunda persona

### Requirement: sin rutas privadas en lo versionado
Tipo: no funcional
Lo que Factory escribe en el repositorio SHALL NOT contener la ruta absoluta de la máquina que lo escribió.

#### Scenario: búsqueda de la ruta de otra máquina
- GIVEN un proyecto completo trabajado en una máquina
- WHEN se busca en lo versionado la ruta de esa máquina
- THEN no aparece

### Requirement: respetar los registros existentes
Tipo: no funcional
Factory SHALL NOT reescribir registros existentes ni exigir migración, y SHALL seguir leyendo los que tienen ruta absoluta.

#### Scenario: registro anterior con ruta absoluta
- GIVEN un veredicto registrado con una ruta absoluta que existe en esta máquina
- WHEN se consulta estado
- THEN se verifica como hasta ahora y el registro no se modifica
