# Una portada viva: pixel art, personajes, escenas animadas y un minijuego de decisiones

## Why

Brian pidió el 2026-10-16 actualizar la web para que sea entretenida y divertida, con más pixel art y animaciones. Hoy la portada es sobria y editorial: un solo cuadro de pixel art (la línea de producción del recorrido) y, en el resto, tarjetas con íconos chicos. Además, a 320 px de ancho desborda horizontalmente, y `tests/test_site.cjs` falla en `main` por eso.

## What changes

- **Fábrica viva**: la portada mantiene su estructura, su paleta y sus textos, pero el pixel art pasa a ser el idioma de toda la página. Cada herramienta tiene su sprite (OpenSpec, Oracle Task, agentes, Oracle Clue, Oracle, vos), el encabezado es una escena con la fábrica, y cada sección tiene una escena que se anima al llegar a la pantalla: la caja avanza por la cinta, Oracle enciende verde o rojo, Clue busca con la lupa.
- **Personajes con nombre**: la persona, el agente que construye, los revisores (codex y agy), Oracle y Clue aparecen a lo largo de la página y dicen en globitos qué hace cada uno. Ninguno decide por la persona.
- **Minijuego de decisiones**: quien visita juega de persona. Llega un pedido y el agente propone. En cada parada se elige, con las mismas reglas que la CLI: no se puede aprobar con un hallazgo medio abierto, aceptar un riesgo deja un motivo y las medidas sin acordar dejan el requisito sin juicio. Al final se ve el registro (quién decidió qué, persona o agente) y por qué Oracle dio verde o rojo.
- **Easter eggs**: detalles escondidos que no tapan contenido ni cambian lo que dice la página. Por ejemplo, la chimenea larga humo, el gato de la fábrica y el código Konami.
- **Accesible y liviana como hasta ahora**: sin red ni dependencias externas, con teclado, y con movimiento reducido no se anima nada y todo se lee. Sin desborde horizontal de 320 a 1440 px.

## Out of scope

- Las guías (desde cero, modos, en equipo): sólo toman el encabezado y los sprites nuevos; su texto no cambia. Rehacerlas va en otro cambio.
- Sonido.

## Human decisions

- Brian eligió el 2026-10-16: «Fábrica viva», con minijuego, personajes con nombre, escenas al hacer scroll y easter eggs; la portada primero.
