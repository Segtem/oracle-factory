Sos un revisor independiente del cambio 20261028-100820-5n7-causa de un proyecto que usa Oracle Factory: «Que aprobar-spec diga qué línea de qué archivo falta completar». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-bloqueo-causa/openspec/changes/20261028-100820-5n7-causa/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-bloqueo-causa/openspec/changes/20261028-100820-5n7-causa/specs/bloqueos/spec.md

Qué revisar:
- Checkout del candidato e996c78 (sólo lectura): /home/workstation/Dev/factory-bloqueo-causa/.factory/local/revisiones/e996c78-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-bloqueo-causa/.factory/cambios/20261028-100820-5n7-causa/candidatos/e996c78/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261028-100820-5n7-causa/candidatos/5d08334/revision/agy-1.json
- .factory/cambios/20261028-100820-5n7-causa/candidatos/5d08334/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261028-100820-5n7-causa.md, kb/requisitos/bloqueos_c675508440ed3a2b8.aprobar_spec_no_cambia_cuando_todo_esta_completo.md, kb/requisitos/bloqueos_c675508440ed3a2b8.el_bloqueo_de_aprobar_spec_dice_si_falta_un_archivo.md, kb/requisitos/bloqueos_c675508440ed3a2b8.el_bloqueo_de_aprobar_spec_nombra_la_linea.md, tareas): 16 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-bloqueo-causa/.factory/local/revisores/e996c78-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-bloqueo-causa/.factory/local/revisores/e996c78-agy2-1/informe.json --paquete /home/workstation/Dev/factory-bloqueo-causa/.factory/cambios/20261028-100820-5n7-causa/candidatos/e996c78/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-bloqueo-causa/.factory/local/revisiones/e996c78-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los hallazgos de la vuelta 1 (enlaces simbólicos con ruta_segura, archivos no UTF-8, redacción en singular y plural, pruebas de la plantilla sin tocar y de varios archivos ausentes). Sobre el hallazgo de que la plantilla real no trae la marca en tasks.md: la spec describe un cambio con marcas en los tres archivos, y la prueba lo construye; la plantilla sin tocar tiene su propia prueba. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261028-100820-5n7-causa/specs/bloqueos/spec.md): en oracle_factory/cli.py las funciones exigir_plantilla_completa y aprobar_spec, tests/test_bloqueo_causa.py, tools/verify_bloqueo_causa.py y catalogos/factory_bloqueo_causa.*.oracle. Mirá especialmente: que el mensaje nombre bien línea, texto y cuántas marcas quedan por archivo, que el corte a 80 caracteres sea exacto, que un archivo ausente se diga como ausente (y no como pendiente), que el comienzo «hay que completar y revisar primero» se conserve para quien lo lea, que aprobar con todo completo no cambie, que no se lea fuera del proyecto (symlinks, rutas) ni se rompa con archivos no UTF-8, y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_bloqueo_causa tests.test_cli_piloto </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
