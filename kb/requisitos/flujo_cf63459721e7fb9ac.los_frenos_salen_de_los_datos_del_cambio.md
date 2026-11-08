---
generado: oracle-factory kb
id: "flujo_cf63459721e7fb9ac.los_frenos_salen_de_los_datos_del_cambio"
vigente: true
---

# los frenos salen de los datos del cambio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cf63459721e7fb9ac.los_frenos_salen_de_los_datos_del_cambio`
- Vigente: sí
- Cambio: [[cambios/20261108-203356-puy-frenos]]
- Veredicto: sin juicio
- Medidas: `factory_frenos.los_frenos_salen_de_los_datos_del_cambio`, `factory_frenos.corrida_completa`
- Fuente: openspec/changes/20261108-203356-puy-frenos/specs/flujo/spec.md#los_frenos_salen_de_los_datos_del_cambio

Tipo: funcional El sistema DEBE calcular, solo con los registros del cambio, su candidato vigente y Git, los frenos del cambio, cada uno con un identificador y un motivo: `juicios_rojos` (los dos últimos juicios de Oracle son rojos), `hallazgo_alto_abierto` (un informe del candidato vigente trae un hallazgo de severidad alta y no hay una revisión aprobada vigente), `prueba_existente_editada`, `cambio_grande` y `bucle_de_revision` (los dos últimos con los umbrales que ya usa `estado`). Un dato que no se puede leer NO DEBE producir un freno ni romper `estado`.
