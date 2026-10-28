Sos un revisor independiente del cambio 20261028-102041-88p-entregaa15 de un proyecto que usa Oracle Factory: «Preparar la distribución 0.1.0a15». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-entrega-a15/openspec/changes/20261028-102041-88p-entregaa15/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-entrega-a15/openspec/changes/20261028-102041-88p-entregaa15/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 4f46d9a (sólo lectura): /home/workstation/Dev/factory-entrega-a15/.factory/local/revisiones/4f46d9a-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-entrega-a15/.factory/cambios/20261028-102041-88p-entregaa15/candidatos/4f46d9a/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261028-102041-88p-entregaa15.md, kb/requisitos/distribucion_c753ee76bc96b08b2.el_wheel_a15_instalado_ofrece_lo_nuevo.md, kb/requisitos/distribucion_c753ee76bc96b08b2.la_entrega_a15_registra_sus_pruebas_y_sus_limites.md, kb/requisitos/distribucion_c753ee76bc96b08b2.la_version_a15_es_coherente_y_declara_su_estado.md, tareas): 8 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-entrega-a15/.factory/local/revisores/4f46d9a-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-entrega-a15/.factory/local/revisores/4f46d9a-agy2-1/informe.json --paquete /home/workstation/Dev/factory-entrega-a15/.factory/cambios/20261028-102041-88p-entregaa15/candidatos/4f46d9a/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-entrega-a15/.factory/local/revisiones/4f46d9a-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261028-102041-88p-entregaa15/specs/distribucion/spec.md): la subida de versión a 0.1.0a15 (pyproject.toml, oracle_factory/__init__.py, README.md, NOTAS-DE-RELEASE.md, site/*.html, docs/colaboracion.md, tests/datos/guias-texto.json), tools/probar_entrega_a15.py (incluida validar_novedades), tools/verify_entrega_a15.py, tools/mutar_entrega_a15.py, tests/test_entrega_a15.py, tests/test_entrega_integridad_a15.py, tests/test_docs.py y catalogos/factory_entrega_a15.*.oracle. Mirá especialmente: que NINGÚN lugar siga nombrando 0.1.0a14 como la versión de esta entrega, que las notas no afirmen que 0.1.0a15 está publicada (aún no lo está) pero sí que 0.1.0a14 lo está, que las notas de 0.1.0a15 digan la verdad sobre lo que trae (cada afirmación contra el código), que el README y la web no prometan instalar algo que todavía no está en PyPI sin decirlo, que la comprobación del wheel instalado sea real (fuera del checkout, origen en site-packages) y que sus chequeos fallen de verdad si se rompe una novedad, y que las pruebas y mutaciones tengan respaldo. Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_entrega_a15 tests.test_entrega_integridad_a15 tests.test_docs </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
