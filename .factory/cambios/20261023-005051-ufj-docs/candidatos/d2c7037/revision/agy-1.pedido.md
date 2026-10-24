Sos un revisor independiente del cambio 20261023-005051-ufj-docs de un proyecto que usa Oracle Factory: «La documentación al día: README, docs y web cuentan lo que Factory hace hoy, con guías nuevas y comprobadas contra la CLI». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-docs/openspec/changes/20261023-005051-ufj-docs/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-docs/openspec/changes/20261023-005051-ufj-docs/specs/web/spec.md

Qué revisar:
- Checkout del candidato d2c7037 (sólo lectura): /home/workstation/Dev/factory-docs/.factory/local/revisiones/d2c7037-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-docs/.factory/cambios/20261023-005051-ufj-docs/candidatos/d2c7037/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261023-005051-ufj-docs/candidatos/f1d0e7f/revision/agy-2.json
- .factory/cambios/20261023-005051-ufj-docs/candidatos/f1d0e7f/revision/agy-3.json
- .factory/cambios/20261023-005051-ufj-docs/candidatos/f1d0e7f/revision/agy2-2.json
- .factory/cambios/20261023-005051-ufj-docs/candidatos/f1d0e7f/revision/agy2-3.json
- .factory/cambios/20261023-005051-ufj-docs/candidatos/eda5953/revision/agy-1.json
- .factory/cambios/20261023-005051-ufj-docs/candidatos/eda5953/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261023-005051-ufj-docs.md, kb/requisitos/web_c2ef84113c2f0ab7f.la_documentacion_cuenta_lo_que_factory_hace_hoy.md, kb/requisitos/web_c2ef84113c2f0ab7f.la_documentacion_se_comprueba_contra_la_cli.md, tareas): 30 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-docs/.factory/local/revisores/d2c7037-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-docs/.factory/local/revisores/d2c7037-agy-1/informe.json --paquete /home/workstation/Dev/factory-docs/.factory/cambios/20261023-005051-ufj-docs/candidatos/d2c7037/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-docs/.factory/local/revisiones/d2c7037-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3: se corrigieron todos los hallazgos de ambas revisiones documentales: versiones finales y de otras series, exención explícita del historial, no aceptar palabras en prosa como comandos, comandos cortos/mayúsculas/dígitos/_/opciones con = o valores entre comillas, documentación de ejemplo, referencia a fabrica.py, enlace de cada herramienta, árbol de carpetas y búsqueda recursiva en plantillas. Revisá todos los archivos del paquete y los requisitos completos. La evidencia nueva está commiteada: 468 pruebas OK, 10 omitidas, fuentes estables; siete mutaciones detectadas y comparación del texto web pasada en Chromium. LEEME_FACTORY de cli.py no cambió desde eda5953, cuya revisión de agy y agy2 quedó limpia en candidatos/eda5953/revision; el paquete usa una base sintética con ese mismo cli.py para no superar 1 MB. Revisá también esa descripción y contrastá esos informes anteriores; verificá que no haya regresiones. Para pruebas, desde la raíz del checkout utilizá PYTHONPATH=. /home/workstation/Dev/factory-docs/.venv/bin/python -m unittest tests.test_docs </dev/null (el clon no tiene .venv propio). No corras suite completa. Reproducí y documentá cualquier hallazgo medio o más. No edites el producto ni la configuración de Git. El contexto se divide en dos paquetes por el límite de 1 MB de Clue: leeme (sólo oracle_factory/cli.py) y documentos (todos los otros archivos del producto). Son bases sintéticas locales para dividir el diff; el candidato no cambia y no se reescribe la historia publicada. Revisá contra los requisitos de su spec en openspec/changes/20261023-005051-ufj-docs/specs/web/spec.md. Mirá especialmente enlaces y comandos de las guías, afirmaciones sobre funcionalidades disponibles, falsos negativos y falsos positivos del comprobador de comandos y versiones, y si las pruebas y evidencia realmente respaldan la spec. La configuración de agy2 fue autorizada por Brian dentro de este cambio. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_docs </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. No modifiques el producto ni ejecutes comandos reservados a una persona. Nombrá archivos con rutas relativas. Informá los hallazgos con severidad, ubicación, explicación y un caso concreto que los reproduzca.
