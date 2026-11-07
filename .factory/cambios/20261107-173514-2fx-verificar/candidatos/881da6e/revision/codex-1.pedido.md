Sos un revisor independiente del cambio 20261107-173514-2fx-verificar de un proyecto que usa Oracle Factory: «Sumar verificar a la puerta local de salida». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-puerta-verificar/openspec/changes/20261107-173514-2fx-verificar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-puerta-verificar/openspec/changes/20261107-173514-2fx-verificar/specs/puerta/spec.md

Qué revisar:
- Checkout del candidato 881da6e (sólo lectura): /home/workstation/Dev/factory-puerta-verificar/.factory/local/revisiones/881da6e-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-puerta-verificar/.factory/cambios/20261107-173514-2fx-verificar/candidatos/881da6e/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_puerta.py, modificado: 7 línea(s) quitada(s); 7 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261107-173514-2fx-verificar.md, kb/requisitos/puerta_c9332ef39d32011d7.la_guia_y_el_hook_cuentan_la_politica_real.md, kb/requisitos/puerta_c9332ef39d32011d7.la_puerta_corre_verificar_y_lo_nombra.md, kb/requisitos/puerta_c9332ef39d32011d7.sin_registro_de_factory_verificar_se_omite.md, kb/requisitos/puerta_c9332ef39d32011d7.verificar_en_la_puerta_avisa_y_no_bloquea.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-puerta-verificar/.factory/local/revisores/881da6e-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Si el paquete omite un archivo porque no es texto (una imagen, por ejemplo), abrilo vos en el checkout y declaralo con una línea de
limitations por archivo, exactamente `abierto: RUTA` (la ruta tal como figura en el paquete). Clue te obliga a marcar review_status
"incompleto" por esa omisión; Factory la acepta sólo si cada binario omitido está declarado así. No declares uno que no abriste.
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-puerta-verificar/.factory/local/revisores/881da6e-codex-1/informe.json --paquete /home/workstation/Dev/factory-puerta-verificar/.factory/cambios/20261107-173514-2fx-verificar/candidatos/881da6e/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-puerta-verificar/.factory/local/revisiones/881da6e-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá que la puerta local corra verificar (oracle_factory/puerta.py), avise sin bloquear, se omita sin .factory/config.json y que docs/puerta.md y el mensaje del hook (cli.py instalar_pre_push) cuenten la política real. Las ediciones a tests/test_puerta.py son adaptaciones por la nueva verificación. Mutaciones propias ya probadas: bloquear=True, SIN_FLAG vacío, sin pista, otro archivo, verificación ausente.
