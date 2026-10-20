Sos un revisor independiente del cambio 20261020-141303-sesion de un proyecto que usa Oracle Factory: «La sesión de Live Share desde el tablero: compartir, unirse, terminar e instalar». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-sesion/openspec/changes/20261020-141303-sesion/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-sesion/openspec/changes/20261020-141303-sesion/specs/ide/spec.md

Qué revisar:
- Checkout del candidato 677f045 (sólo lectura): /home/workstation/Dev/factory-sesion/.factory/local/revisiones/677f045
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-sesion/.factory/cambios/20261020-141303-sesion/candidatos/677f045/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-sesion/.factory/local/revisores/677f045-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-sesion/.factory/local/revisores/677f045-agy-1/informe.json --paquete /home/workstation/Dev/factory-sesion/.factory/cambios/20261020-141303-sesion/candidatos/677f045/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-sesion/.factory/local/revisiones/677f045
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio: editores/vscode/liveshare.js (rolDe, enlaceDeLiveShare, instalar, compartir, enlaceDeLaSesion, terminar, unirse, estado con enlace, diagnostico), editores/vscode/extension.js (el mensaje sesion con instalar, compartir, terminar, copiar y unirse; pintarTablero con el número de pintura y la sesión leída después de los datos; el canal Output → Oracle Factory), editores/vscode/tablero.js (los botones de la sesión y el enlace), package.json 0.3.1, README; tests/test_sesion.py, tests/sesion_en_node.cjs, tools/verify_sesion.py y catalogos/factory_sesion.*.oracle, contra el requisito de la spec. Mirá especialmente: que nunca se llame a share() con una sesión abierta (en VS Code real eso intenta abrir otra y deja la actual a medias), que unirse sólo acepte enlaces https de Live Share, inyección en el panel por el enlace, que ningún botón toque registros de Factory, y que el diagnóstico no anote nombres. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-sesion/.venv/bin/python -m unittest tests.test_sesion tests.test_liveshare </dev/null . Necesita node; si node no arranca, marcá esas pruebas como no ejecutadas y revisá el código. No corras la suite completa. Nombrá archivos con rutas relativas.
