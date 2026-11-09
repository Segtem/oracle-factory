Sos un revisor independiente del cambio 20261109-212224-xo0-registros-raiz de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 1: dos raíces (producto y registros)». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-registros-raiz/openspec/changes/20261109-212224-xo0-registros-raiz/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-registros-raiz/openspec/changes/20261109-212224-xo0-registros-raiz/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 19e963a (sólo lectura): /home/workstation/Dev/factory-registros-raiz/.factory/local/revisiones/19e963a-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-registros-raiz/.factory/cambios/20261109-212224-xo0-registros-raiz/candidatos/19e963a/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261109-212224-xo0-registros-raiz/candidatos/0e53f84/revision/codex-1.json
- .factory/cambios/20261109-212224-xo0-registros-raiz/candidatos/1e242b2/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-212224-xo0-registros-raiz.md, kb/requisitos/flujo_ce4aba0f609f14b30.con_registros_aparte_el_repo_del_producto_queda_limpio.md, kb/requisitos/flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno.md, kb/requisitos/flujo_ce4aba0f609f14b30.sin_registros_aparte_nada_cambia.md, tareas): 23 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-registros-raiz/.factory/local/revisores/19e963a-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-registros-raiz/.factory/local/revisores/19e963a-codex-1/informe.json --paquete /home/workstation/Dev/factory-registros-raiz/.factory/cambios/20261109-212224-xo0-registros-raiz/candidatos/19e963a/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-registros-raiz/.factory/local/revisiones/19e963a-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá registros-raiz (ronda 3). Rondas previas: RRAIZ-1 (almacén dentro del producto o al revés) corregido con un rechazo en main (is_relative_to); RRAIZ-2 (un enlace simbólico dentro del almacén haría escribir en el producto) NO se reproduce: ruta_segura de inicializar y la validación de .factory ya lo bloquean; lo comprobé con enlaces en catalogos, requisitos, macros, corpus, diferencial, relaciones, oracle.json, tareas, openspec, .factory, .gitignore y kb, antes y después de init, y el producto nunca cambió; agregué pruebas que lo fijan en tests/test_registros_raiz.py (rr2). Si RRAIZ-2 te sigue pareciendo válido, dame un caso concreto que reproduzca la escritura en el producto. Etapa 1 de 6: PRODUCTO sólo se usa en argumentos_de_raiz; git sigue con cwd=ROOT (el almacén); los comandos con candidato se rechazan. Buscá lo que quede, pero con un caso que reproduzca.
