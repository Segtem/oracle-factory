Sos un revisor independiente del cambio 20261014-000054-paquete-producto de un proyecto que usa Oracle Factory: «El paquete de revisión deja fuera lo que no es producto». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-paquete-producto/openspec/changes/20261014-000054-paquete-producto/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-paquete-producto/openspec/changes/20261014-000054-paquete-producto/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato e919597 (sólo lectura): /home/workstation/Dev/factory-paquete-producto/.factory/local/revisiones/e919597
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-paquete-producto/.factory/cambios/20261014-000054-paquete-producto/candidatos/e919597/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261014-000054-paquete-producto/candidatos/eef8ecc/revision/agy-1.json
- .factory/cambios/20261014-000054-paquete-producto/candidatos/eef8ecc/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-paquete-producto/.factory/local/revisores/e919597-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-paquete-producto/.factory/local/revisores/e919597-codex-1/informe.json --paquete /home/workstation/Dev/factory-paquete-producto/.factory/cambios/20261014-000054-paquete-producto/candidatos/e919597/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-paquete-producto/.factory/local/revisiones/e919597
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. La vuelta 1 dejó agy-1 y PP-01 (un diff sin producto metía los registros en el paquete; ahora siempre se excluyen y, sin producto, pedir-revision explica cómo revisar con --base), agy-2 y agy-3 (pruebas con paquetes reales de Clue), agy-4 (valores no texto) y agy-5 (estado avisa por qué descarta un informe). Revisá que los arreglos sean correctos y no rompan lo anterior. Revisá la implementación (oracle_factory/cli.py: exclusiones_del_paquete, producto_excluido, el armado del paquete y del pedido en pedir_revision y la comprobación en material_del_candidato) contra los 2 requisitos de la spec, y si tests/test_paquete_producto.py prueba de verdad cada escenario. Este paquete ya se armó con las exclusiones nuevas: .factory/ y tareas/ quedan afuera. Mirá especialmente: archivos del producto que podrían quedar excluidos o registros que podrían colarse, el caso de un diff sin producto, que un informe viejo sin exclusiones se siga usando, y que la comprobación no se pueda saltear. Clue 0.1.0a2 es la versión fijada (pyproject.toml). Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-paquete-producto && /home/workstation/Dev/factory-paquete-producto/.venv/bin/python -m unittest tests.test_paquete_producto tests.test_revisores </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
