# Lo que la prueba del ajedrez dejó a la vista: revisores cortados, acciones sin autor y carpetas de más

## Why

El 2026-10-17 Brian probó Factory desde cero con un agente en `~/Proyectos/CLab/Chess` (un ajedrez en C). El postmortem encontró cuatro problemas de higiene que ensucian el rastro o confunden a quien empieza:

- **Un revisor cortado no deja rastro.** `pedir-revision` a agy1 quedó cortado a mitad (sesión cerrada): tiene paquete y carpeta de trabajo, pero ningún evento, y `estado` no lo menciona. Hoy el evento se registra sólo al terminar.
- **Acciones sin autor.** El agente corrió `nuevo` e `importar` sin `--agente`, y quedaron «sin identificar» sin que nada avise.
- **Carpetas de Oracle que Factory no usa.** `init` deja `corpus/`, `relaciones/` y `diferencial/` vacías (las crea `oracle init`); Brian las vio vacías y no supo para qué eran.
- **Un nombre viejo.** El bloqueo de `medir` vive en `.factory-demo/locks` e `init` agrega `.factory-demo/` al `.gitignore` del proyecto.

Es la parte D de las mejoras que Brian ordenó tras el postmortem (después vienen commits unidos al cambio, «¿por qué existe esta línea?» y el panel en VS Code).

## What changes

- **`pedir-revision` registra el lanzamiento** (`revision_lanzada`, con revisor y candidato) antes de correr al revisor, y el resultado al terminar, también si se interrumpe con Ctrl-C. `estado` avisa de un lanzamiento sin resultado: «el revisor X se lanzó a las HH:MM sobre el candidato Y y no dejó resultado», hasta que ese revisor deja uno para ese candidato.
- **`estado` avisa de las acciones sin autor**: cuántas y cuáles, y que un agente las hace con `--agente NOMBRE`.
- **`init` no deja carpetas de Oracle vacías** que Factory no usa: si `oracle init` creó `corpus/`, `relaciones/` o `diferencial/` y quedaron vacías, las saca. Las que ya existían no se tocan.
- **El bloqueo de `medir` pasa a `.factory/local/locks/`**, que ya está ignorado; `init` deja de agregar `.factory-demo/`.

## Out of scope

- Commits unidos al cambio, «¿por qué existe esta línea?» y el panel de VS Code: cambios aparte.
- Reparar proyectos que ya tienen `.factory-demo/` o carpetas vacías: se pueden borrar a mano.

## Human decisions

- Brian eligió el 2026-10-17 el orden (D, B, C, A) y que `init` no cree las carpetas de Oracle que Factory no usa.
