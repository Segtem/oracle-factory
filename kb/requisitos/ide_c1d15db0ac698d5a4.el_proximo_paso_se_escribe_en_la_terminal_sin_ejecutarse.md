---
generado: oracle-factory kb
id: "ide_c1d15db0ac698d5a4.el_proximo_paso_se_escribe_en_la_terminal_sin_ejecutarse"
vigente: true
---

# el proximo paso se escribe en la terminal sin ejecutarse

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `ide_c1d15db0ac698d5a4.el_proximo_paso_se_escribe_en_la_terminal_sin_ejecutarse`
- Vigente: sí
- Cambio: [[cambios/20261016-101007-vscode]]
- Veredicto: cumple
- Medidas: `factory_vscode.el_proximo_paso_se_escribe_en_la_terminal_sin_ejecutarse`, `factory_vscode.corrida_completa`
- Fuente: openspec/changes/20261016-101007-vscode/specs/ide/spec.md#el próximo paso se escribe en la terminal sin ejecutarse

Tipo: funcional Para un próximo paso que es un comando de Factory, la vista SHALL ofrecer escribirlo en una terminal integrada del proyecto sin ejecutarlo, con la CLI que usa la extensión; un paso que no es un comando SHALL mostrarse sin botón. La extensión SHALL NOT tomar ninguna decisión ni correr comandos que la registren.
