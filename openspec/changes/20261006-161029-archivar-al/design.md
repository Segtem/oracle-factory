# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Fusión:** un módulo `oracle_factory/archivo.py`, puro (texto de spec en, texto consolidado y lista de conflictos fuera), sin tocar el disco. Un requisito se identifica por su nombre (`### Requirement: <nombre>`), igual que en OpenSpec.
- **Spec consolidada:** `# Capability: <capacidad>`, `## Requirements` y cada requisito con su texto, sus escenarios y una línea `Origen: <ID> · <requisito de Oracle>`. Se escribe con reemplazo atómico.
- **Índice derivado:** `.factory/specs/<capacidad>.json` con, por requisito, el vigente y la cadena de los que reemplazó (cambio, requisito de Oracle, fecha). Es lo que leen `estado`, `donde` y luego `resumen`. Se puede regenerar desde los registros de los cambios archivados, en orden de archivo.
- **Cierre:** `cerrar` calcula la fusión antes de pedir la confirmación; si hay conflicto no pregunta. Cierra la tarea y el registro primero y fusiona después: si se corta antes, nada quedó fusionado y el cierre se reintenta; si se corta después, el cambio queda cerrado sin archivar y `archivar` lo completa. (La primera versión fusionaba antes de cerrar; R2 mostró que un reintento con la spec cambiada dejaba la consolidada vieja.)
- **Mapeo:** `capacidades` en `.factory/config.json` (`{"estructura2": "estructura"}`); `config_proyecto` lo valida.
- **Retroactivo:** `oracle-factory archivar --existentes` (o un paso de `migrar`) archiva los cerrados que no tienen marca, en el orden de su evento de cierre. Idempotente.
- **Huella:** una spec consolidada que Factory generó (la que tiene índice en `.factory/specs/`) queda fuera de la huella del producto: se deriva de specs ya aceptadas, y si contara, archivar los cambios existentes vencería al último cambio integrado. Cualquier otro archivo de `openspec/specs/` sigue contando. Para que una edición a mano no pase inadvertida, Factory se niega a fusionar sobre una spec que no coincide con su índice, y el verificador lo comprueba.
