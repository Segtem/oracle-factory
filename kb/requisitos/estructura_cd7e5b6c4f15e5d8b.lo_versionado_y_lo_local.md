---
generado: oracle-factory kb
id: "estructura_cd7e5b6c4f15e5d8b.lo_versionado_y_lo_local"
vigente: true
---

# lo versionado y lo local

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_cd7e5b6c4f15e5d8b.lo_versionado_y_lo_local`
- Vigente: sí
- Cambio: [[cambios/20261005-132144-jerarquia-de]]
- Veredicto: cumple
- Medidas: `factory_estructura.lo_versionado_y_lo_local`, `factory_estructura.corrida_completa`
- Fuente: openspec/changes/20261005-132144-jerarquia-de/specs/estructura/spec.md#lo versionado y lo local

Tipo: no funcional Lo que Factory guarda bajo `.factory/` fuera de `local/` SHALL ser versionable y portátil, sin rutas absolutas, y lo que es de una máquina SHALL ir en `.factory/local/`, ignorada por Git.
