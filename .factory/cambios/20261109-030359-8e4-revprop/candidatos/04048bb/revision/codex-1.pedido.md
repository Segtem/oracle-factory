Sos un revisor independiente del cambio 20261109-030359-8e4-revprop de un proyecto que usa Oracle Factory: «Autopilot: la propuesta de revisión es trabajo del agente, antes de pedírsela a la persona». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-autopilot-revision/openspec/changes/20261109-030359-8e4-revprop/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-autopilot-revision/openspec/changes/20261109-030359-8e4-revprop/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 04048bb (sólo lectura): /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisiones/04048bb-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-autopilot-revision/.factory/cambios/20261109-030359-8e4-revprop/candidatos/04048bb/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_autopilot.py, modificado: 1 línea(s) quitada(s)
- tests/test_conductor.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-030359-8e4-revprop.md, kb/requisitos/flujo_c7819789b58cf6ed1.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision.md, kb/requisitos/flujo_c7819789b58cf6ed1.estado_dice_la_ultima_propuesta_de_revision_de_un_agente.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisores/04048bb-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisores/04048bb-codex-1/informe.json --paquete /home/workstation/Dev/factory-autopilot-revision/.factory/cambios/20261109-030359-8e4-revprop/candidatos/04048bb/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-autopilot-revision/.factory/local/revisiones/04048bb-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá el candidato 04048bb del cambio revprop (capacidad flujo, cambio 3c del autopilot). Spec: openspec/changes/20261109-030359-8e4-revprop/specs/flujo/spec.md. Producto: autopilot.ultima_propuesta y la regla de revisar en autopilot.decidir (oracle_factory/autopilot.py), la clave propuesta_de_revision en lecturas.datos_estado, y docs/modos.md. Pruebas nuevas: tests/test_revprop.py (rp1, rp2). DECLARO DOS PRUEBAS EXISTENTES EDITADAS (la guarda de docs/tests.md; por eso estado marca el freno prueba_existente_editada): sólo los ayudantes, de forma aditiva: el decidir() de tests/test_autopilot.py y el datos() de tests/test_conductor.py ganan la clave propuesta_de_revision con una propuesta del candidato vigente, porque ahora revisar sin propuesta pasa a delegar_al_agente y sin eso los casos que esperan pedir_a_persona dejarían de probar lo que decían. Ningún caso se quitó ni se aflojó. Mirá si la edición está justificada. Evidencia: 1336 pruebas OK; 22 mutaciones propias, todas detectadas. Mirá sobre todo: (1) que ante revisar la decisión nunca salga actuar ni se salte a la persona, y que con propuesta del candidato vigente siga siendo pedir_a_persona; (2) la comparación del candidato (7 caracteres, minúsculas, tipos raros); (3) que la clave de estado sea aditiva y no rompa con registros ilegibles; (4) falsos silencios: propuestas de otro candidato, de una persona (no de un agente), o anteriores a una revisión ya registrada.
