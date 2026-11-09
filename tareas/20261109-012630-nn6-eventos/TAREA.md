# El registro tolera eventos que no son objetos

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-09 01:26:30 UTC)

OpenSpec: openspec/changes/20261109-012630-nn6-eventos. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-09 01:27:03 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-012630-nn6-eventos/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 01:27:17 UTC)

Requisitos importados: flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos (funcional), flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-09 01:29:22 UTC)

Medidas de flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos: factory_eventos_raros.leer_ignora_los_eventos_que_no_son_objetos, factory_eventos_raros.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 01:29:24 UTC)

Medidas de flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros: factory_eventos_raros.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros, factory_eventos_raros.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 01:29:46 UTC)

Medidas de flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 01:29:46 UTC)

Medidas de flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 01:57:42 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos revisores sobre el candidato 079ec8f, sin hallazgos: agy (pedido por el conductor autopilot, que lo corrió él solo) y codex. Evidencia 1329 pruebas OK, 3 casos de contrato. 12 mutaciones propias, todas detectadas (dos revelaron pruebas débiles mías que reforcé: un aviso espurio escondido porque preparar ya había leído el cambio y una cantidad comprobada con un dígito que también está en el id). Toca reglas de decisión (cli.py): camino completo. Sin pruebas existentes editadas. cli.leer pasa el registro por sin_eventos_raros: ignora los eventos que no son objetos, trata un eventos que no es una lista como vacío, avisa una vez por cambio por stderr, no toca el archivo al leer y un registro sano no cambia ni avisa. Decisión declarada en la propuesta: cuando otro comando guarda el registro, los eventos ignorados no se vuelven a escribir. Límites: sólo cubre lo que pasa por cli.leer; no valida los campos de los eventos que sí son objetos; el aviso se emite una vez por cambio y por proceso. Es el cambio con el que se probó por primera vez el autopilot en un cambio real.); 0 abiertos derivados; commit b2d18c00de191e8ea2b9d746476f73e60e30ef8b; informe tareas/20261109-012630-nn6-eventos/revisiones/registro-v6ung8z2/informe.json; decisiones tareas/20261109-012630-nn6-eventos/revisiones/registro-v6ung8z2/decisiones.json.

### Nota (2026-11-09 01:57:55 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-012630-nn6-eventos/oracle-veredicto.txt.

### Nota (2026-11-09 01:58:00 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-012630-nn6-eventos/oracle-veredicto.txt.

### Nota (2026-11-09 02:23:17 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
