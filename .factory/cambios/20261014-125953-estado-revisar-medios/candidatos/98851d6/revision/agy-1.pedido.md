Sos un revisor independiente del cambio 20261014-125953-estado-revisar-medios de un proyecto que usa Oracle Factory: «estado ofrece revisar cuando quedan hallazgos medios». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-estado-revisar-medios/openspec/changes/20261014-125953-estado-revisar-medios/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-estado-revisar-medios/openspec/changes/20261014-125953-estado-revisar-medios/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato 98851d6 (sólo lectura): /home/workstation/Dev/factory-estado-revisar-medios/.factory/local/revisiones/98851d6
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-estado-revisar-medios/.factory/cambios/20261014-125953-estado-revisar-medios/candidatos/98851d6/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-estado-revisar-medios/.factory/local/revisores/98851d6-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-estado-revisar-medios/.factory/local/revisores/98851d6-agy-1/informe.json --paquete /home/workstation/Dev/factory-estado-revisar-medios/.factory/cambios/20261014-125953-estado-revisar-medios/candidatos/98851d6/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-estado-revisar-medios/.factory/local/revisiones/98851d6
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá la implementación (oracle_factory/cli.py: pasos, _pasos y proximo_paso; ofrecer_siguiente; la impresión de alternativas en estado; datos_estado con alternativas; el aviso en pedir_revision) contra el requisito de la spec, y si tests/test_estado_alternativas.py prueba de verdad cada escenario. Mirá especialmente: que la alternativa aparezca sólo cuando quedan medios sin aceptar y con las mismas condiciones que el paso, que el menú ejecute lo elegido y Salir no ejecute nada, que proximo_paso y el JSON sigan iguales para quien ya los usaba, y que un comando con MAYÚSCULAS por completar no se ofrezca. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-estado-revisar-medios && /home/workstation/Dev/factory-estado-revisar-medios/.venv/bin/python -m unittest tests.test_estado_alternativas tests.test_vueltas tests.test_cli_humana tests.test_cli_json </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
