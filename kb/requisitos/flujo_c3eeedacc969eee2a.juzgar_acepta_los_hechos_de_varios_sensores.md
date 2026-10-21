---
generado: oracle-factory kb
id: "flujo_c3eeedacc969eee2a.juzgar_acepta_los_hechos_de_varios_sensores"
vigente: true
---

# juzgar acepta los hechos de varios sensores

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c3eeedacc969eee2a.juzgar_acepta_los_hechos_de_varios_sensores`
- Vigente: sí
- Cambio: [[cambios/20261017-023151-hechos-varios]]
- Veredicto: cumple
- Medidas: `factory_hechos.juzgar_acepta_los_hechos_de_varios_sensores`, `factory_hechos.corrida_completa`
- Fuente: openspec/changes/20261017-023151-hechos-varios/specs/flujo/spec.md#juzgar acepta los hechos de varios sensores

Tipo: funcional `juzgar` SHALL aceptar `--con` repetido, un archivo de hechos por sensor, y SHALL juzgar con todos a la vez. El registro SHALL guardar cada archivo con su huella; si cualquiera cambia, falta o no es una ruta, el juicio SHALL dejar de valer, `estado` SHALL nombrar ese archivo y el próximo paso SHALL repetir el juicio con los mismos archivos. `donde` SHALL listarlos todos. Con un solo `--con` o sin él, el registro SHALL ser el de siempre.
