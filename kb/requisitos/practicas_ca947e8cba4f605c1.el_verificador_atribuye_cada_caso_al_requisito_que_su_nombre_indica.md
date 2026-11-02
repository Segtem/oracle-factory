---
generado: oracle-factory kb
id: "practicas_ca947e8cba4f605c1.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica"
vigente: true
---

# el verificador atribuye cada caso al requisito que su nombre indica

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `practicas_ca947e8cba4f605c1.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica`
- Vigente: sí
- Cambio: [[cambios/20261102-000745-j7r-verificadorgenerico]]
- Veredicto: sin juicio
- Medidas: `factory_verificador_generico.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica`, `factory_verificador_generico.corrida_completa`
- Fuente: openspec/changes/20261102-000745-j7r-verificadorgenerico/specs/practicas/spec.md#el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica

Tipo: funcional El sistema DEBE atribuir cada prueba `test_<letras><n>_…` de un módulo al requisito número `n` de la spec del cambio, en el orden en que la spec los lista, y DEBE negarse a declarar éxito si algún requisito no tiene casos, si un caso nombra un número sin requisito, o si el módulo no tiene casos.
