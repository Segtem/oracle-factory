---
generado: oracle-factory kb
id: "estructura2_c1bed25594460b383.la_configuracion_del_proyecto_vive_en_factory"
vigente: true
---

# la configuracion del proyecto vive en factory

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura2_c1bed25594460b383.la_configuracion_del_proyecto_vive_en_factory`
- Vigente: sí
- Cambio: [[cambios/20261006-004456-fase-2-de-la]]
- Veredicto: cumple
- Medidas: `factory_estructura2.la_configuracion_del_proyecto_vive_en_factory`, `factory_estructura2.corrida_completa`
- Fuente: openspec/changes/20261006-004456-fase-2-de-la/specs/estructura2/spec.md#la configuración del proyecto vive en .factory

Tipo: funcional La configuración SHALL leerse de `.factory/config.json`; si sólo existe el `factory.json` de la raíz SHALL leerse de ahí con un aviso, y `migrar` SHALL pasarla al lugar nuevo.
