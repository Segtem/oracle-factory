Sos un revisor independiente del cambio 20261024-020022-0b3-preguntar de un proyecto que usa Oracle Factory: «Preguntar responde sobre el registro y reconoce los límites de la búsqueda documental». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato e962e47 (sólo lectura): /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/e962e47-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/e962e47/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/revision/agy-1.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/revision/agy2-1.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/revision/agy-2.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/revision/agy2-2.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/49369fc/revision/agy-1.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/49369fc/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/cambios/20261024-020022-0b3-preguntar.md, tareas): 14 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-preguntar/.factory/local/revisores/e962e47-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-preguntar/.factory/local/revisores/e962e47-agy2-1/informe.json --paquete /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/e962e47/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/e962e47-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 4, verificación final de correcciones. Base incremental 49369fc, ya revisada por ambos en agy-1/agy2-1; declarar este alcance y continuidad, sin repetir la auditoría de versiones antiguas. Spec: openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md. Comprobar que AGY-PREGUNTAR-15 y GENERACION-ELABORAR-CONTEO-CLAUSULA-SECUNDARIA-OMITE-REGISTRO quedaron corregidos: se examinan todas las cláusulas reconocidas, orden inverso, dos conteos con distinto filtro, rechazo de ejemplo documental y validación también después de reparación final. Revisar las otras diferencias desde 49369fc: instrucciones de pertinencia y negaciones respaldadas, evaluación que conserva signos C++/C, y exclusión de la afirmación falsa sobre catálogos y vigencia que ambos documentaron fuera del diff. La nueva evidencia commiteada está en .factory/cambios/20261024-020022-0b3-preguntar/candidatos/e962e47/evidencia: fuentes estables, 474 pruebas OK (10 omitidas), 51/51 mutaciones, documental 20/22, registro 6/6, generativa real 4/4 y negativas 3/3 con qwen2.5:14b. Inspeccionar las cuatro respuestas y fuentes reales; los conceptos mínimos no garantizan fidelidad semántica. Catálogos y umbrales siguen como Brian confirmó; los casos de oro se reforzaron para rechazar la falsedad observada. Archivos relevantes: oracle_factory/generacion.py, rag.py, tests/test_preguntar.py, tests/datos/preguntar-abiertas.json, tools/mutar_preguntar.py y docs/conocimiento.md; leer funciones relacionadas si hace falta. Entorno propio ignorado en tu checkout: uv venv .venv y uv pip install -q -p .venv -e . si falta. Pruebas exactamente en primer plano desde raíz: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_preguntar tests.test_rag tests.test_mcp tests.test_docs </dev/null . No suite completa ni modelos reales. No modificar fuentes ni configuración Git, no commitear ni decidir por una persona. Informar hallazgos concretos reproducibles y sus límites; no inventar anclas fuera del diff.
