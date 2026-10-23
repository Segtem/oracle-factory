# La documentación al día: README, docs y web cuentan lo que Factory hace hoy, con guías nuevas y comprobadas contra la CLI

## Why

Factory creció en 17 cambios desde la última vez que la documentación se ordenó, y cada uno agregó su párrafo al README.
El resultado se contradice: el README empieza diciendo «Hoy existe una POC de CLI» y que el análisis con IA está
pendiente, cuando `pedir-revision` lanza revisores desde la 0.1.0a7; la portada de la web presenta como «visión del
producto, aún no implementada» un tablero que ya existe; `docs/revision-guiada.md` usa `fabrica.py`; y el tablero, el
conocimiento (`kb`, `por-que`, `preguntar`), el MCP, la guía para agentes y la extensión de VS Code no tienen una guía,
sólo párrafos sueltos en el README. Una documentación que nadie comprueba se pudre igual que un vault.

## What changes

- El README se reordena: qué es Factory hoy, instalación, un ejemplo, el flujo, y una sección por cada herramienta con
  un párrafo y el enlace a su guía. Lo que ya no es cierto se saca (la POC, CodeRabbit como único revisor, «no coordina
  agentes»).
- Guías nuevas en `docs/`: `tablero.md` (el tablero, quién trabaja en qué, de a dos con Live Share, la extensión),
  `conocimiento.md` (`kb`, notas que vencen, `por-que`, `preguntar` y sus embeddings) y `agentes.md` (`--agente`, la guía
  de `AGENTS.md`, el MCP, los revisores). Las que ya existen se ponen al día (`fabrica.py` → `oracle-factory`).
- La web: la portada deja de presentar como futuro lo que ya está, y enlaza las guías nuevas; las guías de la web que
  nombran versiones o comandos se ponen al día.
- Una comprobación automática, con su prueba: cada subcomando de la CLI aparece en el README o en `docs/`, ningún
  documento ni página nombra un `oracle-factory X` que no exista, y toda versión de Factory que se nombra es la de
  `pyproject.toml`.
- Fuera de este cambio, en sus repositorios: lo que dicen de Factory los README de Oracle, Jam, LyraGASP y el
  `CLAUDE.md` del entorno de Brian, con un commit en cada uno.

## Out of scope

- Traducir la documentación.
- Rehacer el diseño de la web o sus escenas.

## Human decisions

- Decidido por Brian (2026-10-23): la actualización abarca Factory y el ecosistema.
