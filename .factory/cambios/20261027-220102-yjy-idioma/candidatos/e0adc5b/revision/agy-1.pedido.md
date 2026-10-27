Sos un revisor independiente del cambio 20261027-220102-yjy-idioma de un proyecto que usa Oracle Factory: «Elegir el idioma de la propuesta y la spec de un cambio nuevo». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-idioma/openspec/changes/20261027-220102-yjy-idioma/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-idioma/openspec/changes/20261027-220102-yjy-idioma/specs/plantillas/spec.md

Qué revisar:
- Checkout del candidato e0adc5b (sólo lectura): /home/workstation/Dev/factory-idioma/.factory/local/revisiones/e0adc5b-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-idioma/.factory/cambios/20261027-220102-yjy-idioma/candidatos/e0adc5b/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261027-220102-yjy-idioma.md, kb/requisitos/plantillas_c553eae730b044e20.idioma_de_la_plantilla.md, kb/requisitos/plantillas_c553eae730b044e20.idioma_no_admitido.md, kb/requisitos/plantillas_c553eae730b044e20.la_plantilla_en_cualquier_idioma_se_aprueba_e_importa.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-idioma/.factory/local/revisores/e0adc5b-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-idioma/.factory/local/revisores/e0adc5b-agy-1/informe.json --paquete /home/workstation/Dev/factory-idioma/.factory/cambios/20261027-220102-yjy-idioma/candidatos/e0adc5b/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-idioma/.factory/local/revisiones/e0adc5b-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261027-220102-yjy-idioma/specs/plantillas/spec.md): oracle_factory/plantillas.py, en oracle_factory/cli.py las funciones config_proyecto y nuevo (y el argumento --idioma), tests/test_idioma.py, el ajuste en tests/test_cli_piloto.py, tools/verify_idioma.py, catalogos/factory_idioma.*.oracle y el párrafo nuevo de docs/estructura.md. Mirá especialmente: que ninguna plantilla mezcle idiomas, que lo que exige el formato (Capability, ADDED Requirements, Requirement, Scenario, Tipo y la marca de pendiente) esté en las dos, que un idioma inválido se rechace en la configuración y en --idioma sin crear nada (incluidos vacío, mayúsculas y tipos raros), que el ejemplo notas y los cambios ya creados no cambien, que otros lugares que leen config.json o la plantilla (init, migrar, agentes, kb, tablero, MCP, generacion.py) no se rompan, y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_idioma tests.test_cli_piloto </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
