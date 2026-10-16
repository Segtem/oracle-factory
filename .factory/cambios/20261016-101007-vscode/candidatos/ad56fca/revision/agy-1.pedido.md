Sos un revisor independiente del cambio 20261016-101007-vscode de un proyecto que usa Oracle Factory: «Extensión de VS Code: la vista de Factory, sus artefactos y el próximo paso». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-vscode/openspec/changes/20261016-101007-vscode/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-vscode/openspec/changes/20261016-101007-vscode/specs/ide/spec.md

Qué revisar:
- Checkout del candidato ad56fca (sólo lectura): /home/workstation/Dev/factory-vscode/.factory/local/revisiones/ad56fca
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-vscode/.factory/cambios/20261016-101007-vscode/candidatos/ad56fca/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-vscode/.factory/local/revisores/ad56fca-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-vscode/.factory/local/revisores/ad56fca-agy-1/informe.json --paquete /home/workstation/Dev/factory-vscode/.factory/cambios/20261016-101007-vscode/candidatos/ad56fca/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-vscode/.factory/local/revisiones/ad56fca
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá la extensión de VS Code (editores/vscode/package.json, extension.js, modelo.js, empaquetar.py) contra los 3 requisitos de la spec, y si tests/test_vscode.py con tests/vscode_en_node.cjs prueba de verdad cada escenario; revisá también tools/verify_vscode.py y catalogos/factory_vscode.*.oracle. Mirá especialmente: que la extensión no pueda ejecutar ni registrar una decisión (sendText sin Enter, nada que corra comandos de decisión), que un proyecto no pueda hacer correr un ejecutable ajeno por configuración, cómo se cita la CLI en la terminal, artefactos ausentes o no válidos que se ofrezcan abrir, errores de la CLI que dejen la vista vacía, y si el doble de vscode esconde algo que la API real haría distinto. Para correr las pruebas usá exactamente, en primer plano: .venv/bin/python -m unittest tests.test_vscode </dev/null . No corras la suite completa ni abras VS Code. Nombrá archivos con rutas relativas.
