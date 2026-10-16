Sos un revisor independiente del cambio 20261016-114832-informe-no-texto de un proyecto que usa Oracle Factory: «Un valor del registro que no es una ruta se informa sin caerse». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-informe-no-texto/openspec/changes/20261016-114832-informe-no-texto/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-informe-no-texto/openspec/changes/20261016-114832-informe-no-texto/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 4ae7633 (sólo lectura): /home/workstation/Dev/factory-informe-no-texto/.factory/local/revisiones/4ae7633
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-informe-no-texto/.factory/cambios/20261016-114832-informe-no-texto/candidatos/4ae7633/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-informe-no-texto/.factory/local/revisores/4ae7633-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-informe-no-texto/.factory/local/revisores/4ae7633-agy-1/informe.json --paquete /home/workstation/Dev/factory-informe-no-texto/.factory/cambios/20261016-114832-informe-no-texto/candidatos/4ae7633/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-informe-no-texto/.factory/local/revisiones/4ae7633
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el arreglo en oracle_factory/cli.py (ruta_del_registro, NO_VALIDO y sus usos en juicio_vigente, problemas_de_revision, pendientes_actuales, archivos_faltantes y _pasos) contra el requisito de la spec, y si tests/test_informe_no_texto.py prueba de verdad los dos escenarios; revisá también tools/verify_informe_no_texto.py y catalogos/factory_informe.*.oracle. Mirá especialmente: otro lugar que todavía una un valor del registro con la raíz sin mirarlo (también en otros módulos de oracle_factory/), un valor no válido que haga pasar por vigente una revisión o un juicio, si el próximo paso puede quedar en un ciclo, y valores como cadena vacía o con bytes nulos. Para correr las pruebas usá exactamente, en primer plano: python3 -m unittest tests.test_informe_no_texto </dev/null (si falta oracle_factory en ese intérprete, decilo en los límites). No corras la suite completa. Nombrá archivos con rutas relativas.
