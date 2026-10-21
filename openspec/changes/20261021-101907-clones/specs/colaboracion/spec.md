# Capability: colaboracion

## ADDED Requirements

### Requirement: un clon recién hecho puede trabajar
Tipo: funcional
`init` SHALL dejar versionables las carpetas que crea, y en un clon recién hecho de un proyecto inicializado (o de uno viejo al que le falten esas carpetas) `nuevo` SHALL poder crear un cambio.

#### Scenario: la segunda persona clona el proyecto
- GIVEN un proyecto recién inicializado y subido, y una persona que lo clona
- WHEN corre nuevo en su clon, y también en un clon de un proyecto viejo sin tareas/
- THEN el cambio se crea en los dos

### Requirement: dos clones no generan el mismo ID
Tipo: funcional
El ID de un cambio nuevo SHALL llevar, después del sufijo, tres caracteres al azar, de modo que dos clones que crean un cambio en el mismo segundo con el mismo sufijo no generen el mismo ID.

#### Scenario: dos cambios en el mismo segundo
- GIVEN dos clones del mismo proyecto
- WHEN los dos crean a la vez un cambio con el mismo sufijo, y se integran
- THEN los IDs son distintos y la integración no choca

### Requirement: escribir a la vez no obliga a repetir
Tipo: funcional
`mensaje`, `tomar` y `soltar` SHALL reintentar solos cuando el registro del cambio cambió mientras escribían, volviendo a leerlo y a comprobar sus reglas, de modo que escrituras simultáneas sobre un mismo registro se guarden todas sin que nadie las repita; y SHALL fallar con un mensaje claro si no lo logran tras varios intentos.

#### Scenario: doce mensajes a la vez
- GIVEN un cambio y doce procesos que dejan un mensaje en su registro a la vez
- WHEN terminan
- THEN el registro tiene los doce mensajes y ninguno falló
