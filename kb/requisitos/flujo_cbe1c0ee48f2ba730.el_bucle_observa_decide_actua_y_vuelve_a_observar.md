---
generado: oracle-factory kb
id: "flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar"
vigente: true
---

# el bucle observa decide actua y vuelve a observar

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar`
- Vigente: sí
- Cambio: [[cambios/20261108-233304-ywj-actua]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «un comando mecánico», «trabajo creativo con agente», «trabajo creativo sin agente»
- Fuente: openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md#el_bucle_observa_decide_actua_y_vuelve_a_observar

Tipo: funcional El sistema DEBE, en cada vuelta, observar el estado, decidir con `autopilot.decidir`, y si la acción es `actuar` correr el comando de Factory con `--agente NOMBRE` en un proceso aparte, o si es `delegar_al_agente` lanzar el comando de `--lanzar` con la instrucción como último argumento (sin `--lanzar`, detenerse diciendo que falta), y volver a observar después de cada paso.
