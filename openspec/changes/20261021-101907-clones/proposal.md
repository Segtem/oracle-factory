# Dos clones sin tropiezos: init versionable, IDs que no chocan y escrituras simultáneas que se reintentan

## Why

El banco de concurrencia (cambio coordinar-dos, 2026-10-21) encontró tres defectos que aparecen apenas dos personas
trabajan con sus clones:

- **D1:** `init` deja carpetas vacías (`tareas/`, `catalogos/`, `openspec/changes/`, `.factory/cambios/`) que Git no
  versiona. La segunda persona que clona el proyecto no puede crear un cambio: `oracle-task` no encuentra `tareas/`.
- **D4:** dos cambios creados en el mismo segundo con el mismo sufijo, en dos clones, tienen el mismo ID y recién chocan
  al integrar, mezclando dos cambios distintos.
- **D5:** escrituras simultáneas sobre un mismo registro (un agente que deja varios mensajes, o una persona y su agente a
  la vez) no se pierden, pero entre un tercio y dos tercios se rechazan y hay que repetirlas a mano.

## What changes

- `init` deja un `.gitkeep` en cada carpeta que crea y Git versionaría vacía; y los comandos que necesitan una carpeta de
  Factory que falta (por ejemplo `tareas/` en un clon de un proyecto viejo) la crean en vez de fallar.
- El ID de un cambio nuevo lleva tres caracteres al azar antes del sufijo (`20261021-101300-k3x-igual`): dos clones no
  generan el mismo ID aunque creen el cambio en el mismo segundo con el mismo sufijo, y el ID sigue terminando en el sufijo.
- Los comandos que sólo agregan al registro de un cambio sin decidir sobre lo que ya hay (`mensaje`, `tomar`, `soltar`)
  reintentan solos cuando el registro cambió mientras escribían, leyéndolo de nuevo y volviendo a comprobar sus reglas.

## Out of scope

- Unir el registro de un cambio editado en dos ramas: es el cambio «unir registros».

## Human decisions

- Brian eligió el 2026-10-21 corregir D1, D4 y D5 en un cambio chico, antes de «unir registros».
