Sos un revisor independiente del cambio 20261109-030359-8e4-revprop de un proyecto que usa Oracle Factory: «Autopilot: la propuesta de revisión es trabajo del agente, antes de pedírsela a la persona». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-autopilot-revision/openspec/changes/20261109-030359-8e4-revprop/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-autopilot-revision/openspec/changes/20261109-030359-8e4-revprop/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato ef342fd (sólo lectura): /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisiones/ef342fd-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-autopilot-revision/.factory/cambios/20261109-030359-8e4-revprop/candidatos/ef342fd/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261109-030359-8e4-revprop/candidatos/04048bb/revision/codex-1.json
- .factory/cambios/20261109-030359-8e4-revprop/candidatos/c16e67d/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_autopilot.py, modificado: 1 línea(s) quitada(s)
- tests/test_conductor.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-030359-8e4-revprop.md, kb/requisitos/flujo_c7819789b58cf6ed1.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision.md, kb/requisitos/flujo_c7819789b58cf6ed1.estado_dice_la_ultima_propuesta_de_revision_de_un_agente.md, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisores/ef342fd-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisores/ef342fd-codex-1/informe.json --paquete /home/workstation/Dev/factory-autopilot-revision/.factory/cambios/20261109-030359-8e4-revprop/candidatos/ef342fd/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisiones/ef342fd-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 3 del cambio revprop, candidato ef342fd. Spec: openspec/changes/20261109-030359-8e4-revprop/specs/flujo/spec.md. Rondas anteriores, las dos de la clase 'qué cuenta como propuesta válida': REVPROP-1 (ultima_propuesta aceptaba una propuesta de quien no era un agente; ahora exige tipo_actor == 'agente' exacto) y REVPROP-2 (el conductor aceptaba una propuesta incompleta o con candidato con basura; ahora, en autopilot._propuesta_del_candidato, cuenta sólo si trae decision en {aprobar, cambios}, candidato hexadecimal de 7 a 40 caracteres que coincide con el vigente en los 7 primeros, y actor y cuando como texto no vacío). Sigo DECLARANDO las dos pruebas existentes editadas, sólo sus ayudantes (el decidir() de tests/test_autopilot.py y el datos() de tests/test_conductor.py dejan por defecto una propuesta completa y válida del candidato vigente; ningún caso quitado ni aflojado; por eso estado marca el freno prueba_existente_editada). Mirá lo que quede de la clase 'propuesta válida' (otras formas de datos raros, orden respecto de una revisión ya registrada, el candidato vigente mismo con formato raro, una propuesta posterior a un cambio de candidato) y lo demás: que ante revisar la decisión nunca salga actuar ni se salte a la persona, la clave de estado aditiva y sin romper con registros ilegibles. Evidencia: 1336 pruebas OK; 35 mutaciones propias, todas detectadas.
