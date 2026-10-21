---
generado: oracle-factory kb
id: "revisores_c54735f6bdc173577.revisar_reconoce_un_riesgo_ya_aceptado"
vigente: true
---

# revisar reconoce un riesgo ya aceptado

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c54735f6bdc173577.revisar_reconoce_un_riesgo_ya_aceptado`
- Vigente: sí
- Cambio: [[cambios/20261013-115616-vueltas-severidad]]
- Veredicto: cumple
- Medidas: `factory_vueltas.revisar_reconoce_un_riesgo_ya_aceptado`, `factory_vueltas.corrida_completa`
- Fuente: openspec/changes/20261013-115616-vueltas-severidad/specs/revisores/spec.md#revisar reconoce un riesgo ya aceptado

Tipo: funcional En `revisar`, un hallazgo con el mismo archivo y el mismo título normalizado (minúsculas, sin puntuación y con espacios simples) que un riesgo aceptado SHALL mostrarse como ya aceptado, con quién, cuándo y por qué. La persona SHALL elegir entre mantenerlo, que lo registra como riesgo aceptado con el mismo motivo, o revocarlo, que lo saca de los aceptados y lo decide como un hallazgo nuevo. Un hallazgo que no coincide SHALL decidirse como hoy.
