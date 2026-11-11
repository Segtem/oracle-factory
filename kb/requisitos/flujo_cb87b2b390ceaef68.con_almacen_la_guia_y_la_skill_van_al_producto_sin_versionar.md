---
generado: oracle-factory kb
id: "flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar"
vigente: true
---

# con almacen la guia y la skill van al producto sin versionar

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar`
- Vigente: sí
- Cambio: [[cambios/20261111-161316-dd7-almacen-guia]]
- Veredicto: sin juicio
- Medidas: `factory_almacen_guia.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar`, `factory_almacen_guia.corrida_completa`
- Fuente: openspec/changes/20261111-161316-dd7-almacen-guia/specs/flujo/spec.md#con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar

Tipo: funcional El sistema DEBE, con almacén aparte, escribir con `agentes` el bloque de la guía en `AGENTS.md` y `CLAUDE.md` de la raíz del repo del producto (y verificar esos archivos con `agentes --verificar`), y con `skill --instalar` la skill en `.claude/skills/oracle-factory/SKILL.md` del producto; DEBE excluir esas rutas en el archivo de exclusiones local de Git del producto (`git rev-parse --git-path info/exclude`), salvo que ya estén excluidas o ignoradas, sin tocar `.gitignore` ni la configuración de Git y sin escribir nada más en el `.git` del producto, de modo que `git status` del producto quede limpio; y sin almacén aparte DEBE comportarse como hasta ahora.
