# Capability: estructura

## MODIFIED Requirements

### Requirement: buscar en todo el proyecto
Tipo: funcional
`oracle-factory buscar TEXTO` SHALL buscar en propuestas, specs, requisitos, tareas y registros de Factory, y SHALL mostrar por resultado la ruta, la línea y el cambio al que pertenece. SHALL NOT recorrer la evidencia ni los paquetes de Clue de los candidatos (`evidencia/` y `clue/`), ni los JSON de `tareas/`: están atados a hashes y no se leen de corrido; los informes y pedidos de `revision/` sí se recorren.

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

#### Scenario: la evidencia no aparece
- GIVEN un texto que aparece en la evidencia de un candidato, en un paquete de Clue y en un informe de revisión del mismo candidato
- WHEN se busca
- THEN aparece sólo el del informe, y la evidencia y el paquete no cuentan como omitidos por tamaño
