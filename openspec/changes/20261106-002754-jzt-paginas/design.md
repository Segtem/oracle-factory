# Diseño

- `tools/sitio_paginas.py` tiene una tabla `PAGINAS` (archivo, nombre en el menú, frase, orden de lectura) y los marcadores
  `<!-- menu -->…<!-- /menu -->`, `<!-- leer -->…<!-- /leer -->`, `<!-- pie -->…<!-- /pie -->` en cada página. `--escribir`
  los rehace desde la tabla; sin argumentos devuelve los problemas (marcadores que faltan, bloques que difieren de la tabla,
  páginas que no están en la tabla, enlaces rotos) y falla si hay.
- El menú reparte los enlaces de la portada (`#formas`, `#recorrido`…) como hoy: `#…` en la portada y `./index.html#…` en el
  resto. «Seguí leyendo» es un `<nav>` dentro de `<main>`, no una `<section>`, para no alterar el conteo de secciones.
- `documentacion.html` es HTML escrito a mano con una lista por grupo; `problemas()` compara los enlaces a `docs/*.md` con los
  archivos que existen y el título con la primera línea de cada guía.
- Pruebas: `tests/test_web_paginas.py` (generador, tabla, documentación) y `tests/test_web_paginas.cjs` (Chromium: menú,
  `aria-current`, 360 px, teclado, sin errores ni pedidos externos).
