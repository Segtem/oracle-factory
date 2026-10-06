# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Fusión:** un módulo `oracle_factory/archivo.py`, puro (texto de spec en, texto consolidado y lista de conflictos fuera), sin tocar el disco. Un requisito se identifica por su nombre (`### Requirement: <nombre>`), igual que en OpenSpec.
- **Spec consolidada:** `# Capability: <capacidad>`, `## Requirements` y cada requisito con su texto, sus escenarios y una línea `Origen: <ID> · <requisito de Oracle>`. Se escribe con reemplazo atómico.
- **Índice derivado:** `.factory/specs/<capacidad>.json` con, por requisito, el vigente y la cadena de los que reemplazó (cambio, requisito de Oracle, fecha). Es lo que leen `estado`, `donde` y luego `resumen`. Se puede regenerar desde los registros de los cambios archivados, en orden de archivo.
- **Cierre:** `cerrar` calcula la fusión antes de pedir la confirmación; si hay conflicto no pregunta. Escribe spec e índice antes de marcar el registro como cerrado y archivado; si algo falla, no queda un cierre a medias.
- **Mapeo:** `capacidades` en `.factory/config.json` (`{"estructura2": "estructura"}`); `config_proyecto` lo valida.
- **Retroactivo:** `oracle-factory archivar --existentes` (o un paso de `migrar`) archiva los cerrados que no tienen marca, en el orden de su evento de cierre. Idempotente.
- **Huella:** `openspec/specs/` queda fuera de la huella del producto, como `.factory/` y los registros: la deriva Factory de specs ya aceptadas (que sí son producto). Si fuera producto, un cierre cortado no se podría reintentar (su propia fusión vencería la revisión; lo mostró la prueba del reintento) y archivar los cambios existentes vencería al último cambio integrado. Como no se edita a mano, el verificador comprueba que el texto coincide con el que sale del índice.
