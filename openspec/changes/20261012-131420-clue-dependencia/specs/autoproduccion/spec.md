# Capability: autoproduccion

## REMOVED Requirements

### Requirement: los informes se validan o se marcan

## ADDED Requirements

### Requirement: oracle-clue viene con Factory
Tipo: funcional
Instalar `oracle-factory` SHALL instalar `oracle-clue` en una versión fijada, y Factory SHALL usar el Clue de su propio entorno (no uno del `PATH`) para preparar paquetes y validar informes.

#### Scenario: instalación sola
- GIVEN un entorno donde sólo se instaló `oracle-factory`, sin `oracle-clue` en el `PATH`
- WHEN se ejecuta `pedir-revision` con un revisor configurado
- THEN el paquete se prepara y el informe se valida con el Clue instalado con Factory

### Requirement: los informes de revisores siempre se validan
Tipo: funcional
Cada informe de revisor SHALL validarse con Clue contra su paquete antes de usarse; un informe ilegible, inválido, de otro candidato o que no se puede validar (por ejemplo, porque falta su paquete o su checkout) SHALL avisarse y no usarse. No hay informes «sin validar».

#### Scenario: informe que no se puede validar
- GIVEN un candidato con un informe de revisor cuyo paquete no está
- WHEN se ejecuta `revision-preparar`
- THEN se avisa y sus hallazgos no entran al informe
