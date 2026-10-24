Sos un revisor independiente del cambio 20261024-020022-0b3-preguntar de un proyecto que usa Oracle Factory: «Preguntar responde sobre el registro y reconoce los límites de la búsqueda documental». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato 4aba166 (sólo lectura): /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/4aba166-agy-2
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/clue/paquete-agy-2.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/revision/agy-1.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/cambios/20261024-020022-0b3-preguntar.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.la_evaluacion_distingue_exactitud_relevancia_y_abstencion.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.la_recuperacion_documental_expone_si_hay_respaldo_suficiente.md, kb/requisitos/conocimiento_cc12f23b7134ebe23.preguntar_elabora_respuestas_a_preguntas_abiertas_del_proyecto.md, tareas): 26 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-preguntar/.factory/local/revisores/4aba166-agy-2/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-preguntar/.factory/local/revisores/4aba166-agy-2/informe.json --paquete /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/clue/paquete-agy-2.json --repo /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/4aba166-agy-2
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2 incremental desde el candidato ya revisado beb247d. Se corrigieron consultas, vigencia del registro, páginas y orden, límites/proveedores, procedencia, lotes y evaluación; la calidad real aún falla. Inspeccioná la fidelidad semántica y las causas reproducibles, también código completo cuando haga falta. No des por resuelto un hallazgo sólo por lo que dice el autor. Revisá contra los seis requisitos de openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md: oracle_factory/consultas.py, generacion.py, rag.py, cambios de cli.py/mcp.py/extensión, tests/test_preguntar.py, herramientas de mutación/evidencia y catálogos. La base es beb247d, candidato que ambos revisaron en la primera vuelta. El paquete completo desde tarea/docs excede el límite de Clue. Revisá las correcciones acumuladas; leé también los archivos completos y la spec, y declaralo como límite de alcance. Si encontrás un problema fuera del diff, detallalo igualmente en summary/checks con ubicación y reproducción, sin fabricar una ubicación dentro de un hunk. La evidencia nueva está commiteada en .factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/evidencia: 474 pruebas OK (10 omitidas), fuentes estables, documental 21/22, registro 6/6, generativa real 2/4 y negativas 2/3. La evidencia falló: el modelo dio una explicación demasiado general sobre clones, repitió un procedimiento histórico en vigencia y pidió aclaración sobre una cafetera. Esa insuficiencia ya es conocida: buscá causas concretas en recuperación, fuentes, herramientas y validación; no presentes el número de fallas solo como hallazgo. La primera vuelta de agy y agy2 ya fue corregida; revisá también esos arreglos, sin confiar en la descripción del autor. Inspeccioná respuestas/citas y la fidelidad semántica, no sólo el conteo. Mirá especialmente vigencia y pendientes del registro, límites de herramientas/tiempo/contexto, parámetros de proveedores, evaluación que no oculte errores y conservación de significado en los clientes. Para no importar código de otro candidato, creá en tu checkout su propio entorno ignorado si falta: uv venv .venv y uv pip install -q -p .venv -e .; esto no modifica fuentes. Después usá exactamente, desde la raíz del checkout y en primer plano: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_preguntar tests.test_rag tests.test_mcp tests.test_docs </dev/null . No corras la suite completa ni un modelo real. No cambies configuración de Git ni fuentes del producto, no commitees ni ejecutes decisiones de una persona. Informá cada hallazgo con severidad, ruta relativa, explicación y caso reproducible.
