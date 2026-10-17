Sos un revisor independiente del cambio 20261017-023151-hechos-varios de un proyecto que usa Oracle Factory: «Juzgar un candidato con hechos de varios sensores». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-hechos-varios/openspec/changes/20261017-023151-hechos-varios/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-hechos-varios/openspec/changes/20261017-023151-hechos-varios/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato db4acc9 (sólo lectura): /home/workstation/Dev/factory-hechos-varios/.factory/local/revisiones/db4acc9
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-hechos-varios/.factory/cambios/20261017-023151-hechos-varios/candidatos/db4acc9/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261017-023151-hechos-varios/candidatos/18aca3d/revision/agy-1.json
- .factory/cambios/20261017-023151-hechos-varios/candidatos/18aca3d/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-hechos-varios/.factory/local/revisores/db4acc9-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-hechos-varios/.factory/local/revisores/db4acc9-codex-1/informe.json --paquete /home/workstation/Dev/factory-hechos-varios/.factory/cambios/20261017-023151-hechos-varios/candidatos/db4acc9/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-hechos-varios/.factory/local/revisiones/db4acc9
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la 1 codex no encontró nada y agy marcó HV-01 y HV-02 (altas: un hecho que falta llevaba a recuperar desde Git sin repetir el juicio; uno que no es ruta salía como --con 5), HV-03, HV-04, HV-06 (medias: el pendiente no nombraba al sensor inválido, un Oracle con 0 sin filas registraba veredicto, faltaba un rojo de verdad) y bajas. Corregido: comando_juzgar deja RUTA_DE_LOS_HECHOS para lo que no es ruta; el pendiente nombra «hechos del sensor i de n» y un null en la lista es inválido; sin filas de requisito no hay veredicto con cualquier código; prueba del rojo. HV-01 se resolvió así: un hecho que falta se sigue recuperando desde Git (decisión anterior de cli-piloto, test_c4 de tests/test_cli_humana.py: juzgar con un archivo que falta fallaría), y el paso ahora dice «después: oracle-factory juzgar ID --con … --con …» con todos. Verificá que las correcciones sean de verdad y buscá lo que siga. Revisá el cambio en oracle_factory/cli.py (juzgar con una lista de hechos, hechos_registrados y sus usos en juicio_vigente, pendientes_actuales, archivos_faltantes, _pasos y datos_estado, el --con con action=append de la CLI y la detección de «Oracle no juzgó» por falta de filas de requisito), oracle_factory/estructura.py (donde con hechos_mas), la subida a oracle-metalenguaje 0.39.0 en pyproject.toml y tools/verify_collaboration.py, el párrafo nuevo de docs/colaboracion.md, tests/test_hechos_varios.py, tools/verify_hechos_varios.py y catalogos/factory_hechos.*.oracle, contra los 2 requisitos de la spec. Mirá especialmente: registros viejos con un solo archivo que cambien de significado, un archivo de los demás que cambie, falte o no sea una ruta sin que se note, rutas con espacios en el próximo paso, que la detección de «Oracle no juzgó» no tape un rojo de verdad ni deje pasar un juicio vacío, y si las pruebas prueban cada escenario. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-hechos-varios/.venv/bin/python -m unittest tests.test_hechos_varios </dev/null (ese intérprete tiene Oracle 0.39.0; PYTHONPATH=. prueba el código del checkout). No corras la suite completa. Nombrá archivos con rutas relativas.
