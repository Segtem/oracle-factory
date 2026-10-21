---
generado: oracle-factory kb
id: "trazabilidad_cca95191eb0039b11.el_sensor_registra_que_lineas_ejecuta_cada_caso"
vigente: true
---

# el sensor registra que lineas ejecuta cada caso

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `trazabilidad_cca95191eb0039b11.el_sensor_registra_que_lineas_ejecuta_cada_caso`
- Vigente: sí
- Cambio: [[cambios/20261013-180751-trazabilidad]]
- Veredicto: cumple
- Medidas: `factory_trazabilidad.el_sensor_registra_que_lineas_ejecuta_cada_caso`, `factory_trazabilidad.corrida_completa`
- Fuente: openspec/changes/20261013-180751-trazabilidad/specs/trazabilidad/spec.md#el sensor registra qué líneas ejecuta cada caso

Tipo: funcional `oracle_factory.trazabilidad` SHALL correr los casos que un sensor asigna a cada requisito con una traza de líneas de la biblioteca estándar y SHALL escribir `trazabilidad.json` con `esquema` `oracle-factory.trazabilidad-casos/1`, cada requisito con sus casos y cada caso con su resultado y las líneas que ejecutó de archivos del proyecto (rutas relativas, sin el entorno virtual). Un caso que falla SHALL quedar registrado con su resultado, sin cortar la traza de los demás.
