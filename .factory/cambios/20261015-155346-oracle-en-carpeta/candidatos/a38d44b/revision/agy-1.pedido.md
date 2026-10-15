Sos un revisor independiente del cambio 20261015-155346-oracle-en-carpeta de un proyecto que usa Oracle Factory: «El proyecto Oracle puede estar en una carpeta del proyecto». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-oracle-en-carpeta/openspec/changes/20261015-155346-oracle-en-carpeta/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-oracle-en-carpeta/openspec/changes/20261015-155346-oracle-en-carpeta/specs/estructura/spec.md

Qué revisar:
- Checkout del candidato a38d44b (sólo lectura): /home/workstation/Dev/factory-oracle-en-carpeta/.factory/local/revisiones/a38d44b
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-oracle-en-carpeta/.factory/cambios/20261015-155346-oracle-en-carpeta/candidatos/a38d44b/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261015-155346-oracle-en-carpeta/candidatos/af991ba/revision/agy-1.json
- .factory/cambios/20261015-155346-oracle-en-carpeta/candidatos/af991ba/revision/codex-1.json
- .factory/cambios/20261015-155346-oracle-en-carpeta/candidatos/75bbe8a/revision/agy-1.json
- .factory/cambios/20261015-155346-oracle-en-carpeta/candidatos/75bbe8a/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-oracle-en-carpeta/.factory/local/revisores/a38d44b-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-oracle-en-carpeta/.factory/local/revisores/a38d44b-agy-1/informe.json --paquete /home/workstation/Dev/factory-oracle-en-carpeta/.factory/cambios/20261015-155346-oracle-en-carpeta/candidatos/a38d44b/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-oracle-en-carpeta/.factory/local/revisiones/a38d44b
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3. La 2 (agy un alto y dos medios, codex un medio) quedó corregida: juzgar carga primero el catálogo y entrega el error de Oracle con escalares sin declarar (y el detalle de una cobertura que falla); la prueba sin declararlos afirma ese error, que no se corrió Oracle y que el juicio anterior no se toca, y con_escalares se prueba aparte; las rutas con barras invertidas o absolutas de Windows se rechazan. Revisá la implementación (oracle_factory/cli.py: config_proyecto, proyecto_oracle, oracle_rel, requisitos_dir, con_escalares, catalogo_del_proyecto, inventario_medidas, inicializar con --oracle, plan_ejemplo, comando_buscar y la validación al empezar main; oracle_factory/estructura.py: donde, buscar y _cambio_de) contra los 3 requisitos de la spec, y si tests/test_oracle_en_carpeta.py prueba de verdad cada escenario; revisá también tools/verify_oracle_en_carpeta.py, los catálogos factory_carpeta, docs/estructura.md y la subida a oracle-metalenguaje 0.38.2. Mirá especialmente: lugares que todavía suponen el proyecto Oracle en la raíz (requisitos, catálogos, oracle.json, --proyecto de Oracle), rutas que escapan del proyecto (enlaces, ..), init sobre un proyecto ya inicializado, y cuándo se ejecutan escalares del proyecto. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-oracle-en-carpeta && /home/workstation/Dev/factory-oracle-en-carpeta/.venv/bin/python -m unittest tests.test_oracle_en_carpeta tests.test_estructura </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
