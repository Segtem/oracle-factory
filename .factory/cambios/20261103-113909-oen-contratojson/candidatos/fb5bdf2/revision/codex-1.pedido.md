Sos un revisor independiente del cambio 20261103-113909-oen-contratojson de un proyecto que usa Oracle Factory: «Pruebas de contrato entre la CLI y la extensión de VS Code». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-contrato-json/openspec/changes/20261103-113909-oen-contratojson/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-contrato-json/openspec/changes/20261103-113909-oen-contratojson/specs/ide/spec.md

Qué revisar:
- Checkout del candidato fb5bdf2 (sólo lectura): /home/workstation/Dev/factory-contrato-json/.factory/local/revisiones/fb5bdf2-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-contrato-json/.factory/cambios/20261103-113909-oen-contratojson/candidatos/fb5bdf2/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261103-113909-oen-contratojson/candidatos/eea6c47/revision/agy2-flash-1.json
- .factory/cambios/20261103-113909-oen-contratojson/candidatos/eea6c47/revision/codex-1.json
- .factory/cambios/20261103-113909-oen-contratojson/candidatos/58363a1/revision/agy2-flash-1.json
- .factory/cambios/20261103-113909-oen-contratojson/candidatos/58363a1/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261103-113909-oen-contratojson.md, kb/requisitos/ide_cc0ded3b7b46b23f7.el_documento_explica_como_actualizar_el_contrato.md, kb/requisitos/ide_cc0ded3b7b46b23f7.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido.md, kb/requisitos/ide_cc0ded3b7b46b23f7.la_extension_solo_lee_de_los_json_de_la_cli_lo_que_el_contrato_declara.md, tareas): 23 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-contrato-json/.factory/local/revisores/fb5bdf2-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-contrato-json/.factory/local/revisores/fb5bdf2-codex-1/informe.json --paquete /home/workstation/Dev/factory-contrato-json/.factory/cambios/20261103-113909-oen-contratojson/candidatos/fb5bdf2/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-contrato-json/.factory/local/revisiones/fb5bdf2-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la tercera ronda de contrato-json. La segunda trajo 10 hallazgos: la regex de la revisión estática no veía accesos encadenados (ahora lookbehind), la revisión estática mezclaba comandos (ahora cada archivo se compara sólo con el contrato de los JSON que lee: modelo.js con resumen/estado/donde y tablero.js con tablero), y faltaban claves y tipos del tablero (se completaron 14 entradas y se ensancharon 8 tipos con una «nota» sacada del código de la CLI; las claves que ningún estado ejerce son opcionales). Límite declarado en docs/tablero.md: la revisión estática es por nombre, no por ruta. Verificá que los arreglos cubren la CLASE y buscá errores reales y de impacto práctico, sobre todo: claves que oracle_factory/tablero.py, lecturas.py y cli.py producen y que modelo.js o tablero.js LEEN pero el contrato no declara con su ruta completa (revisá el código JS línea por línea, no sólo los nombres), y tipos mal declarados. Marcá los exóticos y decí si lo que queda es un límite razonable. Revisá editores/vscode/contrato.json, tools/contrato_vscode.py, tests/contrato_en_node.cjs, tests/test_contrato_vscode.py y docs/tablero.md. Clasificá por severidad.
