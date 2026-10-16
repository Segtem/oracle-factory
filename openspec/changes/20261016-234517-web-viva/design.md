# Design

- Todo en `site/`: el pixel art son SVG en línea (`shape-rendering: crispEdges`) o rejillas de CSS; nada de imágenes externas ni de fuentes nuevas. `site/viva.js` (nuevo) arma las escenas, los personajes, el minijuego y los easter eggs; `site/factory.js` (el recorrido) no cambia de contrato.
- Las escenas se animan con clases que pone un `IntersectionObserver`. Con `prefers-reduced-motion: reduce` no se agregan, y cada escena muestra su estado final.
- El minijuego es una máquina de estados pura (`site/juego.js`, sin DOM), probada con node. Las reglas salen de la CLI: el corte por severidad (un medio o más sin aceptar no deja aprobar), riesgo aceptado con motivo, medidas acordadas o el requisito queda sin juicio, y cierre sólo con todo vigente. Lo que se ve en pantalla lo arma `viva.js` con ese estado.
- Las pruebas: `tests/test_site.cjs` (Chromium con Playwright) suma el minijuego con teclado, las escenas con y sin movimiento reducido, los easter eggs y el desborde a 320 px; `tests/test_juego.cjs` prueba la máquina de estados; `tests/test_web_viva.py` corre los dos y los cruza con el contrato del sensor.
