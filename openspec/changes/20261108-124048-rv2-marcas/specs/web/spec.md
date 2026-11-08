# Capability: web

## ADDED Requirements

### Requirement: el_comprobador_del_sitio_rechaza_un_bloque_marcado_duplicado
Tipo: funcional
El sistema DEBE hacer que `tools/sitio_paginas.py` rechace, nombrando la página y el bloque, toda página donde los marcadores de un bloque generado (`menu`, `pie`, `leer` o `ruta`) aparezcan más de una vez, aunque el primer bloque coincida con la tabla; una página con una sola pareja bien formada NO DEBE recibir ese rechazo.

#### Scenario: una segunda pareja alterada
- DADO una copia del sitio donde una página repite la pareja del menú con otro contenido
- CUANDO se corre el comprobador
- ENTONCES falla nombrando la página y el bloque «menu»

#### Scenario: una apertura o un cierre repetidos
- DADO una página con una segunda apertura, o un segundo cierre, del mismo bloque
- CUANDO se corre el comprobador
- ENTONCES falla nombrando la página y el bloque

#### Scenario: un bloque que la página no debe tener
- DADO la portada con dos parejas del bloque «leer», o una guía con dos del bloque «ruta»
- CUANDO se corre el comprobador
- ENTONCES falla nombrando la página y el bloque

#### Scenario: el sitio actual sigue pasando
- DADO el repositorio sin tocar
- CUANDO se corre el comprobador
- ENTONCES no hay problemas
