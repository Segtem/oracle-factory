---
generado: oracle-factory kb
id: "tablero_c67ccc28106a13a74.el_contrato_de_la_extension_cubre_destinos"
vigente: true
---

# el contrato de la extension cubre destinos

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `tablero_c67ccc28106a13a74.el_contrato_de_la_extension_cubre_destinos`
- Vigente: sí
- Cambio: [[cambios/20261107-013054-a8d-vista-destinos]]
- Veredicto: cumple
- Medidas: `factory_tablero_destinos.el_contrato_de_la_extension_cubre_destinos`, `factory_tablero_destinos.corrida_completa`
- Fuente: openspec/changes/20261107-013054-a8d-vista-destinos/specs/tablero/spec.md#el_contrato_de_la_extension_cubre_destinos

Tipo: funcional El contrato entre la CLI y la extensión DEBE declarar las claves de `destinos --json` que lee la extensión, y la suite DEBE fallar si la extensión lee una no declarada o la CLI deja de entregar una declarada.
