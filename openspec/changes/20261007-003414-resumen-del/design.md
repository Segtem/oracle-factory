# Design

Notas para implementar después de la aceptación. No son parte del contrato. Borrador de partida: la propuesta de Agy2 (`tareas/<ID>/propuesta-resumen-agy2.md`).

- **Módulo puro** `oracle_factory/resumen.py`: recibe los datos ya leídos (índices de `.factory/specs/`, registros, decisiones e informes de revisión) y devuelve el texto. La CLI lee y escribe.
- **Fuentes:** índices de las specs consolidadas (requisitos vigentes y reemplazados); `requisitos/<rid>.requisito` (`medido_por`); registro del cambio de origen (`oracle.codigo`, `cierre.cuando`, `medidas[rid]`); `pendientes_actuales` para los abiertos; `revision.decisiones` (estado `riesgo_aceptado`) y `revision.informe` (`limites`) de los cerrados.
- **Huella:** sha256 de las entradas leídas, en orden de ruta, escrita en la primera línea como comentario HTML. `--verificar` recalcula y compara con el archivo.
- **Pendientes de los abiertos:** `pendientes_actuales` mira la huella del producto; cambia con cualquier commit. Se muestran, pero para la huella del resumen se usan sólo fase, modo y registro, así que un commit de código no vuelve viejo el resumen. Se aclara en el texto: «lo que falta» se calcula al generar.
- **Al cerrar y archivar:** después de `marcar_archivado` y `guardar`. Si falla la generación, el cierre ya está hecho y `resumen` lo repara.
