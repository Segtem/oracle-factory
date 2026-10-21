---
generado: oracle-factory kb
id: "revisores_c466ac292a9f99ce6.pedir_una_revision_del_candidato_actual"
vigente: true
---

# pedir una revision del candidato actual

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c466ac292a9f99ce6.pedir_una_revision_del_candidato_actual`
- Vigente: sí
- Cambio: [[cambios/20261007-192608-revisores]]
- Veredicto: cumple
- Medidas: `factory_revisores.pedir_una_revision_del_candidato_actual`, `factory_revisores.corrida_completa`
- Fuente: openspec/changes/20261007-192608-revisores/specs/revisores/spec.md#pedir una revisión del candidato actual

Tipo: funcional `pedir-revision ID --a NOMBRE` SHALL preparar el checkout y el paquete de Oracle Clue del candidato actual en sus rutas (`ruta ID checkout` y `ruta ID clue`), lanzar el comando del revisor NOMBRE con el pedido, esperar a que termine y, si el informe es válido para ese paquete, guardarlo en la carpeta `revision/` del candidato junto con el pedido usado.
