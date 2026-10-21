---
generado: oracle-factory kb
id: "flujo_cecdfd053bebfee21.init_no_deja_carpetas_que_factory_no_usa"
vigente: true
---

# init no deja carpetas que factory no usa

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cecdfd053bebfee21.init_no_deja_carpetas_que_factory_no_usa`
- Vigente: sí
- Cambio: [[cambios/20261017-135953-higiene]]
- Veredicto: cumple
- Medidas: `factory_higiene.init_no_deja_carpetas_que_factory_no_usa`, `factory_higiene.corrida_completa`
- Fuente: openspec/changes/20261017-135953-higiene/specs/flujo/spec.md#init no deja carpetas que Factory no usa

Tipo: funcional `init` SHALL NOT dejar en el proyecto carpetas de Oracle vacías que Factory no usa (`corpus`, `relaciones`, `diferencial`) si las creó al inicializar, y SHALL NOT tocar las que ya existían. El bloqueo de `medir` SHALL vivir dentro de `.factory/local/` y el `.gitignore` que arma `init` SHALL NOT nombrar `.factory-demo/`.
