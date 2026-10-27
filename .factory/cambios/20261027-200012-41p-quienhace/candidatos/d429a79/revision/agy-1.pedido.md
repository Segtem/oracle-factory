Sos un revisor independiente del cambio 20261027-200012-41p-quienhace de un proyecto que usa Oracle Factory: «El tablero dice qué hace cada quien y cuándo no te toca nada». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tablero-quien-hace/openspec/changes/20261027-200012-41p-quienhace/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tablero-quien-hace/openspec/changes/20261027-200012-41p-quienhace/specs/tablero/spec.md

Qué revisar:
- Checkout del candidato d429a79 (sólo lectura): /home/workstation/Dev/factory-tablero-quien-hace/.factory/local/revisiones/d429a79-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tablero-quien-hace/.factory/cambios/20261027-200012-41p-quienhace/candidatos/d429a79/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261027-200012-41p-quienhace.md, kb/requisitos/tablero_c36d16c32608f4c53.ahora_no_te_toca_nada.md, kb/requisitos/tablero_c36d16c32608f4c53.cada_pendiente_dice_quien_lo_hace.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tablero-quien-hace/.factory/local/revisores/d429a79-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tablero-quien-hace/.factory/local/revisores/d429a79-agy-1/informe.json --paquete /home/workstation/Dev/factory-tablero-quien-hace/.factory/cambios/20261027-200012-41p-quienhace/candidatos/d429a79/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-tablero-quien-hace/.factory/local/revisiones/d429a79-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261027-200012-41p-quienhace/specs/tablero/spec.md): oracle_factory/tablero.py (FRASES, PENDIENTES, _faltan, _paso y su uso en armar), editores/vscode/tablero.js (faltante, nadaPorHacer y cambio), tests/test_tablero_quien_hace.py, el cambio en tests/test_tablero.py, tools/verify_tablero_quien_hace.py, catalogos/factory_tablero_quien_hace.*.oracle y la frase nueva de docs/tablero.md. Mirá especialmente: que los patrones de PENDIENTES clasifiquen bien todos los textos que genera pendientes() y pendientes_actuales() en oracle_factory/cli.py (y no clasifiquen mal un texto parecido), que lo desconocido quede con su texto y sin responsable, que el aviso «Ahora no te toca nada» aparezca y no aparezca donde dice la spec, que todo texto del registro se escape, que el JSON siga siendo compatible (MCP, extensión, otras pruebas) y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_tablero_quien_hace tests.test_tablero </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
