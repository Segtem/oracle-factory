---
generado: oracle-factory kb
id: "despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona"
vigente: true
---

# un despliegue es un plan que autoriza una persona

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona`
- Vigente: sí
- Cambio: [[cambios/20261106-205202-8od-destinos]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «simular no ejecuta nada», «un agente no autoriza», «la puerta en rojo»
- Fuente: openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md#un_despliegue_es_un_plan_que_autoriza_una_persona

Tipo: funcional El sistema DEBE armar el plan de despliegue de un commit de la rama de despliegue —los destinos en el orden de sus dependencias— y mostrarlo antes de ejecutar algo, DEBE negarse si la puerta local no está en verde o si el commit no está en esa rama, y DEBE ejecutarlo sólo cuando una persona lo autoriza: un agente puede armarlo y simularlo, pero no autorizarlo, y ningún despliegue arranca solo.
