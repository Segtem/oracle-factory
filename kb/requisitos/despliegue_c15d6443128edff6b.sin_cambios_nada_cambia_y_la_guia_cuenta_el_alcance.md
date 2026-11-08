---
generado: oracle-factory kb
id: "despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance"
vigente: true
---

# sin cambios nada cambia y la guia cuenta el alcance

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance`
- Vigente: sí
- Cambio: [[cambios/20261108-020932-3t5-alcance]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «sin la opción», «las dos opciones juntas», «la guía y la plantilla»
- Fuente: openspec/changes/20261108-020932-3t5-alcance/specs/despliegue/spec.md#sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance

Tipo: funcional El sistema NO DEBE cambiar lo que hace `desplegar` sin `--cambios`, DEBE negar `--cambios` junto con `--destino`, y DEBE contar el campo `alcance`, la opción y sus límites en `docs/despliegue.md` y en la plantilla `docs/plantillas/destinos.json`.
