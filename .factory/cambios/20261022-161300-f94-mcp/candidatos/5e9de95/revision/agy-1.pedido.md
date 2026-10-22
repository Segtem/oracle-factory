Sos un revisor independiente del cambio 20261022-161300-f94-mcp de un proyecto que usa Oracle Factory: «Preguntar al proyecto desde el editor y desde un agente: el comando de VS Code y oracle-factory mcp, de sólo lectura». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-mcp/openspec/changes/20261022-161300-f94-mcp/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-mcp/openspec/changes/20261022-161300-f94-mcp/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato 5e9de95 (sólo lectura): /home/workstation/Dev/factory-mcp/.factory/local/revisiones/5e9de95-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-mcp/.factory/cambios/20261022-161300-f94-mcp/candidatos/5e9de95/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261022-161300-f94-mcp.md, kb/requisitos/conocimiento_cff5a3575a1b86452.preguntar_desde_vs_code.md, kb/requisitos/conocimiento_cff5a3575a1b86452.un_agente_consulta_el_proyecto_por_mcp_sin_poder_cambiarlo.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-mcp/.factory/local/revisores/5e9de95-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-mcp/.factory/local/revisores/5e9de95-agy-1/informe.json --paquete /home/workstation/Dev/factory-mcp/.factory/cambios/20261022-161300-f94-mcp/candidatos/5e9de95/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-mcp/.factory/local/revisiones/5e9de95-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio, contra los 2 requisitos de su spec: oracle_factory/mcp.py (el servidor MCP por stdio: protocolo, herramientas, validación de argumentos, cómo corre la CLI), el subcomando mcp en oracle_factory/cli.py, la extensión de VS Code (factory.preguntar en editores/vscode/extension.js, el botón en tablero.js, package.json 0.5.0), tests/test_mcp.py, tests/tablero_en_node.cjs, tools/verify_mcp.py, catalogos/factory_mcp.*.oracle y el README. Mirá especialmente: que ninguna herramienta pueda cambiar el proyecto o leer fuera de él, inyección de opciones o rutas por los argumentos, que un error corte el servidor o ensucie stdout, respuestas que no sigan el protocolo MCP, y que la extensión no corra nada que no deba. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-mcp/.venv/bin/python -m unittest tests.test_mcp </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
