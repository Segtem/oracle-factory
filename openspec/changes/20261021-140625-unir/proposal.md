# Unir registros: el de un cambio editado en dos ramas se une sin perder nada, y lo generado se rehace

## Why

El banco de concurrencia (coordinar-dos, 2026-10-21) mostró el problema central de trabajar de a dos: el registro de un
cambio (`.factory/cambios/<ID>/factory.json`) editado en dos ramas —dos personas que toman el mismo cambio, o que dejan
mensajes o decisiones cada una en su rama— choca como texto al integrar. Factory no ayuda a unirlo, y la resolución más
común (quedarse con un lado) pierde las decisiones de la otra persona (escenarios s4 y a3). Lo mismo, sin pérdida pero con
trabajo a mano, pasa con lo que Factory genera (`.factory/resumen.md`, `kb/`).

## What changes

- `init` y `oracle-factory hooks` configuran en el clon un *merge driver* de Git para los registros de los cambios: al
  integrar, Git le pasa a Factory las dos versiones y la común, y Factory las une. Los eventos de las dos ramas quedan
  todos, en orden; lo que cambió una sola rama se toma de esa rama.
- Si las dos ramas decidieron distinto sobre lo mismo (dos responsables, dos aprobaciones de spec, dos medidas de un mismo
  requisito, dos revisiones, dos juicios, dos fases), Factory no elige: deja las dos versiones anotadas en el registro,
  `estado` lo avisa con qué hay que decidir, y la decisión queda en una persona (por ejemplo `tomar --relevo`, o volver a
  aprobar o medir). Nada se pierde.
- Lo generado (`.factory/resumen.md`, las notas de `kb/`) no choca al integrar: se rehace después del merge, y
  `resumen --verificar` y `kb --verificar` lo comprueban.
- El banco de concurrencia pasa los escenarios s4 y a3 sin decisiones perdidas.

## Out of scope

- Un servicio central de bloqueos: la unión es al integrar, no antes.
- Unir automáticamente el código del producto: eso es de Git y de las personas.

## Human decisions

- Brian eligió el 2026-10-21 corregirlo en un cambio propio antes de cerrar coordinar-dos.
- La regla «Factory no elige cuando las dos ramas decidieron distinto» es una decisión de diseño a confirmar con esta spec.
