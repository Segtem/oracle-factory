# Registros fuera del repo del producto, etapa 4b1: cada comando commitea sólo lo de su cambio, con un bloqueo corto

## Por qué

La etapa 4a hace que Factory commitee en el almacén lo que cambió durante cada comando. Brian aceptó un riesgo: dos comandos de Factory a la vez sobre el mismo almacén (dos worktrees, o una persona y un agente) pueden mezclar sus archivos en un solo commit, y el segundo choca con el `index.lock` de Git. Brian decidió (2026-11-11) arreglarlo con un commit por cambio y un bloqueo corto, sin serializar los comandos enteros.

## Qué cambia (sólo con almacén aparte; sin él, nada cambia)

- Un comando sobre un cambio commitea sólo lo que cambió de ese cambio y de lo común. Los archivos que pertenecen a OTRO cambio (su carpeta en `.factory/cambios/`, `tareas/`, `openspec/changes/` y su nota en `kb/cambios/`) no entran aunque hayan cambiado mientras tanto: los commitea el comando de ese otro cambio.
- Un comando sin cambio (por ejemplo `kb` o `init`) commitea todo lo que cambió, como hasta ahora.
- El commit (la foto final, el `add` y el `commit`) se hace con un bloqueo exclusivo propio del almacén, sólo durante el commit: dos comandos que terminan a la vez commitean uno después del otro, sin chocar con `index.lock`. Si el bloqueo no se consigue en un tiempo razonable, el comando no falla: avisa y deja los registros en el disco.
- Dos comandos sobre el MISMO cambio a la vez todavía pueden compartir archivos en un commit: queda dicho como límite.

## Fuera de alcance

- `conectar URL` y `sincronizar` (etapa 4b2).
- Bloquear los comandos enteros.

## Decisiones humanas

Ninguna nueva: es la decisión de Brian del 2026-11-11.
