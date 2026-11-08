---
generado: oracle-factory kb
id: "flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas"
vigente: true
---

# el conductor decide el siguiente paso por reglas

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas`
- Vigente: sí
- Cambio: [[cambios/20261108-220606-51z-autopilot]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «una decisión de persona», «un comando mecánico», «trabajo creativo», «construir»
- Fuente: openspec/changes/20261108-220606-51z-autopilot/specs/flujo/spec.md#el_conductor_decide_el_siguiente_paso_por_reglas

Tipo: funcional El sistema DEBE decidir, solo con los datos de `estado` del cambio y por reglas fijas, una acción entre `terminado`, `frenar`, `pedir_a_persona`, `delegar_al_agente` y `actuar`, con el comando o la instrucción, quién actúa y el motivo de la regla. Un comando de decisión de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `abandonar`, `modo`, `autonomia`, `soltar`, `decidir-union`) DEBE ser siempre `pedir_a_persona`; un comando mecánico (`importar`, `juzgar`, `pedir-revision`, `revision-preparar`, `tomar`, `mensaje`) DEBE ser `actuar`; un paso escrito en prosa (corregir, commitear, resolver) o elegir medidas DEBE ser `delegar_al_agente`; y si un paso de revisión llega sin candidato, la acción es construir, también `delegar_al_agente`.
