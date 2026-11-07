---
generado: oracle-factory kb
id: "despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto"
vigente: true
---

# se prueba cada destino y el conjunto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto`
- Vigente: sí
- Cambio: [[cambios/20261106-205202-8od-destinos]]
- Veredicto: cumple
- Medidas: `factory_despliegue.se_prueba_cada_destino_y_el_conjunto`, `factory_despliegue.corrida_completa`
- Fuente: openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md#se_prueba_cada_destino_y_el_conjunto

Tipo: funcional El sistema DEBE ejecutar, por destino y en orden, comprobar que se alcanza, construir, desplegar, verificar que corre la versión del plan y correr su prueba de humo, y DEBE correr al final la prueba de conjunto declarada; DEBE decir «todo quedó funcionando» sólo cuando cada destino del plan quedó probado con la versión del plan y la prueba de conjunto pasó, y un destino que no se alcanzó DEBE quedar «inalcanzable», nunca verde.
