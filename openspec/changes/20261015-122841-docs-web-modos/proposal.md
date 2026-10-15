# Docs y web: los modos de trabajo y quién decide qué

## Why

Brian, 2026-10-05: «encontramos lo más importante de todo el sistema […] hace más partícipe a la persona». Los modos de trabajo deciden cuánto decide una persona y cuánto un agente, pero hoy sólo hay una tarjeta en la portada del sitio y menciones sueltas en el README: no se explica cuándo conviene cada modo, qué decide cada uno según el tipo de requisito, ni cómo leer en `estado` quién decidió, quién propuso y quién confirmó.

Tarea de origen: `20261005-112955-docs-web-modos`.

## What changes

- **`docs/modos.md`**, la referencia: los tres modos y cuándo conviene cada uno; una tabla de quién decide cada cosa (spec, medidas de un requisito funcional o no funcional, revisión, cierre) en cada modo; requisitos funcionales y no funcionales con `tipos_obligatorios`; cómo leer `estado`; cómo cambiar de modo; un ejemplo real, y los límites (Factory no autentica a nadie).
- **`site/modos.html`**, la misma explicación para quien empieza, enlazada desde la tarjeta de los modos en la portada; el README enlaza el documento.
- **La tabla se comprueba contra el código**: una prueba la lee en la página y en el documento y la compara con lo que decide `modos.via_agente`.
- El ejemplo real es el trabajo de Factory sobre sí misma (modo confirmación: el agente propone, una persona confirma, y `estado` lo muestra). El piloto con agentes de la tarea es anterior a los modos (0.1.0a3) y no sirve de ejemplo; se dice.

## Out of scope

- Cambiar cómo funcionan los modos.
- La página de colaboración entre varias personas (tarea `web-colaboracion`).

## Human decisions

- Brian eligió el formato el 2026-10-15: un documento en `docs/` y una página del sitio.
