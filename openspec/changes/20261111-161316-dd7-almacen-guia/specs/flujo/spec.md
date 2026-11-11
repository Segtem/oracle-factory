# Capability: flujo

## ADDED Requirements

### Requirement: con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar
Tipo: funcional
El sistema DEBE, con almacén aparte, escribir con `agentes` el bloque de la guía en `AGENTS.md` y `CLAUDE.md` de la raíz del repo del producto (y verificar esos archivos con `agentes --verificar`), y con `skill --instalar` la skill en `.claude/skills/oracle-factory/SKILL.md` del producto; DEBE excluir esas rutas en el archivo de exclusiones local de Git del producto (`git rev-parse --git-path info/exclude`), salvo que ya estén excluidas o ignoradas, sin tocar `.gitignore` ni la configuración de Git y sin escribir nada más en el `.git` del producto, de modo que `git status` del producto quede limpio; y sin almacén aparte DEBE comportarse como hasta ahora.

#### Scenario: la guía en el producto
- DADO un producto conectado a un almacén
- CUANDO se corren `agentes` y `skill --instalar`
- ENTONCES el producto tiene `AGENTS.md`, `CLAUDE.md` y la skill, `git status` del producto está limpio, sus rutas figuran en `.git/info/exclude` y la configuración de Git no cambió

#### Scenario: desde un worktree
- DADO un worktree del producto
- CUANDO se corre `agentes` en él
- ENTONCES la exclusión va al archivo común a todos los worktrees y vale también en ellos

#### Scenario: verificar
- DADO la guía escrita en el producto
- CUANDO se corre `agentes --verificar`
- ENTONCES verifica la del producto, no la del almacén

#### Scenario: sin almacén aparte
- DADO un proyecto Factory de los de hoy
- CUANDO se corren `agentes` y `skill --instalar`
- ENTONCES escriben donde siempre y no tocan `.git/info/exclude`

### Requirement: con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen
Tipo: funcional
El sistema DEBE, con almacén aparte, negarse a modificar `AGENTS.md`, `CLAUDE.md` o la skill si el producto ya los versiona, diciendo cuál y sin escribir nada; y DEBE incluir en la guía, con almacén aparte, que los registros viven en un almacén aparte y que se comparten con `oracle-factory sincronizar`.

#### Scenario: el producto ya tiene su AGENTS.md
- DADO un producto conectado que versiona su propio `AGENTS.md`
- CUANDO se corre `agentes`
- ENTONCES se niega nombrando `AGENTS.md`, el archivo y el `.git` del producto no cambian

#### Scenario: la guía dice del almacén
- DADO un producto conectado
- CUANDO se corre `agentes`
- ENTONCES el `AGENTS.md` del producto dice que los registros viven en un almacén aparte y nombra `oracle-factory sincronizar`
