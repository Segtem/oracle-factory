Sos un revisor independiente del cambio 20261103-113909-oen-contratojson de un proyecto que usa Oracle Factory: «Pruebas de contrato entre la CLI y la extensión de VS Code». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-contrato-json/openspec/changes/20261103-113909-oen-contratojson/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-contrato-json/openspec/changes/20261103-113909-oen-contratojson/specs/ide/spec.md

Qué revisar:
- Checkout del candidato eea6c47 (sólo lectura): /home/workstation/Dev/factory-contrato-json/.factory/local/revisiones/eea6c47-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-contrato-json/.factory/cambios/20261103-113909-oen-contratojson/candidatos/eea6c47/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261103-113909-oen-contratojson.md, kb/requisitos/ide_cc0ded3b7b46b23f7.el_documento_explica_como_actualizar_el_contrato.md, kb/requisitos/ide_cc0ded3b7b46b23f7.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido.md, kb/requisitos/ide_cc0ded3b7b46b23f7.la_extension_solo_lee_de_los_json_de_la_cli_lo_que_el_contrato_declara.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-contrato-json/.factory/local/revisores/eea6c47-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-contrato-json/.factory/local/revisores/eea6c47-codex-1/informe.json --paquete /home/workstation/Dev/factory-contrato-json/.factory/cambios/20261103-113909-oen-contratojson/candidatos/eea6c47/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-contrato-json/.factory/local/revisiones/eea6c47-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio contrato-json: editores/vscode/contrato.json (qué claves de los JSON de la CLI lee la extensión de VS Code, con sus tipos), tools/contrato_vscode.py (comprobar_la_cli, comprobar_la_extension, muestras, _pasos, tipo_de), tests/contrato_en_node.cjs (el registrador de lecturas con Proxy), tests/test_contrato_vscode.py, el párrafo nuevo de docs/tablero.md y los catálogos. La evidencia de ESTE cambio la produjo tools/verificar_cambio.py. Es un contrato en las dos direcciones: lo que la extensión LEE tiene que estar declarado, y lo declarado tiene que ENTREGARlo la CLI con un tipo permitido; las claves de más en la CLI no fallan. Buscá errores reales y de impacto práctico: lecturas que el Proxy no ve (spread, Object.keys/entries, desestructuración, `in`, JSON.stringify, métodos de arreglos, getters), falsos verdes (claves que se leen sólo en estados que las pruebas no ejercen), rutas con puntos o corchetes en los nombres de las claves, el manejo de `null` y de padres ausentes, tipos mal declarados (en tablero.cambios[].linea_de_tiempo[].detalle.* los tipos null/string/number los amplié a mano: decí si son los correctos mirando oracle_factory/), el recorrido de objetos con nombres variables (.*), y divergencias entre el documento y el código. Marcá los exóticos. Clasificá por severidad.
