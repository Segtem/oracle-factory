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

### Requirement: importar no trae lo que la spec retira
Tipo: funcional
Los requisitos de la sección `## REMOVED Requirements` de la spec de un cambio SHALL quedar fuera de su importación: `importar` no los registra entre los requisitos del cambio ni deja sus archivos en `requisitos/`, porque lo que se retira no se mide; se retiran de la spec consolidada al cerrar.

#### Scenario: una spec que retira un requisito
- GIVEN una spec aprobada con un requisito en ADDED y otro en REMOVED
- WHEN se ejecuta `importar`
- THEN sólo queda importado el de ADDED, y no hay archivo de requisito para el retirado
