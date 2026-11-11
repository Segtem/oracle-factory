# Registros fuera del repo del producto, etapa 5a: la guía de agentes y la skill van al producto sin versionar

## Por qué

Con almacén aparte (etapas 1–4), `oracle-factory agentes` escribe `AGENTS.md` y `CLAUDE.md` en la raíz de los registros, o sea en el almacén, y `skill --instalar` escribe la skill en `.claude/skills/` del almacén. Un agente que trabaja en la carpeta del producto no los lee: trabaja sin las reglas de Factory. Brian decidió (2026-11-11) que, con almacén aparte, la guía y la skill van al producto **sin versionar**, excluidas en `.git/info/exclude`.

## Qué cambia (sólo con almacén aparte; sin él, nada cambia)

- `oracle-factory agentes` escribe el bloque de la guía en `AGENTS.md` y `CLAUDE.md` (`@AGENTS.md`) de la raíz del producto, y `agentes --verificar` mira esos archivos.
- `oracle-factory skill --instalar` escribe la skill en `.claude/skills/oracle-factory/SKILL.md` del producto.
- Factory agrega esas rutas al archivo de exclusiones local de Git del producto (`.git/info/exclude`, el común a todos sus worktrees), si todavía no están excluidas o ignoradas, sin tocar el `.gitignore` ni ninguna configuración de Git. Así `git status` del producto queda limpio y el repo no los versiona. Es la única escritura en el `.git` del producto, y sólo cuando se piden esos comandos.
- Si el producto ya versiona `AGENTS.md`, `CLAUDE.md` o esa skill (por ejemplo, el equipo tiene su propio `AGENTS.md`), Factory no los modifica: lo dice y no escribe nada, para no ensuciar el árbol de trabajo del producto.
- Con almacén aparte, la guía agrega una línea que dice que los registros viven en un almacén aparte y que se comparten con `oracle-factory sincronizar`.

## Fuera de alcance

- La extensión de VS Code (etapa 5b) y la migración (etapa 6).

## Decisiones humanas

La de Brian del 2026-11-11; y, por defecto, que si el producto ya versiona esos archivos Factory se niega en vez de modificarlos (se confirma al aprobar la spec).
