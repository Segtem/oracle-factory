---
generado: oracle-factory kb
id: "procedencia_cadae59b33b0c0b2c.el_lock_de_factory_coincide_con_su_pyproject"
vigente: true
---

# el lock de factory coincide con su pyproject

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `procedencia_cadae59b33b0c0b2c.el_lock_de_factory_coincide_con_su_pyproject`
- Vigente: sí
- Cambio: [[cambios/20261028-235529-lhi-uvlock]]
- Veredicto: cumple
- Medidas: `factory_uv_lock.el_lock_de_factory_coincide_con_su_pyproject`, `factory_uv_lock.corrida_completa`
- Fuente: openspec/changes/20261028-235529-lhi-uvlock/specs/procedencia/spec.md#el_lock_de_factory_coincide_con_su_pyproject

Tipo: funcional El sistema DEBE hacer fallar una prueba cuando el uv.lock versionado no coincide con el pyproject.toml de Factory, de modo que cambiar la versión o una dependencia sin regenerar el lock se detecte.
