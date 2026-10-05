# Design

Se completa después de la aceptación, con las respuestas a las preguntas abiertas de la propuesta.

Puntos a resolver al implementar:

- `contexto_producto()` y `pendientes_actuales` comparan hoy el diccionario entero; pasan a comparar `archivos_sha256` y a conservar `head` como dato.
- `revision.validar` compara `informe.contexto == contexto` con el diccionario entero; debe comparar sólo la huella.
- `estado` y `cerrar` agregan el aviso de HEAD distinto.
