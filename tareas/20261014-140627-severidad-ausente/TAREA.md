# Spec de revisores: un informe sin severidad no se guarda

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-14 14:06:27 UTC)

OpenSpec: openspec/changes/20261014-140627-severidad-ausente. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-14 14:07:36 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261014-140627-severidad-ausente/specs/revisores/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-14 14:07:44 UTC)

Requisitos importados: revisores_cd964f597ba125312.el_corte_de_vueltas_sigue_la_severidad (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-14 14:11:01 UTC)

Medidas de revisores_cd964f597ba125312.el_corte_de_vueltas_sigue_la_severidad: factory_severidad.el_corte_de_vueltas_sigue_la_severidad, factory_severidad.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-14 14:11:50 UTC)

Medidas de revisores_cd964f597ba125312.el_corte_de_vueltas_sigue_la_severidad: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-14 14:43:40 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: dos vueltas de codex y agy, a la vez. La 1: agy un alto, un medio y dos bajos, codex un bajo. Corregidos el medio (la pérdida de severidad ahora con dos revisores: decide el informe que queda) y el bajo repetido (vs1 lee el próximo paso de estado por la CLI). El alto no era cierto: el sensor compara con Counter(expected), así que un caso que falta o se repite da incompleto (comprobado). El bajo de «alta» sin escenario propio no se cambió: alta y media van por la misma rama del corte. La 2 no encontró nada. Suite 345 y evidencia en verde.); 0 abiertos derivados; commit 273e7faa1e0080924ec6e785f506468cad4d6eac; informe tareas/20261014-140627-severidad-ausente/revisiones/registro-f4cqrm25/informe.json; decisiones tareas/20261014-140627-severidad-ausente/revisiones/registro-f4cqrm25/decisiones.json.

### Nota (2026-10-14 14:43:51 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261014-140627-severidad-ausente/oracle-veredicto.txt.

### Nota (2026-10-14 14:44:44 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
