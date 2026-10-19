Sos un revisor independiente del cambio 20261017-135953-higiene de un proyecto que usa Oracle Factory: «Lo que la prueba del ajedrez dejó a la vista: revisores cortados, acciones sin autor y carpetas de más». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-higiene/openspec/changes/20261017-135953-higiene/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-higiene/openspec/changes/20261017-135953-higiene/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 823450c (sólo lectura): /home/workstation/Dev/factory-higiene/.factory/local/revisiones/823450c
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-higiene/.factory/cambios/20261017-135953-higiene/candidatos/823450c/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261017-135953-higiene/candidatos/a6cefc0/revision/agy-1.json
- .factory/cambios/20261017-135953-higiene/candidatos/a6cefc0/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-higiene/.factory/local/revisores/823450c-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-higiene/.factory/local/revisores/823450c-codex-1/informe.json --paquete /home/workstation/Dev/factory-higiene/.factory/cambios/20261017-135953-higiene/candidatos/823450c/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-higiene/.factory/local/revisiones/823450c
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la vuelta 1 se corrigieron HIG-1/HG-002 (cada revision_pedida cierra un solo lanzamiento), HG-001 (un lanzamiento nuevo del mismo revisor sobre otro candidato deja atrás los cortados del anterior) y HG-003 (el try de KeyboardInterrupt cubre también la validación con Clue); verificá esas correcciones y buscá lo que quede. Revisá el cambio en oracle_factory/cli.py (pedir_revision: el evento revision_lanzada antes del revisor y el KeyboardInterrupt que deja «interrumpido»; aviso_lanzamientos y aviso_sin_autor y sus usos en estado y datos_estado; inicializar: SIN_USO_DE_ORACLE y las carpetas vacías que quita; bloqueo_medidas en .factory/local/locks; el .gitignore de init sin .factory-demo/), la mudanza de la guía (site/desde-cero.html), los README de notas y el principal a .factory/local/, el texto congelado actualizado (tests/datos/guias-texto.json, sólo .factory-demo → .factory/local), los ajustes de tests/test_distribution.py, tests/test_guided.py, tests/test_portabilidad.py, tests/test_tutorial.py y de tools/verify_guide.py, tools/verify_installed.py y tools/verify_collaboration.py, y tests/test_higiene.py, tools/verify_higiene.py y catalogos/factory_higiene.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente: un lanzamiento que quede sin cerrar aunque el revisor haya terminado (también con dos revisores del mismo nombre o candidatos distintos), avisos falsos, que init no borre nada que el usuario tenga, y que la guía siga funcionando de punta a punta con .factory/local/. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-higiene/.venv/bin/python -m unittest tests.test_higiene tests.test_tutorial tests.test_portabilidad </dev/null . No corras la suite completa. Nombrá archivos con rutas relativas.
