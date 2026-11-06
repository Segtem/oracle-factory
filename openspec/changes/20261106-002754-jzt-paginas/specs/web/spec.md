# Capability: web

## ADDED Requirements

### Requirement: el_menu_es_el_mismo_en_todas_las_paginas
Tipo: funcional
El sistema DEBE mostrar en todas las páginas del sitio el mismo menú —los enlaces de la portada de siempre más Desde cero, Modos, En equipo, Simulación y Documentación—, con la página actual marcada con `aria-current="page"` y sólo ella, y DEBE generar el menú, el pie y los enlaces de lectura desde una sola tabla de páginas que un comprobador verifica contra los HTML.

#### Scenario: recorrer el menú desde cualquier página
- DADA cualquiera de las seis páginas
- CUANDO se leen los enlaces de su menú
- ENTONCES son los mismos que en las demás, todos llevan a algo que existe, y sólo el de la página actual está marcado

#### Scenario: una página que se salió de la tabla
- DADO un menú, un pie o un bloque de lectura editado a mano, o una página que no está en la tabla
- CUANDO se corre el comprobador
- ENTONCES falla nombrando la página y el bloque

### Requirement: cada_pagina_lleva_a_la_siguiente
Tipo: funcional
El sistema DEBE ordenar la lectura así: Desde cero, Modos, En equipo, Simulación, Documentación; cada una de esas páginas DEBE terminar con «Seguí leyendo», con enlace a la anterior y a la siguiente (la primera vuelve a la portada y la última a la portada), y la portada DEBE tener «Por dónde seguir» con las cinco páginas, una frase cada una, en ese orden; el pie DEBE enlazar todas las páginas.

#### Scenario: seguir la lectura de punta a punta
- DADA la guía «Desde cero»
- CUANDO se sigue el enlace «siguiente» de cada página hasta el final
- ENTONCES se pasa por las cinco páginas en el orden dicho y se termina en la portada, y cada «anterior» vuelve a la página de la que se vino

#### Scenario: llegar a la lectura desde la portada
- DADA la portada
- CUANDO se mira «Por dónde seguir»
- ENTONCES enlaza las cinco páginas en orden, cada una con su frase

### Requirement: toda_la_documentacion_esta_en_la_web
Tipo: funcional
El sistema DEBE tener una página `documentacion.html` que liste cada guía de `docs/` con su título tal como figura en la guía, una frase y su enlace, agrupadas en cuatro grupos, y DEBE fallar el comprobador si falta una guía, si sobra un enlace a una guía que no existe o si un título no coincide.

#### Scenario: se agrega una guía y no se lista
- DADA una guía nueva en `docs/`
- CUANDO se corre el comprobador
- ENTONCES falla nombrando la guía

#### Scenario: la página lista todo
- DADA la página de documentación
- CUANDO se cuentan sus guías
- ENTONCES están las 12 de `docs/`, cada una en un solo grupo, con su título y un enlace que existe

### Requirement: el_sitio_se_usa_en_pantalla_chica
Tipo: funcional
El sistema DEBE poder usarse a 360 px de ancho en las seis páginas, sin desplazamiento horizontal de la página, con todos los enlaces del menú alcanzables con el teclado, y sin errores de consola ni pedidos a otros dominios.

#### Scenario: recorrer las seis páginas en un teléfono
- DADO un ancho de 360 px
- CUANDO se abre cada página y se recorre su menú con Tab
- ENTONCES no hay desplazamiento horizontal de la página, cada enlace del menú recibe el foco, y no hay errores ni pedidos externos
