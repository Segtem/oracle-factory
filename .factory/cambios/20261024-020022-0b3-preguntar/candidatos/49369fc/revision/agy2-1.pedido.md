Sos un revisor independiente del cambio 20261024-020022-0b3-preguntar de un proyecto que usa Oracle Factory: «Preguntar responde sobre el registro y reconoce los límites de la búsqueda documental». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-preguntar/openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato 49369fc (sólo lectura): /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/49369fc-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/49369fc/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/revision/agy-1.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/beb247d/revision/agy2-1.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/revision/agy-2.json
- .factory/cambios/20261024-020022-0b3-preguntar/candidatos/4aba166/revision/agy2-2.json
Fuera del paquete, porque no son producto (.factory, kb/cambios/20261024-020022-0b3-preguntar.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-preguntar/.factory/local/revisores/49369fc-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-preguntar/.factory/local/revisores/49369fc-agy2-1/informe.json --paquete /home/workstation/Dev/factory-preguntar/.factory/cambios/20261024-020022-0b3-preguntar/candidatos/49369fc/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-preguntar/.factory/local/revisiones/49369fc-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3. Revisá el cambio contra los seis requisitos de openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md. La base es 4aba166, ya revisada por agy y agy2 en la segunda vuelta; el paquete completo desde tarea/docs excedió el límite de Clue. Declarar este alcance incremental y leer también los archivos completos actuales, la spec y ambos informes previos. Revisar todas las correcciones posteriores: interpretar preguntas compuestas antes de filtros; abstención antes de llamar al modelo; ordinales/versiones; presupuesto acumulado previo a registrar fuentes; vigencia normativa contra antecedentes; alcances actual/antecedentes/exclusiones; índice sin perder embeddings; exclusiones sólo como literal negativo; control de pensamiento; citas por fragmentos conocidos sin texto inventado; enum del esquema final; normalización de tildes y plurales -ción/-sión en conceptos positivos. No cambiaron los casos de oro ni los umbrales respecto de la confirmación humana. Archivos: oracle_factory/consultas.py, generacion.py, rag.py, tests/test_preguntar.py, tools/mutar_preguntar.py, tools/verify_preguntar.py, docs/conocimiento.md y catálogo de corrida. La evidencia commiteada está en .factory/cambios/20261024-020022-0b3-preguntar/candidatos/49369fc/evidencia: 474 pruebas OK, 10 omitidas, 49/49 mutaciones, fuentes estables, documental 20/22, registro 6/6, generativa real 4/4 y negativas 3/3 con qwen2.5:14b. Inspeccioná el detalle real, no confíes en los conceptos mínimos ni en el informe del autor. En particular la respuesta pq-vigencia agrega que cambios del catálogo no afectan directamente la vigencia de una revisión: comprobá si eso es cierto con huella de producto y fuentes. Los conceptos y la pertenencia textual no certifican inferencia semántica. Evaluá fallas concretas reproducibles del producto, sensor o evaluación, sin pedir comprensión universal. Para hallazgos fuera del diff detallá ruta y reproducción en summary/checks y declaralo como límite, sin inventar un ancla dentro del hunk. Creá un entorno propio ignorado en tu checkout si falta con uv venv .venv y uv pip install -q -p .venv -e . . Para probar usá exactamente, en primer plano y desde la raíz: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_preguntar tests.test_rag tests.test_mcp tests.test_docs </dev/null . No corras la suite completa ni modelos reales. No cambies fuentes ni la configuración Git de ningún repositorio, no commitees ni ejecutes decisiones de persona. Nombrá rutas relativas, severidad, explicación y disparador de cada hallazgo.
