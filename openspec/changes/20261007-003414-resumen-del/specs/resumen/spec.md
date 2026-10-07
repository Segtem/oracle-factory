# Capability: resumen

## ADDED Requirements

### Requirement: el resumen muestra lo vigente y lo pendiente
Tipo: funcional
`oracle-factory resumen` SHALL escribir `.factory/resumen.md` con los requisitos vigentes de cada capacidad (tipo, requisito de Oracle, cambio de origen, medidas y veredicto), los cambios abiertos con su fase, su modo y lo que les falta para cerrar, y un enlace a la spec consolidada de cada capacidad, sin copiar sus escenarios.

#### Scenario: proyecto con capacidades archivadas y cambios abiertos
- GIVEN un proyecto con una capacidad archivada y un cambio abierto
- WHEN se ejecuta `resumen`
- THEN el resumen lista los requisitos vigentes de la capacidad con sus medidas y el cambio abierto con lo que le falta, y no contiene los escenarios

#### Scenario: requisito reemplazado
- GIVEN un requisito que un cambio posterior reemplazó
- WHEN se ejecuta `resumen`
- THEN aparece sólo la versión vigente, con el cambio que la trajo

### Requirement: riesgos aceptados y límites declarados
Tipo: funcional
El resumen SHALL listar los riesgos aceptados (decisiones de revisión con estado `riesgo_aceptado`, con su motivo y quién decidió) y los límites declarados en los informes de revisión de los cambios cerrados, separando los de cambios que todavía tienen requisitos vigentes de los históricos.

#### Scenario: riesgo de un cambio con requisitos reemplazados
- GIVEN un cambio cerrado con un riesgo aceptado cuyos requisitos fueron todos reemplazados
- WHEN se ejecuta `resumen`
- THEN el riesgo aparece entre los históricos, con su motivo y quién lo aceptó

### Requirement: el veredicto es el del cierre y lo dice
Tipo: funcional
Para cada requisito vigente, el resumen SHALL mostrar el veredicto registrado al cerrar el cambio del que viene, con ese cambio y su fecha, y SHALL decir que no es una corrida nueva; si el cambio no registró veredicto, SHALL decirlo en vez de inventarlo.

#### Scenario: cambio cerrado con veredicto verde
- GIVEN un requisito vigente de un cambio cerrado con veredicto verde
- WHEN se ejecuta `resumen`
- THEN el requisito muestra el veredicto, el cambio y la fecha del cierre, y el resumen aclara que no es una corrida nueva

### Requirement: el resumen es determinista y no cambia nada más
Tipo: no funcional
Con los mismos registros, `resumen` SHALL producir los mismos bytes, sin fecha ni commit, sin red ni modelos de lenguaje; SHALL NOT modificar ningún otro archivo, y `.factory/resumen.md` SHALL quedar fuera de la huella del producto.

#### Scenario: dos ejecuciones seguidas
- GIVEN un resumen recién generado
- WHEN se ejecuta `resumen` otra vez sin cambios en los registros
- THEN el archivo queda byte a byte igual y ninguna revisión vence

### Requirement: se sabe cuándo quedó viejo
Tipo: funcional
El resumen SHALL llevar la huella de lo que resume, y `resumen --verificar` SHALL terminar con código distinto de cero, sin escribir, cuando el resumen falta o no coincide con los registros actuales.

#### Scenario: un cambio avanza después de generar el resumen
- GIVEN un resumen generado
- WHEN un cambio abierto avanza de fase y se ejecuta `resumen --verificar`
- THEN termina con código distinto de cero y no modifica el archivo

### Requirement: se actualiza al cerrar y al archivar
Tipo: funcional
`cerrar` y `archivar` SHALL regenerar `.factory/resumen.md` después de fusionar la spec, y `resumen --salida RUTA` SHALL escribirlo en la ruta indicada dentro del proyecto.

#### Scenario: cerrar un cambio
- GIVEN un cambio listo para cerrar
- WHEN la persona lo cierra
- THEN `.factory/resumen.md` ya incluye sus requisitos como vigentes y `resumen --verificar` termina con éxito

### Requirement: este repositorio tiene su resumen al día
Tipo: no funcional
Este repositorio SHALL tener `.factory/resumen.md` al día, y un verificador SHALL comprobarlo junto con las pruebas del contrato.

#### Scenario: verificación sobre este repositorio
- GIVEN este repositorio con su resumen generado
- WHEN se corre el verificador
- THEN `resumen --verificar` termina con éxito
