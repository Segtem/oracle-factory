Sos un revisor independiente del cambio 20261102-000745-j7r-verificadorgenerico de un proyecto que usa Oracle Factory: «Un verificador reutilizable para la evidencia de cada cambio». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-verificador-generico/openspec/changes/20261102-000745-j7r-verificadorgenerico/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-verificador-generico/openspec/changes/20261102-000745-j7r-verificadorgenerico/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 1b54f3f (sólo lectura): /home/workstation/Dev/factory-verificador-generico/.factory/local/revisiones/1b54f3f-agy2-flash-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-verificador-generico/.factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/1b54f3f/clue/paquete-agy2-flash-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261102-000745-j7r-verificadorgenerico.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_escribe_los_catalogos_del_cambio.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_produce_la_evidencia_completa_del_cambio.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-verificador-generico/.factory/local/revisores/1b54f3f-agy2-flash-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-verificador-generico/.factory/local/revisores/1b54f3f-agy2-flash-1/informe.json --paquete /home/workstation/Dev/factory-verificador-generico/.factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/1b54f3f/clue/paquete-agy2-flash-1.json --repo /home/workstation/Dev/factory-verificador-generico/.factory/local/revisiones/1b54f3f-agy2-flash-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio verificador-generico: tools/verificar_cambio.py (casos_del_modulo, requisitos_de_la_spec, contrato, leer_contrato, fuentes, producir, catálogos, main), tests/test_verificador_generico.py, docs/tests.md y los catálogos catalogos/factory_verificador_generico.*. La evidencia de ESTE cambio la produjo la propia herramienta (python tools/verificar_cambio.py ID --pruebas test_verificador_generico --salida …), no un verify_<x>.py a mano. Buscá errores reales: la convención test_<letras><n>_ y el orden de los requisitos (specs con varias capacidades, encabezados raros, requisitos repetidos), el contrato (falsos verdes: casos que no corren, duplicados, omitidos, skips), la estabilidad de las fuentes (qué cuenta como fuente, carpetas ignoradas, evidencia dentro del repositorio), el manejo de errores (registro o spec ilegibles, módulo con errores de sintaxis, tracebacks, carpeta a medias), la idempotencia de los catálogos (nombres con caracteres raros, comillas en el alcance), divergencias entre el documento y el código, y pruebas que pasan por construcción. Clasificá por severidad.
