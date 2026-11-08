---
generado: oracle-factory kb
id: "practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado"
vigente: true
---

# el verificador no pide casos para un requisito exceptuado

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado`
- Vigente: sí
- Cambio: [[cambios/20261108-115714-ohv-noaplica]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «un requisito exceptuado sin casos», «un caso para el requisito exceptuado», «los demás requisitos siguen exigiendo casos»
- Fuente: openspec/changes/20261108-115714-ohv-noaplica/specs/practicas/spec.md#el_verificador_no_pide_casos_para_un_requisito_exceptuado

Tipo: funcional El sistema DEBE tratar el requisito que la spec marca con «Pruebas: no aplica — motivo» como un requisito que no necesita casos: el verificador DEBE derivar el contrato sin él, conservar la numeración de los demás (`test_<letras><n>_…` sigue siendo el requisito `n` de la spec) y NO DEBE aceptar un caso que nombre un requisito exceptuado.
