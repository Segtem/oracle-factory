---
generado: oracle-factory kb
id: "colaboracion_cf0b1719108ccce04.el_banco_pone_a_prueba_el_trabajo_a_la_vez"
vigente: true
---

# el banco pone a prueba el trabajo a la vez

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_cf0b1719108ccce04.el_banco_pone_a_prueba_el_trabajo_a_la_vez`
- Vigente: sí
- Cambio: [[cambios/20261004-121432-coordinar-dos]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «dos personas a la vez»
- Fuente: openspec/changes/20261004-121432-coordinar-dos/specs/colaboracion/spec.md#el banco pone a prueba el trabajo a la vez

Tipo: funcional El banco de concurrencia SHALL correr, con dos personas en dos clones con su identidad de Git y un agente de prueba cada una, en un orden reproducible por una semilla y también con procesos simultáneos, estos escenarios: frentes en paralelo sobre archivos distintos; el mismo archivo; cambios que pasan solos y fallan juntos; dos `tomar` a la vez; decisiones simultáneas sobre un mismo registro; dos cambios con el mismo ID creados en dos clones; y los archivos que Factory genera y ambos tocan. En cada uno SHALL comprobar que no se pierde ni se atribuye a otra persona ninguna decisión, que un conflicto se detecta a más tardar al integrar y que ninguna evidencia o revisión vieja se da por vigente.
