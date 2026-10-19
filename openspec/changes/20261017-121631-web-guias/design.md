# Design

- Las guías cargan `pixel.js` y `viva.js` (los de la portada). `viva.js` suma tres escenas (`guia`, `modos`, `equipo`) y sigue sin tocar nada que no esté: el minijuego y los secretos sólo se arman si sus elementos existen.
- Los personajes son el mismo `<figure class="personaje">` de la portada, marcados `data-viva` para que la prueba de «el texto no cambia» los deje afuera.
- `tests/test_web_guias.cjs` (Chromium con Playwright) compara el texto de cada guía con el de `main` sin lo marcado `data-viva`, recorre escenas y personajes con y sin movimiento reducido y mide el desborde; `tests/test_web_guias.py` lo corre para el sensor.
