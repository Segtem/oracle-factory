# Guía de colaboración v2 con las fricciones del piloto

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: colaboracion, piloto


## Objetivo

Corregir en `docs/colaboracion.md` y en las plantillas las fricciones 2, 3, 4, 5, 9 y 10 del [piloto con agentes](../20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md):
- **Archivos compartidos por diseño:** un patrón por capacidad (`sensor_<cap>.py`, catálogos `<cap>.*`, relación `<cap>_comprobacion` con el campo `requisito` en un formato único) y quién edita `oracle.json` (`sensores`).
- **Commit de producto y commit de evidencia:** cuál se ofrece, cuál se revisa y qué va en «HEAD» de un relevo que se commitea.
- **Reparto y relevo:** quién actualiza el escritor activo y el estado del reparto después de un relevo o una entrega.
- **Registro de una integración de varios cambios:** `integracion.md` va en la tarea de un cambio y las otras lo referencian; `tareas/integracion-*` no es un ID válido de Task.
- **Riesgos aceptados por frente:** revisarlos otra vez contra el candidato integrado (R1-01).
- **`oracle cobertura --con`:** cuándo usarlo como verificación previa, sin registro.
