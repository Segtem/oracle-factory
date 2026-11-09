---
generado: oracle-factory kb
id: "flujo_c350dc50b9b6cde6a.estado_dice_que_segundo_revisor_falta_en_el_camino_completo"
vigente: true
---

# estado dice que segundo revisor falta en el camino completo

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c350dc50b9b6cde6a.estado_dice_que_segundo_revisor_falta_en_el_camino_completo`
- Vigente: sí
- Cambio: [[cambios/20261109-162444-701-segundo-revisor]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «camino completo con un solo proveedor», «ya hay dos proveedores», «camino ligero», «sin otro proveedor ni datos legibles»
- Fuente: openspec/changes/20261109-162444-701-segundo-revisor/specs/flujo/spec.md#estado_dice_que_segundo_revisor_falta_en_el_camino_completo

Tipo: funcional El sistema DEBE ofrecer en `estado --json` la clave `segundo_revisor`: el nombre de un revisor configurado cuyo proveedor todavía no informó, cuando el camino del candidato es completo y los informes de todos los candidatos del cambio cubren menos de dos proveedores distintos; en cualquier otro caso (camino ligero o sin calcular, ya hay dos proveedores, ningún revisor configurado de otro proveedor, configuración o informes ilegibles) DEBE ser `null`, sin cambiar ningún otro dato del estado.
