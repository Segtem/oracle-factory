Sos un revisor independiente del cambio 20261013-153440-cli-json de un proyecto que usa Oracle Factory: «Salidas en JSON de estado, donde y resumen». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-cli-json/openspec/changes/20261013-153440-cli-json/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-cli-json/openspec/changes/20261013-153440-cli-json/specs/cli/spec.md

Qué revisar:
- Checkout del candidato 7b12c87 (sólo lectura): /home/workstation/Dev/factory-cli-json/.factory/local/revisiones/7b12c87
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-cli-json/.factory/cambios/20261013-153440-cli-json/candidatos/7b12c87/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261013-153440-cli-json/candidatos/48ccf54/revision/agy-1.json
- .factory/cambios/20261013-153440-cli-json/candidatos/48ccf54/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-cli-json/.factory/local/revisores/7b12c87-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-cli-json/.factory/local/revisores/7b12c87-codex-1/informe.json --paquete /home/workstation/Dev/factory-cli-json/.factory/cambios/20261013-153440-cli-json/candidatos/7b12c87/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-cli-json/.factory/local/revisiones/7b12c87
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. La vuelta 1 dejó CLIJSON-001 (codex: vigencia del juicio), CLI-JSON-002/003 (pruebas de oracle y del resumen) y CLI-JSON-004 (actor de registros viejos); el candidato los corrige. CLI-JSON-001 de agy (un cambio sin evidencia no la lista como ausente en donde; cumplirlo cambiaría el texto de donde, que otro requisito prohíbe) lo decide la persona en revisar: no lo reportes otra vez. Revisá la implementación (oracle_factory/cli.py: imprimir_json, _decision, datos_estado, datos_donde, insumos_resumen y las ramas --json de main; oracle_factory/resumen.py: datos) contra los 3 requisitos de la spec, y si tests/test_cli_json.py prueba de verdad cada escenario. Mirá especialmente: que --json nunca pregunte, escriba ni deje stdout a medias; que la vigencia de revisión y juicio coincida con la que usa estado en texto; que el texto sin --json no cambie (tests/datos/cli_texto/ se generó con main antes del cambio); y si el esquema es estable para un cliente (IDE, panel, MCP). Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-cli-json && /home/workstation/Dev/factory-cli-json/.venv/bin/python -m unittest tests.test_cli_json tests.test_resumen tests.test_estructura </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
