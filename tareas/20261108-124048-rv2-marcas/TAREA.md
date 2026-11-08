# El comprobador del sitio detecta bloques marcados duplicados

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 12:40:49 UTC)

OpenSpec: openspec/changes/20261108-124048-rv2-marcas. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 12:41:57 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-124048-rv2-marcas/specs/web/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 12:42:20 UTC)

Requisitos importados: web_c5280d3ce46f7827d.el_comprobador_del_sitio_rechaza_un_bloque_marcado_duplicado (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 12:42:58 UTC)

Medidas de web_c5280d3ce46f7827d.el_comprobador_del_sitio_rechaza_un_bloque_marcado_duplicado: factory_marcas.el_comprobador_del_sitio_rechaza_un_bloque_marcado_duplicado, factory_marcas.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 12:43:23 UTC)

Medidas de web_c5280d3ce46f7827d.el_comprobador_del_sitio_rechaza_un_bloque_marcado_duplicado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 13:13:03 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Camino ligero: un revisor, una ronda, sin hallazgos medios ni altos. Codex: un hallazgo bajo (heurístico): el control cuenta sólo los marcadores exactos que escribe la herramienta (<!-- bloque --> y <!-- /bloque -->), así que una segunda pareja con espacios extra o mayúsculas pasa inadvertida. Propongo aceptarlo como límite declarado: el escritor sólo genera la forma canónica, y detectar variantes de un comentario HTML es heurístico y no se cierra por rondas. Evidencia 1260 pruebas OK, 5 casos. 6 mutaciones propias, las 6 detectadas. Sin ediciones a pruebas existentes. 83 líneas de producto en tools/sitio_paginas.py.); 0 abiertos derivados; commit 2bef3490cc0c98221632ba8a3c8f608ab5da5d5f; informe tareas/20261108-124048-rv2-marcas/revisiones/registro-70vu9gxs/informe.json; decisiones tareas/20261108-124048-rv2-marcas/revisiones/registro-70vu9gxs/decisiones.json.

### Nota (2026-11-08 13:13:12 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261108-124048-rv2-marcas/oracle-veredicto.txt.

### Nota (2026-11-08 13:13:39 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
