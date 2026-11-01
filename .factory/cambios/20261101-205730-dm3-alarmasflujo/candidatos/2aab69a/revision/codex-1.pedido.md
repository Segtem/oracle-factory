Sos un revisor independiente del cambio 20261101-205730-dm3-alarmasflujo de un proyecto que usa Oracle Factory: «Avisar de los bucles de revisión y de los cambios demasiado grandes». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-alarmas-flujo/openspec/changes/20261101-205730-dm3-alarmasflujo/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-alarmas-flujo/openspec/changes/20261101-205730-dm3-alarmasflujo/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 2aab69a (sólo lectura): /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisiones/2aab69a-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-alarmas-flujo/.factory/cambios/20261101-205730-dm3-alarmasflujo/candidatos/2aab69a/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261101-205730-dm3-alarmasflujo/candidatos/9edd02d/revision/agy2-flash-1.json
- .factory/cambios/20261101-205730-dm3-alarmasflujo/candidatos/9edd02d/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_tests_editados.py, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261101-205730-dm3-alarmasflujo.md, kb/requisitos/practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado.md, kb/requisitos/practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto.md, kb/requisitos/practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisores/2aab69a-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisores/2aab69a-codex-1/informe.json --paquete /home/workstation/Dev/factory-alarmas-flujo/.factory/cambios/20261101-205730-dm3-alarmasflujo/candidatos/2aab69a/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisiones/2aab69a-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la segunda ronda de alarmas-flujo. La primera trajo 8 hallazgos: base fija «main» (ahora main o master, con base_del_candidato, también para tests editados), salidas de numstat rotas o truncadas, nombres de archivo no UTF-8 que rompían la decodificación (ahora _git devuelve None), SHA de distinto largo contados como rondas distintas, eventos raros (rondas devuelve None si algo no es un evento), cambios abandonados con las claves del flujo en null, una prueba del renombre que no distinguía origen de destino, y el sys.path de la prueba del contrato. Verificá que cada arreglo cubre la CLASE entera y buscá errores reales nuevos en oracle_factory/alarmas.py, lecturas.py, cli.py (mostrar), docs/tests.md, tools/verify_alarmas_flujo.py y tests/test_alarmas_flujo.py. Tests existentes que el candidato modificó: tests/test_tests_editados.py::test_te1_sin_candidato_o_sin_base_no_se_calcula_y_no_se_llama_a_git_de_mas pasó de esperar 1 llamada a 2 (el merge-base ahora prueba main y master); decí si te parece justificado. Son avisos: no deben bloquear ni cambiar pendientes ni próximo paso, y un fallo de Git o un registro raro no debe romper el estado. Clasificá por severidad.
