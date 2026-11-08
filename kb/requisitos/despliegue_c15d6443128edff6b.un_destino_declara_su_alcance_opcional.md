---
generado: oracle-factory kb
id: "despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional"
vigente: true
---

# un destino declara su alcance opcional

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional`
- Vigente: sí
- Cambio: [[cambios/20261108-020932-3t5-alcance]]
- Veredicto: no cumple
- Medidas: `factory_destinos_alcance.un_destino_declara_su_alcance_opcional`, `factory_destinos_alcance.corrida_completa`
- Fuente: openspec/changes/20261108-020932-3t5-alcance/specs/despliegue/spec.md#un_destino_declara_su_alcance_opcional

Tipo: funcional El sistema DEBE aceptar en cada destino un campo opcional `alcance` con una lista no vacía de rutas de Git, y DEBE rechazar con un mensaje que nombre el destino un `alcance` que no sea una lista no vacía de textos no vacíos.
