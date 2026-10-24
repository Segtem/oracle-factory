Sos un revisor independiente del cambio 20261024-020022-0b3-preguntar de un proyecto que usa Oracle Factory: «Preguntar responde sobre el registro y reconoce los límites de la búsqueda documental». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato beb247d (sólo lectura): /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/beb247d-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261024-020022-0b3-preguntar.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.la_elaboracion_usa_herramientas_acotadas_y_un_modelo_explicito.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.la_evaluacion_distingue_exactitud_relevancia_y_abstencion.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.la_recuperacion_documental_expone_si_hay_respaldo_suficiente.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.la_respuesta_conserva_su_significado_en_cli_mcp_y_vs_code.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.preguntar_cuenta_y_lista_cambios_desde_el_registro_vigente.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.preguntar_elabora_respuestas_a_preguntas_abiertas_del_proyecto.md, tareas): 11 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-preguntar/.factory/local/revisores/beb247d-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-preguntar/.factory/local/revisores/beb247d-agy2-1/informe.json --paquete /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/beb247d-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá contra los seis requisitos de openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md: oracle_factory/consultas.py, generacion.py, rag.py, cambios de cli.py/mcp.py/extensión, tests/test_preguntar.py, herramientas de mutación/evidencia y catálogos. La base es tarea/docs, ya cerrado y revisado; evaluá el diff de preguntar. La primera evidencia está commiteada en /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/evidencia: 474 pruebas OK, fuentes estables, documental 21/22, registro 6/6, negativas 3/3, generativa real 2/4. Esa insuficiencia ya se está diagnosticando: no la presentes como un hallazgo nuevo sin una causa concreta. Inspeccioná respuestas/citas y la fidelidad semántica, no sólo el conteo. Mirá especialmente vigencia y pendientes del registro, límites de herramientas/tiempo/contexto, parámetros de proveedores, evaluación que no oculte errores y conservación de significado en los clientes. Para no importar código de otro candidato, creá en tu checkout su propio entorno ignorado si falta: uv venv .venv y uv pip install -q -p .venv -e .; esto no modifica fuentes. Después usá exactamente, desde la raíz del checkout y en primer plano: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_preguntar tests.test_rag tests.test_mcp tests.test_docs </dev/null . No corras la suite completa ni un modelo real. No cambies configuración de Git ni fuentes del producto, no commitees ni ejecutes decisiones de una persona. Informá cada hallazgo con severidad, ruta relativa, explicación y caso reproducible.
