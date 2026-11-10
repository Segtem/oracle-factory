# cli.py: mudar los comandos del proyecto a su módulo para volver a tener margen bajo el tope

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-10 20:39:07 UTC)

OpenSpec: openspec/changes/20261110-203907-qfp-partir-cli. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-10 20:46:45 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261110-203907-qfp-partir-cli/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-10 20:46:57 UTC)

Requisitos importados: flujo_cc3654ad164ff3899.cli_py_queda_con_margen_bajo_su_tope (no funcional), flujo_cc3654ad164ff3899.lo_mudado_a_proyecto_sigue_igual (no funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-10 20:58:11 UTC)

Medidas de flujo_cc3654ad164ff3899.cli_py_queda_con_margen_bajo_su_tope: factory_partir_cli.cli_py_queda_con_margen_bajo_su_tope, factory_partir_cli.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 20:58:13 UTC)

Medidas de flujo_cc3654ad164ff3899.lo_mudado_a_proyecto_sigue_igual: factory_partir_cli.lo_mudado_a_proyecto_sigue_igual, factory_partir_cli.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 22:04:00 UTC)

Medidas de flujo_cc3654ad164ff3899.cli_py_queda_con_margen_bajo_su_tope: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 22:04:00 UTC)

Medidas de flujo_cc3654ad164ff3899.lo_mudado_a_proyecto_sigue_igual: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 22:49:50 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Mudanza mecánica sin cambio de comportamiento, hecha por mí con un script sobre el árbol sintáctico. Candidato 18ec893: evidencia verde (1399 pruebas, la suite entera; 3 casos de contrato). QUÉ CAMBIA: siete funciones (inicializar, plan_ejemplo, comando_migrar, comando_procedencia, comando_autonomia, comando_desplegar, comando_autopilot) pasan de cli.py a oracle_factory/proyecto.py con el patrón de lecturas.py (leen cli.NOMBRE al usarlo; cli las reexporta, el mismo objeto y la misma firma). cli.py pasa de 159984 a 139642 bytes: unos 20 KB de margen bajo su tope de 160000. PRUEBA EXISTENTE EDITADA (declarada, motivo del freno si aparece): tests/test_cli_modulos.py suma proyecto a MODULOS, para que le apliquen las reglas cm1/cm2 que ya valen para lecturas, flujo_revision y flujo_medidas; no se quitó ni se aflojó nada. CAMINO: completo, porque cuenta 444 líneas movidas y toca cli.py, aunque no cambia nada de lo que hace. REVISIÓN: sólo codex, una ronda, sin hallazgos (agy sin cuota). MUTACIONES: 3 de 3 detectadas (sacar proyecto de la vigilancia, leer ROOT sin cli., que cli.py vuelva a definir una función mudada). Un detalle del script: las columnas del árbol sintáctico de Python son bytes UTF-8, no caracteres; una aserción lo detectó antes de escribir nada y lo corregí.); 0 abiertos derivados; commit a1a395c377f972b741cd5935502fec78213b3eda; informe tareas/20261110-203907-qfp-partir-cli/revisiones/registro-oor3tjiu/informe.json; decisiones tareas/20261110-203907-qfp-partir-cli/revisiones/registro-oor3tjiu/decisiones.json.

### Nota (2026-11-10 22:50:16 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261110-203907-qfp-partir-cli/oracle-veredicto.txt.

### Nota (2026-11-10 22:51:03 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
