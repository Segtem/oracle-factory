Sos un revisor independiente del cambio 20261013-011811-abandonar de un proyecto que usa Oracle Factory: «Abandonar un cambio con motivo, decidido por una persona». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-abandonar/openspec/changes/20261013-011811-abandonar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-abandonar/openspec/changes/20261013-011811-abandonar/specs/archivo/spec.md

Qué revisar:
- Checkout del candidato 05c64dc (sólo lectura): /home/workstation/Dev/factory-abandonar/.factory/local/revisiones/05c64dc
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-abandonar/.factory/cambios/20261013-011811-abandonar/candidatos/05c64dc/clue/paquete-agy-1.json


Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-abandonar/.factory/local/revisores/05c64dc-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-abandonar/.factory/local/revisores/05c64dc-agy-1/informe.json --paquete /home/workstation/Dev/factory-abandonar/.factory/cambios/20261013-011811-abandonar/candidatos/05c64dc/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-abandonar/.factory/local/revisiones/05c64dc
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: timeout 200 /home/workstation/Dev/factory-abandonar/.venv/bin/python -m unittest tests.test_abandonar tests.test_archivo tests.test_resumen </dev/null (el checkout no tiene .venv; ese intérprete tiene las dependencias). No corras tools/verify_*.py ni la suite entera. En los límites, escribí rutas relativas al repositorio. Foco: que abandonar sea siempre de una persona (también en modo autónomo), que no quede un estado a medias si falla el tracker o se corta, que ningún comando que modifica un cambio acepte uno abandonado, el registro mínimo de una carpeta sin registro en los comandos de lectura (estado, donde, buscar, listar, resumen) y si las pruebas cubren los escenarios de la spec.
