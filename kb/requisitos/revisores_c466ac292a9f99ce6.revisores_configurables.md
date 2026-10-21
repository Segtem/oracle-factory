---
generado: oracle-factory kb
id: "revisores_c466ac292a9f99ce6.revisores_configurables"
vigente: true
---

# revisores configurables

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c466ac292a9f99ce6.revisores_configurables`
- Vigente: sí
- Cambio: [[cambios/20261007-192608-revisores]]
- Veredicto: cumple
- Medidas: `factory_revisores.revisores_configurables`, `factory_revisores.corrida_completa`
- Fuente: openspec/changes/20261007-192608-revisores/specs/revisores/spec.md#revisores configurables

Tipo: funcional Los revisores SHALL declararse en `.factory/config.json` bajo `revisores`, cada uno con su comando (lista de argumentos con marcadores), proveedor, modelo y tope en minutos; un revisor no declarado o una configuración inválida SHALL rechazarse antes de preparar nada, mostrando cómo declararlo.
