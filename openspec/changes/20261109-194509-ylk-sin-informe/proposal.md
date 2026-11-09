# Autopilot: el conductor no repite el pedido a un revisor que se lanzó y no dejó resultado

## Por qué

En `segundo-revisor` el conductor pide a un revisor de otro proveedor. Si ese revisor se lanza y no deja informe (por ejemplo agy sin cuota: «Individual quota reached»), Factory registra el lanzamiento sin resultado y `estado` lo avisa, pero `segundo_revisor` lo sigue ofreciendo: el conductor repite el pedido, vuelve a fallar y recién lo frena «sin progreso». Es ruido y gasto de tiempo, y esconde el problema a la persona.

## Qué cambia

`estado --json` no ofrece en `segundo_revisor` a un revisor con un lanzamiento sin resultado sobre el candidato vigente. Ofrece, en su lugar, otro revisor configurado de otro proveedor que no tenga ese problema; si no queda ninguno, `segundo_revisor` es `null` y el conductor sigue como si no hiciera falta (la persona ve el aviso del lanzamiento en `estado`).

## Fuera de alcance

- Reintentar un lanzamiento fallido, o esperar a que se reinicie una cuota.
- Cambiar el aviso del lanzamiento sin resultado ni cómo se registra.
- Lanzamientos sobre un candidato que ya no es el vigente: no cuentan.

## Decisiones humanas

Ninguna nueva.
