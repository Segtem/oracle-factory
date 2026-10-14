Sos un revisor independiente del cambio 20261014-145018-donde-ausente de un proyecto que usa Oracle Factory: «Spec de cli: lo ausente en donde es lo que un registro nombra y ya no está». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-donde-ausente/openspec/changes/20261014-145018-donde-ausente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-donde-ausente/openspec/changes/20261014-145018-donde-ausente/specs/cli/spec.md

Qué revisar:
- Checkout del candidato e98ed8d (sólo lectura): /home/workstation/Dev/factory-donde-ausente/.factory/local/revisiones/e98ed8d
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-donde-ausente/.factory/cambios/20261014-145018-donde-ausente/candidatos/e98ed8d/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261014-145018-donde-ausente/candidatos/fba13a5/revision/agy-1.json
- .factory/cambios/20261014-145018-donde-ausente/candidatos/fba13a5/revision/codex-1.json
- .factory/cambios/20261014-145018-donde-ausente/candidatos/f2f379c/revision/agy-1.json
- .factory/cambios/20261014-145018-donde-ausente/candidatos/f2f379c/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-donde-ausente/.factory/local/revisores/e98ed8d-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-donde-ausente/.factory/local/revisores/e98ed8d-codex-1/informe.json --paquete /home/workstation/Dev/factory-donde-ausente/.factory/cambios/20261014-145018-donde-ausente/candidatos/e98ed8d/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-donde-ausente/.factory/local/revisiones/e98ed8d
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3. La 2 trajo: codex RESUMEN-001 (resumen agrupa los pendientes de medidas iguales, así que no son 'los mismos que estado'), codex DONDE-002 (la prueba no exigía los artefactos fijos) y agy DONDE-TEST-001 (la prueba elegía por la situación que comprueba). Corregidos: la spec dice que resumen agrupa y su GIVEN arma ese caso, y cj2 elige por gate y exige proposal, design, tasks y TAREA.md. Este cambio reescribe (MODIFIED) el requisito «donde y resumen se leen como JSON» de openspec/specs/cli/spec.md, sin cambiar el código: el escenario de un artefacto ausente pasa a ser el de los hechos de un juicio registrado que se borraron. Revisá la spec del cambio contra el código (oracle_factory/cli.py: donde y datos_donde, y resumen --json) y si los casos cj2 de tests/test_cli_json.py prueban de verdad cada escenario y cada promesa del requisito; revisá también tools/verify_donde_ausente.py y los catálogos factory_donde. Mirá especialmente si alguna promesa del requisito reescrito sigue sin cumplirse o sin probarse. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-donde-ausente && /home/workstation/Dev/factory-donde-ausente/.venv/bin/python -m unittest tests.test_cli_json </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
