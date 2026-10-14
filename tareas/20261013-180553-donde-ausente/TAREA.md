# Spec de cli: el escenario de donde con un artefacto ausente

- ESTADO: CERRADA
- PRIORIDAD: 10
- ETIQUETAS: 

### Nota (2026-10-13 18:05:53 UTC)

Hallazgo CLI-JSON-001 (agy, medio) de 20261013-153440-cli-json, nombrado como límite en su revisión: el escenario «donde con un artefacto ausente» dice «un cambio sin evidencia → la evidencia figura ausente», pero donde lista la evidencia de un candidato sólo cuando existe; cumplirlo así cambiaría el texto de donde, que el mismo cambio promete no cambiar. Reescribir con un MODIFIED: lo ausente es un artefacto que un registro nombra y ya no está (como los hechos de un juicio registrado), que es lo que se probó. De paso, el design.md de cli-json dice que la vigencia usa sólo mismo_producto: desde la vuelta 1 usa juicio_vigente y problemas_de_revision, como estado en texto.

### Nota (2026-10-14 19:59:17 UTC)

Hecho en el cambio 20261014-145018-donde-ausente (merge 70d66a6): MODIFIED de donde_y_resumen_se_leen_como_json; ausente es lo que el cambio espera y no está (fijos de la convención o lo que un registro nombra), los históricos e inválidos no cuentan, y resumen agrupa los pendientes de medidas iguales. cj2 más estrictos. La frase vieja del design.md de cli-json se corrige en la propuesta, sin reescribir ese cambio cerrado.
