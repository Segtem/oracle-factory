# Frenos de construcción: avisos de estado que mandan parar

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 20:33:56 UTC)

OpenSpec: openspec/changes/20261108-203356-puy-frenos. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 20:35:02 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-203356-puy-frenos/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 20:36:59 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-203356-puy-frenos/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 20:37:08 UTC)

Requisitos importados: flujo_cf63459721e7fb9ac.estado_muestra_los_frenos (funcional), flujo_cf63459721e7fb9ac.los_frenos_salen_de_los_datos_del_cambio (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 20:39:02 UTC)

Medidas de flujo_cf63459721e7fb9ac.los_frenos_salen_de_los_datos_del_cambio: factory_frenos.los_frenos_salen_de_los_datos_del_cambio, factory_frenos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 20:39:04 UTC)

Medidas de flujo_cf63459721e7fb9ac.estado_muestra_los_frenos: factory_frenos.estado_muestra_los_frenos, factory_frenos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 20:49:12 UTC)

Medidas de flujo_cf63459721e7fb9ac.estado_muestra_los_frenos: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 20:49:12 UTC)

Medidas de flujo_cf63459721e7fb9ac.los_frenos_salen_de_los_datos_del_cambio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 21:18:52 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Codex sin hallazgos sobre bbd1646 (una ronda). Evidencia 1301 pruebas OK, 7 casos de contrato. 18 mutaciones propias, las 18 detectadas (5 sobrevivían y se cerraron con casos dentro de métodos existentes). Toca reglas de decisión (cli.py): camino completo. Los frenos son información: no cambian pendientes ni próximo paso, se calculan en cada consulta y un dato ilegible no produce un freno. Sin pruebas existentes editadas. Límites: los umbrales de cambio_grande y bucle_de_revision son los de estado y los dos juicios rojos seguidos son nuevos; estado ya fallaba con eventos que no son objetos (aviso_revision, preexistente, seguimiento aparte). La evidencia falló una vez por test_cm2 (lecturas debe llamar a cli.frenos_del_cambio) y se corrigió con una línea. Es el cambio 2 del autopilot: el conductor que obedece los frenos es el cambio 3.); 0 abiertos derivados; commit 93e7a17b7fb63583b40f053e5899a0e150124907; informe tareas/20261108-203356-puy-frenos/revisiones/registro-aqngyyje/informe.json; decisiones tareas/20261108-203356-puy-frenos/revisiones/registro-aqngyyje/decisiones.json.

### Nota (2026-11-08 21:19:20 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261108-203356-puy-frenos/oracle-veredicto.txt.

### Nota (2026-11-08 21:19:33 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
