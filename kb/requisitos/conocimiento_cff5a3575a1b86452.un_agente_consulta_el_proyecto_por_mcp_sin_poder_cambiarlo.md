---
generado: oracle-factory kb
id: "conocimiento_cff5a3575a1b86452.un_agente_consulta_el_proyecto_por_mcp_sin_poder_cambiarlo"
vigente: true
---

# un agente consulta el proyecto por mcp sin poder cambiarlo

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_cff5a3575a1b86452.un_agente_consulta_el_proyecto_por_mcp_sin_poder_cambiarlo`
- Vigente: sí
- Cambio: [[cambios/20261022-161300-f94-mcp]]
- Veredicto: cumple
- Medidas: `factory_mcp.un_agente_consulta_el_proyecto_por_mcp_sin_poder_cambiarlo`, `factory_mcp.corrida_completa`
- Fuente: openspec/changes/20261022-161300-f94-mcp/specs/conocimiento/spec.md#un agente consulta el proyecto por MCP sin poder cambiarlo

Tipo: funcional `oracle-factory mcp` SHALL atender por la entrada y la salida estándar el protocolo MCP (initialize, tools/list, tools/call) con las herramientas preguntar, estado, buscar, por_que, resumen, log y listar, que SHALL devolver lo mismo que el comando de la CLI correspondiente. Ninguna herramienta SHALL cambiar archivos del proyecto (salvo el índice local de preguntar), un argumento SHALL ser rechazado si no tiene el tipo o la forma esperada (un texto nunca se toma como una opción) y un error SHALL volver como resultado de error de la herramienta sin cortar el servidor.
