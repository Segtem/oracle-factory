# Capability: trazabilidad

## ADDED Requirements

### Requirement: el trailer elige bien el cambio
Tipo: funcional
El hook SHALL elegir el cambio del trailer `Cambio:` en este orden: si el mensaje nombra el ID de un cambio del proyecto, ése (y si nombra varios, ninguno); si no, el único cambio abierto del checkout; si hay varios abiertos, el único que tiene como responsable a la persona que hace el commit (su nombre en la configuración de Git). En cualquier otro caso SHALL NOT agregar el trailer.

#### Scenario: un merge que nombra el cambio que integra
- GIVEN un checkout con un cambio abierto A y un commit cuyo mensaje dice «Integrar <ID de B>», con B cerrado
- WHEN se hace el commit
- THEN lleva «Cambio: <ID de B>», no el de A

#### Scenario: varios abiertos y uno tomado por quien commitea
- GIVEN dos cambios abiertos, uno tomado por la persona que hace el commit y otro sin responsable
- WHEN esa persona hace un commit que no nombra ningún cambio
- THEN lleva el cambio que tomó; y si no tomó ninguno, no lleva trailer
