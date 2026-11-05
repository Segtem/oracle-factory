# Web: simulación pixel art de personas y agentes trabajando a la vez

## Por qué

La guía de colaboración explica con texto cómo dos personas y sus agentes trabajan a la vez sin pisarse: ramas y worktrees,
quién decide qué, qué se une solo y qué no, por qué una revisión vieja deja de valer. Es lo más difícil de entender sin verlo.
Brian pidió simularlo en pixel art, «como funciona la concurrencia». Quien llega a la web tiene que poder mirar a Ana, a Beto y
a sus agentes trabajar en paralelo, parar la escena, avanzarla paso a paso y leer en cada paso quién decidió y por qué.

## Qué cambia

- Una página nueva, `site/concurrencia.html`, con una escena de pixel art: un tronco (`main`), un carril por persona o agente
  (su rama y su checkout), cambios que viajan, y un registro que dice quién decidió cada cosa.
- Un motor de reglas puro y determinista (`site/concurrencia.js`, se prueba con node, sin navegador), con la misma semilla
  la misma traza. Cinco escenarios guiados, sacados de los que mide el banco de concurrencia y de `docs/colaboracion.md`:
  1. dos frentes en paralelo que se unen solos;
  2. el mismo archivo editado por dos (conflicto: lo resuelve una persona);
  3. dos ramas que decidieron distinto (`decidir-union`, sólo de una persona);
  4. una revisión que queda vieja porque la otra persona integró antes;
  5. un agente que intenta cerrar o aprobar (no puede; propone).
- Controles: elegir escenario, avanzar un paso, reproducir y pausar, velocidad y reiniciar; todo con teclado.
- Enlaces desde la guía de colaboración y la portada, y un rótulo claro: es una simulación de las reglas, no ejecuta Factory.

## Fuera de alcance

- No corre Factory ni Git de verdad dentro de la página; el motor modela las reglas documentadas.
- No se reordenan ni se completan las demás páginas (es el cambio 3 de la web).
- Sin sonido y sin librerías nuevas.

## Decisiones humanas

- Aprobar esta spec, en particular los cinco escenarios y el nombre y lugar de la página nueva.
- Límite aceptado: una simulación puede quedar desactualizada respecto de la herramienta real. Cada regla del motor cita el
  texto de `docs/colaboracion.md` que la respalda, y una prueba comprueba que esas citas y los comandos nombrados existan.
