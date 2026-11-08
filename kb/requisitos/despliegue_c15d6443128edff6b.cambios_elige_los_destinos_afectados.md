---
generado: oracle-factory kb
id: "despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados"
vigente: true
---

# cambios elige los destinos afectados

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados`
- Vigente: sí
- Cambio: [[cambios/20261108-020932-3t5-alcance]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «se cambia sólo lo de un destino», «lo que no se puede descartar entra», «un elegido arrastra lo que necesita»
- Fuente: openspec/changes/20261108-020932-3t5-alcance/specs/despliegue/spec.md#cambios_elige_los_destinos_afectados

Tipo: funcional El sistema DEBE ofrecer `desplegar --cambios`, que elige los destinos con archivos cambiados dentro de su `alcance` entre la última versión que Factory desplegó en ese destino y el commit del plan, DEBE incluir siempre los destinos sin `alcance`, los que nunca se desplegaron y aquellos cuya versión anterior no se puede comparar, y DEBE incluir también lo que los elegidos necesitan por `depende_de`.
