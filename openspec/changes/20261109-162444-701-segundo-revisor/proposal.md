# Autopilot: en el camino completo el conductor pide un segundo revisor de otro proveedor

## Por qué

`estado` sólo sugiere un revisor (`pedir-revision --a agy`). Para un cambio de camino completo (más de 150 líneas de producto o que toca reglas de decisión) hemos pedido siempre dos revisiones de proveedores distintos (agy y codex), pero el conductor (`autopilot --ejecutar`) pasa a `revisar` apenas hay una ronda sin hallazgos medios. La segunda ronda la hace hoy una persona o un agente a mano.

## Qué cambia

- `estado --json` trae `segundo_revisor`: el nombre del revisor configurado que falta, o `null`. Sólo hay uno cuando el camino del candidato es completo, entre los informes de todos los candidatos del cambio hay menos de dos proveedores distintos y existe un revisor configurado de otro proveedor.
- El conductor, ante el próximo paso `revisar` con un `segundo_revisor`, decide `actuar` con `pedir-revision ID --a ESE_REVISOR` (mecánico) antes de preparar la propuesta o pedirle la revisión a una persona.
- No cambia el próximo paso de `estado`, ni nada que decida una persona, ni el camino ligero (un revisor y una ronda).

## Fuera de alcance

- Hacer obligatoria la segunda ronda para cerrar: `estado` sigue sin exigirla; sólo el conductor la pide.
- Más de dos revisores, o elegir el revisor por calidad.

## Decisiones humanas

Que «camino completo» pida dos proveedores en el conductor es una política que deducimos de cómo trabajamos; se confirma al aprobar esta spec.
