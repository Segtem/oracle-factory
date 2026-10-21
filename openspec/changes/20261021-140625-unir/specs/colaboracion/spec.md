# Capability: colaboracion

## ADDED Requirements

### Requirement: el registro de un cambio editado en dos ramas se une sin perder nada
Tipo: funcional
Con los hooks de Factory instalados, al integrar dos ramas que editaron el registro de un mismo cambio, Git SHALL unirlo con Factory sin conflicto de texto: todos los eventos de las dos ramas SHALL quedar, sin repetirse y en orden; y lo que cambió una sola rama SHALL tomarse de esa rama.

#### Scenario: dos ramas que dejaron mensajes en el mismo cambio
- GIVEN un cambio cuyo registro tiene un mensaje nuevo en la rama de Ana y otro en la de Beto
- WHEN se integran las dos ramas
- THEN no hay conflicto y el registro tiene los dos mensajes y todos los eventos anteriores, una sola vez cada uno

### Requirement: si las dos ramas decidieron distinto, decide una persona
Tipo: funcional
Si al unir el registro las dos ramas decidieron distinto sobre lo mismo (por ejemplo, dos responsables o dos aprobaciones), Factory SHALL NOT elegir en silencio: SHALL conservar en el registro lo de las dos ramas, `estado` SHALL avisar qué hay que decidir y cómo, y la decisión de una persona que corresponde SHALL resolverlo.

#### Scenario: los dos tomaron el mismo cambio en sus clones
- GIVEN un cambio que Ana tomó en su clon y Beto en el suyo
- WHEN se integran las dos ramas
- THEN el registro conserva los dos «tomado», estado avisa que hay dos responsables y cómo acordarlo, y cuando una de las personas lo toma con --relevo el aviso desaparece

### Requirement: lo generado no choca al integrar
Tipo: funcional
Al integrar dos ramas, `.factory/resumen.md` y las notas generadas de `kb/` SHALL NOT dejar conflictos de texto: Factory SHALL rehacerlos después del merge, de modo que `resumen --verificar` y `kb --verificar` pasen sin editar nada a mano.

#### Scenario: dos cambios integrados uno tras otro
- GIVEN dos ramas con un cambio cada una, con resumen.md y kb/ regenerados en cada rama
- WHEN se integran las dos
- THEN no hay conflicto en resumen.md ni en kb/, y después del merge resumen --verificar y kb --verificar pasan
