# Design

Notas para implementar después de la aceptación. No son parte del contrato. Borrador de partida: la propuesta de Agy2 (`tareas/<ID>/propuesta-resumen-agy2.md`).

- **Módulo puro** `oracle_factory/resumen.py`: recibe los datos ya leídos (índices de `.factory/specs/`, registros, decisiones e informes de revisión) y devuelve el texto. La CLI lee y escribe.
- **Fuentes:** índices de las specs consolidadas (requisitos vigentes y reemplazados); `requisitos/<rid>.requisito` (`medido_por`); registro del cambio de origen (`oracle.codigo`, `cierre.cuando`, `medidas[rid]`); `pendientes_actuales` para los abiertos; `revision.decisiones` (estado `riesgo_aceptado`) y `revision.informe` (`limites`) de los cerrados.
- **Huella y `--verificar`:** como la salida es determinista, `--verificar` regenera el texto en memoria y lo compara con el archivo; la primera línea lleva el sha256 del cuerpo para que se vea a simple vista si alguien lo editó. «Lo que falta» de los cambios abiertos sale de `pendientes_actuales` y depende de la huella del producto: si un commit vence una revisión, el resumen queda viejo, y eso es correcto porque lo que muestra ya no es cierto.
- **Al cerrar y archivar:** después de `marcar_archivado` y `guardar`. Si falla la generación, el cierre ya está hecho y `resumen` lo repara.
