Sos un revisor independiente del cambio 20261021-140625-unir de un proyecto que usa Oracle Factory: «Unir registros: el de un cambio editado en dos ramas se une sin perder nada, y lo generado se rehace». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-unir/openspec/changes/20261021-140625-unir/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-unir/openspec/changes/20261021-140625-unir/specs/colaboracion/spec.md

Qué revisar:
- Checkout del candidato a192c6b (sólo lectura): /home/workstation/Dev/factory-unir/.factory/local/revisiones/a192c6b-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-unir/.factory/cambios/20261021-140625-unir/candidatos/a192c6b/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261021-140625-unir.md, kb/requisitos/colaboracion_cf525024cf654a9ec.el_registro_de_un_cambio_editado_en_dos_ramas_se_une_sin_perder_nada.md, kb/requisitos/colaboracion_cf525024cf654a9ec.lo_generado_no_choca_al_integrar.md, kb/requisitos/colaboracion_cf525024cf654a9ec.si_las_dos_ramas_decidieron_distinto_decide_una_persona.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-unir/.factory/local/revisores/a192c6b-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-unir/.factory/local/revisores/a192c6b-agy-1/informe.json --paquete /home/workstation/Dev/factory-unir/.factory/cambios/20261021-140625-unir/candidatos/a192c6b/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-unir/.factory/local/revisiones/a192c6b-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio: oracle_factory/unir.py (la unión pura de tres registros), en oracle_factory/cli.py instalar_union, unir_registro, rehacer_generado, aviso_union, el limpiado de pendientes_de_union en evento y los subcomandos unir-registro, unir-generado y rehacer-generado; tests/test_unir.py, tools/verify_unir.py, catalogos/factory_unir.*.oracle y el README, contra los 3 requisitos de la spec. Mirá especialmente: eventos o decisiones que se pierdan o dupliquen al unir, valores que Factory elija en silencio cuando las dos ramas decidieron distinto, el post-merge (MERGE_HEAD, merges con conflicto, ramas que no son main, un hook ajeno), .gitattributes repetido o pisado, y lo generado que quede viejo o sin commitear. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-unir/.venv/bin/python -m unittest tests.test_unir </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
