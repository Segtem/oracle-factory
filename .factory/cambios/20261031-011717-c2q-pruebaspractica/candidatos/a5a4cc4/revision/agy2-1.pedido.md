Sos un revisor independiente del cambio 20261031-011717-c2q-pruebaspractica de un proyecto que usa Oracle Factory: «Pedir las pruebas como práctica de desarrollo, sin bloquear». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-pruebas-practica/openspec/changes/20261031-011717-c2q-pruebaspractica/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-pruebas-practica/openspec/changes/20261031-011717-c2q-pruebaspractica/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato a5a4cc4 (sólo lectura): /home/workstation/Dev/factory-pruebas-practica/.factory/local/revisiones/a5a4cc4-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-pruebas-practica/.factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/a5a4cc4/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/b160cda/revision/agy-1.json
- .factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/b160cda/revision/agy2-1.json
- .factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/8104329/revision/agy-1.json
- .factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/8104329/revision/agy2-1.json
- .factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/8d1350a/revision/agy-1.json
- .factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/8d1350a/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261031-011717-c2q-pruebaspractica.md, kb/requisitos/practicas_c185a6b4ec26306ce.el_estado_avisa_de_los_requisitos_sin_pruebas_sin_bloquear.md, kb/requisitos/practicas_c185a6b4ec26306ce.la_plantilla_de_tareas_pide_escribir_primero_las_pruebas.md, kb/requisitos/practicas_c185a6b4ec26306ce.una_excepcion_declarada_en_la_spec_explica_por_que_no_hay_pruebas.md, tareas): 31 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-pruebas-practica/.factory/local/revisores/a5a4cc4-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-4-argon-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-pruebas-practica/.factory/local/revisores/a5a4cc4-agy2-1/informe.json --paquete /home/workstation/Dev/factory-pruebas-practica/.factory/cambios/20261031-011717-c2q-pruebaspractica/candidatos/a5a4cc4/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-pruebas-practica/.factory/local/revisiones/a5a4cc4-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Cuarta ronda del cambio pruebas-practica (oracle_factory/pruebas.py, cli.py, lecturas.py, plantillas.py, tests/test_pruebas_practica.py, tools/verify_pruebas_practica.py, docs/trazabilidad.md). La tercera ronda dejó, ya corregido: la cabecera del requisito se cierra como en el importador de Oracle (#, ##, ### con espacio, o #### Scenario:); la vigencia de la aprobación compara las huellas de propuesta y spec (cli.documentos) como exigir_spec; spec_aprobada rara no rompe el estado; el motivo conserva guiones iniciales legítimos; se valida el identificador y el candidato antes de armar rutas; las excepciones aprobadas se ven antes de importar; el verificador exige que los casos trazados pasen y no cuenta la carpeta de evidencia. Verificá esos arreglos y buscá errores nuevos reales; clasificá por severidad.
