# Web: un menú, un orden de lectura y toda la documentación

## Por qué

La web ya tiene cinco páginas (portada, desde cero, modos, en equipo y la simulación), pero se leen sueltas. Hoy el menú no
lleva a «Modos» ni a la «Simulación» desde ningún lado, ninguna guía lleva a la siguiente, la portada no dice por dónde seguir,
y de las 12 guías de `docs/` (tablero, conocimiento, puerta, revisión guiada, trazabilidad, procedencia, agentes…) la web
cuenta sólo las que tienen página propia. Quien llega desde cero no tiene un camino; quien busca una guía no la encuentra.
Es el tercero de los tres cambios de la web que pidió Brian (después de las capturas de VS Code y de la simulación).

## Qué cambia

- **Una sola tabla de páginas** (`tools/sitio_paginas.py`) de la que salen el menú, el pie y los enlaces de lectura de todas las
  páginas; el mismo script verifica que lo escrito en los HTML coincide con la tabla, así que no se desordenan.
- **Un menú igual en todas las páginas**: los enlaces de la portada de siempre y las cinco páginas de contenido más
  «Documentación», con la página actual marcada (`aria-current="page"`).
- **Un orden de lectura**: Desde cero → Modos → En equipo → Simulación → Documentación. Cada guía termina con «Seguí leyendo»
  (la anterior y la siguiente) y la portada tiene una sección «Por dónde seguir» con las cinco páginas y una frase cada una.
- **Una página nueva, `documentacion.html`**, con las 12 guías de `docs/` agrupadas (empezar, trabajar de a varios, calidad y
  entrega, consultar el proyecto), cada una con su título, una frase y su enlace. Una prueba falla si falta alguna guía.
- **Pantalla chica**: el menú más largo sigue usable a 360 px, sin desplazamiento horizontal de la página.

## Fuera de alcance

- No se escriben páginas nuevas de contenido (por ejemplo una del tablero con capturas propias, ni ejemplos de `preguntar`):
  salen como un cambio aparte si Brian los quiere.
- No se cambia el contenido de las guías existentes salvo lo que agrega el bloque «Seguí leyendo».
- Sin librerías nuevas ni cambios de estilo de fondo; los estilos agregados son los del menú, el pie y la página nueva.

## Decisiones humanas

- Aprobar esta spec, en particular el orden de lectura, el nombre «Documentación» y los cuatro grupos de guías.
- Se mantiene el orden actual de los enlaces de la portada en el menú (Cuatro caminos, El recorrido…), aunque no sea el de sus
  secciones, porque una prueba existente depende de él; el orden de lectura nuevo es el de las páginas, no el de la portada.
