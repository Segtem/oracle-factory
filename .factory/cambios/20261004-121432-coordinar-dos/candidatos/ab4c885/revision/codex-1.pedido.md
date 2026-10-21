Sos un revisor independiente del cambio 20261004-121432-coordinar-dos de un proyecto que usa Oracle Factory: «Coordinar dos personas con sus agentes sin interferencias». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-coordinar/openspec/changes/20261004-121432-coordinar-dos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-coordinar/openspec/changes/20261004-121432-coordinar-dos/specs/colaboracion/spec.md

Qué revisar:
- Checkout del candidato ab4c885 (sólo lectura): /home/workstation/Dev/factory-coordinar/.factory/local/revisiones/ab4c885-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-coordinar/.factory/cambios/20261004-121432-coordinar-dos/candidatos/ab4c885/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/c85f68d/revision/agy-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/c85f68d/revision/codex-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/f335782/revision/agy-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/f335782/revision/codex-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/39675c8/revision/agy-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/39675c8/revision/codex-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/2b81712/revision/agy-1.json
- .factory/cambios/20261004-121432-coordinar-dos/candidatos/2b81712/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261004-121432-coordinar-dos.md, kb/requisitos/colaboracion_c20a7f5e3d414985d.aislamiento_y_sincronizacion_explicitos.md, kb/requisitos/colaboracion_c20a7f5e3d414985d.demostracion_reproducible_con_limites.md, kb/requisitos/colaboracion_c20a7f5e3d414985d.integracion_serializada_y_evidencia_vigente.md, kb/requisitos/colaboracion_c20a7f5e3d414985d.relevo_recuperable.md, kb/requisitos/colaboracion_c20a7f5e3d414985d.reparto_explicito_del_trabajo.md, kb/requisitos/colaboracion_c20a7f5e3d414985d.revision_vinculada_a_una_version.md, kb/requisitos/colaboracion_cf0b1719108ccce04.aislamiento_y_sincronizacion_explicitos.md, kb/requisitos/colaboracion_cf0b1719108ccce04.demostracion_reproducible_con_limites.md, kb/requisitos/colaboracion_cf0b1719108ccce04.el_banco_informa_sus_numeros.md, kb/requisitos/colaboracion_cf0b1719108ccce04.el_banco_pone_a_prueba_el_trabajo_a_la_vez.md, kb/requisitos/colaboracion_cf0b1719108ccce04.el_banco_pone_a_prueba_el_trabajo_de_a_turnos.md, kb/requisitos/colaboracion_cf0b1719108ccce04.integracion_serializada_y_evidencia_vigente.md, kb/requisitos/colaboracion_cf0b1719108ccce04.relevo_recuperable.md, kb/requisitos/colaboracion_cf0b1719108ccce04.reparto_explicito_del_trabajo.md, kb/requisitos/colaboracion_cf0b1719108ccce04.revision_vinculada_a_una_version.md, tareas): 229 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-coordinar/.factory/local/revisores/ab4c885-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-coordinar/.factory/local/revisores/ab4c885-codex-1/informe.json --paquete /home/workstation/Dev/factory-coordinar/.factory/cambios/20261004-121432-coordinar-dos/candidatos/ab4c885/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-coordinar/.factory/local/revisiones/ab4c885-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 5: se corrigió REV-001 de la vuelta 4: informe_completo exige las versiones de oracle-factory, oracle-metalenguaje, oracle-task, oracle-clue, python y git. Revisá el cambio, contra los 9 requisitos de su spec: tools/banco.py (los 13 escenarios del banco de concurrencia y su informe, también --real), tools/verify_banco.py y catalogos/factory_banco.*.oracle (lo que miden de los 3 requisitos del banco), el caso C4 de tools/verify_collaboration.py (ahora comprueba que dos cambios del mismo segundo tienen IDs distintos) y docs/colaboracion.md. Mirá especialmente: escenarios que den ok sin comprobar lo que su requisito promete (decisiones perdidas o mal atribuidas, conflictos detectados tarde, evidencia vieja vigente, quien retoma ve el estado de la otra persona), medidas que pasen con hechos que no prueban el requisito, la reproducibilidad con la misma semilla, y lo que la guía afirma que el código no hace. Para correr el banco usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-coordinar/.venv/bin/python tools/banco.py --salida /tmp/banco-revision-$RANDOM </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
