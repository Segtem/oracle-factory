Sos un revisor independiente del cambio 20261014-100834-revision-simultanea de un proyecto que usa Oracle Factory: «pedir-revision tolera pedidos simultáneos sobre el mismo candidato». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-revision-simultanea/openspec/changes/20261014-100834-revision-simultanea/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-revision-simultanea/openspec/changes/20261014-100834-revision-simultanea/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato f9b6d27 (sólo lectura): /home/workstation/Dev/factory-revision-simultanea/.factory/local/revisiones/f9b6d27
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-revision-simultanea/.factory/cambios/20261014-100834-revision-simultanea/candidatos/f9b6d27/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261014-100834-revision-simultanea/candidatos/5b949fc/revision/agy-1.json
- .factory/cambios/20261014-100834-revision-simultanea/candidatos/5b949fc/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-revision-simultanea/.factory/local/revisores/f9b6d27-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-revision-simultanea/.factory/local/revisores/f9b6d27-agy-1/informe.json --paquete /home/workstation/Dev/factory-revision-simultanea/.factory/cambios/20261014-100834-revision-simultanea/candidatos/f9b6d27/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-revision-simultanea/.factory/local/revisiones/f9b6d27
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: la 1 de agy pidió que las pruebas fuercen la carrera del evento en factory.json y que comprueben que el revisor corre fuera del turno (H-01, H-02); el H-03 (evento antes del informe en revision/) es previo a este cambio. Revisá la implementación (oracle_factory/cli.py: turno_de_pedidos y su uso en pedir_revision) contra los 2 requisitos de la spec, y si tests/test_revision_simultanea.py prueba de verdad cada escenario. Mirá especialmente: carreras que el turno no cubre (checkout, numeración del paquete y de la carpeta de trabajo, el informe y el pedido guardados en revision/, el evento en factory.json), que el turno no se tome durante lo largo (el revisor), que un pedido interrumpido no deje nada trabado, y si las pruebas fallarían con el código anterior. Estos dos pedidos (codex y agy) se lanzaron a la vez con este mismo código. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-revision-simultanea && /home/workstation/Dev/factory-revision-simultanea/.venv/bin/python -m unittest tests.test_revision_simultanea tests.test_revisores </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
