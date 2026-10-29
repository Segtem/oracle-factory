---
generado: oracle-factory kb
id: "procedencia_cadae59b33b0c0b2c.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario"
vigente: true
---

# un paquete que el entorno no instala no vuelve no confiable el inventario

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `procedencia_cadae59b33b0c0b2c.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario`
- Vigente: sí
- Cambio: [[cambios/20261028-235529-lhi-uvlock]]
- Veredicto: sin juicio
- Medidas: `factory_uv_lock.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario`, `factory_uv_lock.corrida_completa`
- Fuente: openspec/changes/20261028-235529-lhi-uvlock/specs/procedencia/spec.md#un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario

Tipo: funcional El sistema DEBE marcar como no instalado, sin declarar no confiable el inventario, un paquete que está en el lock y no está instalado en el entorno consultado, y DEBE seguir declarando no confiable una versión instalada distinta de la del lock.
