Sos un revisor independiente del cambio 20261027-140946-d48-bloqueos de un proyecto que usa Oracle Factory: «Mostrar en el tablero qué falta en cada cambio y cómo se destraba». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tablero-bloqueos/openspec/changes/20261027-140946-d48-bloqueos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tablero-bloqueos/openspec/changes/20261027-140946-d48-bloqueos/specs/tablero/spec.md

Qué revisar:
- Checkout del candidato 959ab12 (sólo lectura): /home/workstation/Dev/factory-tablero-bloqueos/.factory/local/revisiones/959ab12-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tablero-bloqueos/.factory/cambios/20261027-140946-d48-bloqueos/candidatos/959ab12/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261027-140946-d48-bloqueos/candidatos/03f59a2/revision/agy-1.json
- .factory/cambios/20261027-140946-d48-bloqueos/candidatos/03f59a2/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261027-140946-d48-bloqueos.md, kb/requisitos/tablero_cae12f0cad890a9c2.el_texto_del_registro_se_escapa.md, kb/requisitos/tablero_cae12f0cad890a9c2.instruccion_distinta_de_comando.md, kb/requisitos/tablero_cae12f0cad890a9c2.que_falta_en_cada_cambio.md, tareas): 16 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tablero-bloqueos/.factory/local/revisores/959ab12-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tablero-bloqueos/.factory/local/revisores/959ab12-agy2-1/informe.json --paquete /home/workstation/Dev/factory-tablero-bloqueos/.factory/cambios/20261027-140946-d48-bloqueos/candidatos/959ab12/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-tablero-bloqueos/.factory/local/revisiones/959ab12-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los hallazgos de la vuelta 1 (orden no alfabético, escapado de comandos y de data-comando, rótulo en alternativas, design.md). Revisá el cambio contra los requisitos de su spec (openspec/changes/20261027-140946-d48-bloqueos/specs/tablero/spec.md): editores/vscode/tablero.js (paso, faltante y cambio), tests/test_tablero_bloqueos.py, tools/verify_tablero_bloqueos.py y catalogos/factory_tablero_bloqueos.*.oracle. Mirá especialmente: que un comando de Factory siga con su botón y su rótulo, que una explicación no tenga botón ni formato de código, que ningún texto del registro entre sin escapar al HTML (pendientes, pasos, alternativas), que el árbol de modelo.js y otras pruebas del tablero no dependan del rótulo viejo, que la sección «Qué falta» no rompa el orden ni el estilo del panel y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_tablero_bloqueos tests.test_tablero </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
