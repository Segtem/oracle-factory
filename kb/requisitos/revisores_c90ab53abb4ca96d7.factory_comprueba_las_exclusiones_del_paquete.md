---
generado: oracle-factory kb
id: "revisores_c90ab53abb4ca96d7.factory_comprueba_las_exclusiones_del_paquete"
vigente: true
---

# factory comprueba las exclusiones del paquete

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c90ab53abb4ca96d7.factory_comprueba_las_exclusiones_del_paquete`
- Vigente: sí
- Cambio: [[cambios/20261014-000054-paquete-producto]]
- Veredicto: cumple
- Medidas: `factory_paquete.factory_comprueba_las_exclusiones_del_paquete`, `factory_paquete.corrida_completa`
- Fuente: openspec/changes/20261014-000054-paquete-producto/specs/revisores/spec.md#Factory comprueba las exclusiones del paquete

Tipo: funcional Un paquete cuyas exclusiones dejan afuera un archivo del producto SHALL NOT usarse: `pedir-revision` SHALL fallar sin guardar el informe, y la preparación de la revisión SHALL no usar el informe de ese paquete y avisar por qué. Los paquetes sin exclusiones de vueltas anteriores SHALL seguir usándose.
