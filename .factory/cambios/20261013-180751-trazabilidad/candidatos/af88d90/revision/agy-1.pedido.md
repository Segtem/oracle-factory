Sos un revisor independiente del cambio 20261013-180751-trazabilidad de un proyecto que usa Oracle Factory: «Trazabilidad por candidato: requisito, casos y líneas cambiadas». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-trazabilidad/openspec/changes/20261013-180751-trazabilidad/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-trazabilidad/openspec/changes/20261013-180751-trazabilidad/specs/trazabilidad/spec.md

Qué revisar:
- Checkout del candidato af88d90 (sólo lectura): /home/workstation/Dev/factory-trazabilidad/.factory/local/revisiones/af88d90
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-trazabilidad/.factory/cambios/20261013-180751-trazabilidad/candidatos/af88d90/clue/paquete-agy-1.json


Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-trazabilidad/.factory/local/revisores/af88d90-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-trazabilidad/.factory/local/revisores/af88d90-agy-1/informe.json --paquete /home/workstation/Dev/factory-trazabilidad/.factory/cambios/20261013-180751-trazabilidad/candidatos/af88d90/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-trazabilidad/.factory/local/revisiones/af88d90
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá la implementación (oracle_factory/trazabilidad.py entero; oracle_factory/cli.py: datos_trazabilidad, comando_trazabilidad, rangos y el subcomando; tools/verify_trazabilidad.py) contra los 3 requisitos de la spec, y si tests/test_trazabilidad.py prueba de verdad cada escenario. Mirá especialmente: líneas que se dan por respaldadas o sin respaldo cuando no lo son (lineas_ejecutables, la línea del def, el parseo de git diff -U0, renombres y archivos borrados), que trazar no deje una traza puesta ni rompa la de quien ya trazaba, y que los límites declarados sean ciertos. Podés ver la salida real con: cd /home/workstation/Dev/factory-trazabilidad && /home/workstation/Dev/factory-trazabilidad/.venv/bin/oracle-factory trazabilidad 20261013-180751-trazabilidad </dev/null . Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-trazabilidad && /home/workstation/Dev/factory-trazabilidad/.venv/bin/python -m unittest tests.test_trazabilidad tests.test_cli_json </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
