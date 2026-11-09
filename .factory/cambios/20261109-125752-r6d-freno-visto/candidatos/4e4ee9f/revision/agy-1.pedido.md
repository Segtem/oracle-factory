Sos un revisor independiente del cambio 20261109-125752-r6d-freno-visto de un proyecto que usa Oracle Factory: «Frenos: el de pruebas editadas deja de frenar cuando una persona aprobó la revisión». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-freno-declarado/openspec/changes/20261109-125752-r6d-freno-visto/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-freno-declarado/openspec/changes/20261109-125752-r6d-freno-visto/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 4e4ee9f (sólo lectura): /home/workstation/Dev/factory-freno-declarado/.factory/local/revisiones/4e4ee9f-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-freno-declarado/.factory/cambios/20261109-125752-r6d-freno-visto/candidatos/4e4ee9f/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-125752-r6d-freno-visto.md, kb/requisitos/flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada.md, tareas): 9 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-freno-declarado/.factory/local/revisores/4e4ee9f-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Si el paquete omite un archivo porque no es texto (una imagen, por ejemplo), abrilo vos en el checkout y declaralo con una línea de
limitations por archivo, exactamente `abierto: RUTA` (la ruta tal como figura en el paquete). Clue te obliga a marcar review_status
"incompleto" por esa omisión; Factory la acepta sólo si cada binario omitido está declarado así. No declares uno que no abriste.
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-freno-declarado/.factory/local/revisores/4e4ee9f-agy-1/informe.json --paquete /home/workstation/Dev/factory-freno-declarado/.factory/cambios/20261109-125752-r6d-freno-visto/candidatos/4e4ee9f/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-freno-declarado/.factory/local/revisiones/4e4ee9f-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá el cambio freno-visto: en oracle_factory/frenos.py el freno prueba_existente_editada deja de declararse cuando hay una revisión aprobada y vigente (revision_aprobada, calculada en lecturas.frenos_del_cambio). Buscá: casos en que el freno se levante sin que una persona haya mirado, o que siga frenando con revisión vigente; el efecto sobre autopilot.decidir y conductor; y huecos en tests/test_freno_visto.py. Declaramos que se editaron dos tests existentes? No: este cambio no edita tests existentes.
