# Partir cli.py en módulos para alejarlo del límite de Oracle Clue

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-28 22:26:56 UTC)

OpenSpec: openspec/changes/20261028-222656-b2m-clidividido. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-28 22:29:07 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261028-222656-b2m-clidividido/specs/cli/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-28 22:29:19 UTC)

Requisitos importados: cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse (funcional), cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo (funcional), cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-28 22:53:37 UTC)

Medidas de cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse: factory_cli_modulos.la_cli_se_comporta_igual_tras_partirse, factory_cli_modulos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-28 22:53:39 UTC)

Medidas de cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo: factory_cli_modulos.lo_movido_lee_a_cli_en_el_momento_de_usarlo, factory_cli_modulos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-28 22:53:40 UTC)

Medidas de cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope: factory_cli_modulos.ningun_archivo_fuente_pasa_del_tope, factory_cli_modulos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-28 22:59:23 UTC)

Medidas de cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-28 22:59:23 UTC)

Medidas de cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-28 22:59:23 UTC)

Medidas de cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-28 23:13:07 UTC)

Medidas de cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-10-28 23:13:08 UTC)

Medidas de cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-10-28 23:13:09 UTC)

Medidas de cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-10-28 23:15:02 UTC)

Medidas de cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-28 23:15:03 UTC)

Medidas de cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-28 23:15:03 UTC)

Medidas de cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-28 23:42:33 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Una vuelta de agy y agy2, sin hallazgos. 707 pruebas y 18 casos de contrato en verde, sin modificar ninguna prueba existente. Comprobación propia: las 68 funciones movidas son idénticas al original en el árbol sintáctico, tras quitar el prefijo cli. y la sustitución de sys.modules[__name__]; ninguna función que sigue en cli.py cambió y no se perdió ninguna. cli.py pasó de 253965 a 137054 bytes. Un defecto de importación circular (importar primero un módulo nuevo fallaba) se encontró y corrigió antes de la revisión. Límite: la equivalencia se comprobó por el árbol sintáctico y por las 707 pruebas, no ejecutando cada comando en cada situación; el tope real de Oracle Clue (256000) no se prueba, sólo los topes propios de 160000 y 200000.); 0 abiertos derivados; commit 9c04f216e69513b842491c89d471a55dde7ddcb1; informe tareas/20261028-222656-b2m-clidividido/revisiones/registro-blnvkeit/informe.json; decisiones tareas/20261028-222656-b2m-clidividido/revisiones/registro-blnvkeit/decisiones.json.

### Nota (2026-10-28 23:42:44 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261028-222656-b2m-clidividido/oracle-veredicto.txt.

### Nota (2026-10-28 23:46:27 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
