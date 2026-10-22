---
generado: oracle-factory kb
id: "flujo_cbbf375bdcabddbc9.la_guia_para_agentes_se_genera_y_no_se_desactualiza"
vigente: true
---

# la guia para agentes se genera y no se desactualiza

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cbbf375bdcabddbc9.la_guia_para_agentes_se_genera_y_no_se_desactualiza`
- Vigente: sí
- Cambio: [[cambios/20261022-215347-y70-agentes]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «un proyecto con su propio AGENTS.md»
- Fuente: openspec/changes/20261022-215347-y70-agentes/specs/flujo/spec.md#la guía para agentes se genera y no se desactualiza

Tipo: funcional `oracle-factory agentes` SHALL escribir en `AGENTS.md` (creándolo si falta) un bloque entre marcas, armado desde la CLI, con quién decide qué en cada modo de trabajo según `modos.via_agente` (marcando el modo por defecto del proyecto), los comandos de una persona y los de un agente con `--agente`, cómo ver el próximo paso y cómo consultar el proyecto (estado, preguntar, por-que y el MCP); SHALL conservar lo que está fuera del bloque y SHALL agregar `@AGENTS.md` al `CLAUDE.md` si no lo tiene. `--verificar` SHALL fallar sin escribir si el bloque falta o no coincide, e `init` SHALL escribirlo.
