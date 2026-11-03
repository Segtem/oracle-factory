---
generado: oracle-factory kb
id: "ide_cc0ded3b7b46b23f7.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido"
vigente: true
---

# la cli entrega cada clave declarada con un tipo permitido

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `ide_cc0ded3b7b46b23f7.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido`
- Vigente: sí
- Cambio: [[cambios/20261103-113909-oen-contratojson]]
- Veredicto: cumple
- Medidas: `factory_contrato_vscode.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido`, `factory_contrato_vscode.corrida_completa`
- Fuente: openspec/changes/20261103-113909-oen-contratojson/specs/ide/spec.md#la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido

Tipo: funcional El sistema DEBE fallar una prueba, nombrando el comando, la clave, el tipo esperado y el encontrado, cuando la CLI no entrega una clave declarada en el contrato o la entrega con un tipo que el contrato no permite, y NO DEBE fallar por claves de más en la salida de la CLI.
