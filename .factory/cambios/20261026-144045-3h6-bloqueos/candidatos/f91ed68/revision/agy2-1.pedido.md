Sos un revisor independiente del cambio 20261026-144045-3h6-bloqueos de un proyecto que usa Oracle Factory: «Mostrar cada bloqueo con su solución». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-bloqueos/openspec/changes/20261026-144045-3h6-bloqueos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-bloqueos/openspec/changes/20261026-144045-3h6-bloqueos/specs/bloqueos/spec.md

Qué revisar:
- Checkout del candidato f91ed68 (sólo lectura): /home/workstation/Dev/factory-bloqueos/.factory/local/revisiones/f91ed68-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-bloqueos/.factory/cambios/20261026-144045-3h6-bloqueos/candidatos/f91ed68/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261026-144045-3h6-bloqueos/candidatos/7e993c7/revision/agy-1.json
- .factory/cambios/20261026-144045-3h6-bloqueos/candidatos/7e993c7/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261026-144045-3h6-bloqueos.md, kb/requisitos/bloqueos_c48b34e270263f8fb.el_paquete_vacio_nombra_la_salida.md, kb/requisitos/bloqueos_c48b34e270263f8fb.el_proximo_paso_sin_revisor_lo_explica.md, kb/requisitos/bloqueos_c48b34e270263f8fb.revisar_bloqueado_dice_como_seguir.md, kb/requisitos/bloqueos_c48b34e270263f8fb.revisar_el_producto_de_un_primer_commit.md, tareas): 16 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-bloqueos/.factory/local/revisores/f91ed68-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-bloqueos/.factory/local/revisores/f91ed68-agy2-1/informe.json --paquete /home/workstation/Dev/factory-bloqueos/.factory/cambios/20261026-144045-3h6-bloqueos/candidatos/f91ed68/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-bloqueos/.factory/local/revisiones/f91ed68-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigió que pedir-revision sin --base con diff vacío nombre --base vacio, que revisar distinga 'tiene evidencia pero falta el informe de un revisor' de 'no tiene nada', que los tres próximos pasos usen pedido_de_revision (con --a), y que base_vacia fije también nombre y correo de autor y committer ignorando el entorno. Verificá que esas correcciones valgan y buscá regresiones. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261026-144045-3h6-bloqueos/specs/bloqueos/spec.md): oracle_factory/cli.py (funciones pedido_de_revision, base_vacia, pedir_revision, _revisar_paso_a_paso, preparar_revision y _pasos), tests/test_bloqueos.py, los cuatro asserts actualizados en tests/test_cli_humana.py y tests/test_informe_no_texto.py, tools/verify_bloqueos.py y catalogos/factory_bloqueos.*.oracle. Mirá especialmente: que base_vacia no toque ramas, historia ni configuración de git (ni use una identidad global), que el comando sugerido nunca quede con un hueco, que --base vacio funcione con el clon local del revisor, y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-bloqueos/.venv/bin/python -m unittest tests.test_bloqueos </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
