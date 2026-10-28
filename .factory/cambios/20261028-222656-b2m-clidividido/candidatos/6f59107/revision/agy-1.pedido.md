Sos un revisor independiente del cambio 20261028-222656-b2m-clidividido de un proyecto que usa Oracle Factory: «Partir cli.py en módulos para alejarlo del límite de Oracle Clue». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-cli-modulos/openspec/changes/20261028-222656-b2m-clidividido/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-cli-modulos/openspec/changes/20261028-222656-b2m-clidividido/specs/cli/spec.md

Qué revisar:
- Checkout del candidato 6f59107 (sólo lectura): /home/workstation/Dev/factory-cli-modulos/.factory/local/revisiones/6f59107-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-cli-modulos/.factory/cambios/20261028-222656-b2m-clidividido/candidatos/6f59107/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261028-222656-b2m-clidividido.md, kb/requisitos/cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse.md, kb/requisitos/cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo.md, kb/requisitos/cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-cli-modulos/.factory/local/revisores/6f59107-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-cli-modulos/.factory/local/revisores/6f59107-agy-1/informe.json --paquete /home/workstation/Dev/factory-cli-modulos/.factory/cambios/20261028-222656-b2m-clidividido/candidatos/6f59107/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-cli-modulos/.factory/local/revisiones/6f59107-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261028-222656-b2m-clidividido/specs/cli/spec.md): es un refactor que parte oracle_factory/cli.py en oracle_factory/parser.py, flujo_revision.py, flujo_medidas.py y lecturas.py sin cambiar lo que hace, más tests/test_cli_modulos.py, tools/tamanos.py, tools/verify_cli_modulos.py, tests/datos/nombres-cli.json y ayuda-cli.json (tomados de cli.py ANTES de mover nada), catalogos/factory_cli_modulos.*.oracle y el párrafo nuevo de docs/estructura.md. Mirá especialmente: que NADA de lo movido haya cambiado de comportamiento (comparalo con el código original en git: git show main:oracle_factory/cli.py), que cada nombre de cli que usa el código movido pase por cli.NOMBRE y que no quede ninguno sin prefijo ni copiado al importar, que las funciones con decoradores, valores por defecto, global o __name__ sigan funcionando, que los dorados sean fieles y los tests no sean circulares, que no se haya pisado ningún módulo existente de oracle_factory/, que cli.py y cada módulo estén bajo los topes, que las importaciones circulares entre cli y los módulos nuevos sean seguras en cualquier orden de importación (por ejemplo importar oracle_factory.flujo_revision primero), y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_cli_modulos tests.test_cli_piloto tests.test_docs </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
