---
generado: oracle-factory kb
id: "calidad_cdbf33d35727ca9d7.el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja"
vigente: true
---

# el hook pre push llama a la puerta con lo que se empuja

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `calidad_cdbf33d35727ca9d7.el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja`
- Vigente: sí
- Cambio: [[cambios/20261101-121356-ih8-puertalocal]]
- Veredicto: sin juicio
- Medidas: `factory_puerta_local.el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja`, `factory_puerta_local.corrida_completa`
- Fuente: openspec/changes/20261101-121356-ih8-puertalocal/specs/calidad/spec.md#el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja

Tipo: funcional El sistema DEBE instalar con oracle-factory hooks un hook pre-push que corre la puerta sobre los commits que se van a empujar, que bloquea el push si la puerta falla, que no hace nada al borrar una rama remota, que no pisa un hook pre-push ajeno, y que deja pasar con un aviso si el intérprete de Factory no está.
