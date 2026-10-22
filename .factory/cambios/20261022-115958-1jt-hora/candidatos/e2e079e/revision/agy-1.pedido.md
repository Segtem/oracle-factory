Sos un revisor independiente del cambio 20261022-115958-1jt-hora de un proyecto que usa Oracle Factory: «La hora de cada evento con microsegundos: lo de dos ramas en el mismo segundo queda en orden». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-hora/openspec/changes/20261022-115958-1jt-hora/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-hora/openspec/changes/20261022-115958-1jt-hora/specs/colaboracion/spec.md

Qué revisar:
- Checkout del candidato e2e079e (sólo lectura): /home/workstation/Dev/factory-hora/.factory/local/revisiones/e2e079e-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-hora/.factory/cambios/20261022-115958-1jt-hora/candidatos/e2e079e/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261022-115958-1jt-hora/candidatos/6489a62/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/6489a62/revision/codex-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/7e3abab/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/7e3abab/revision/codex-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/57e960c/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/57e960c/revision/codex-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/4ad55f4/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/4ad55f4/revision/codex-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/3a0cba6/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/3a0cba6/revision/codex-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/bf616bd/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/bf616bd/revision/codex-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/21fa6bb/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/21fa6bb/revision/codex-1.json
Riesgos ya aceptados por una persona en este cambio (no los reportes otra vez salvo que el defecto haya cambiado o empeorado):
- oracle_factory/cli.py: Dos ramas con el mismo registro base aún pueden dar la misma hora a eventos simultáneos (aceptado por Brian Hollweg: Acepto el riesgo: Dos ramas con el mismo registro base aún pueden dar la misma hora a eventos simultáneos)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261022-115958-1jt-hora.md, kb/requisitos/colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio.md, kb/requisitos/colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo.md, tareas): 68 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-hora/.factory/local/revisores/e2e079e-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-hora/.factory/local/revisores/e2e079e-agy-1/informe.json --paquete /home/workstation/Dev/factory-hora/.factory/cambios/20261022-115958-1jt-hora/candidatos/e2e079e/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-hora/.factory/local/revisiones/e2e079e-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 8: la evidencia de la vuelta 7 encontró una prueba que fallaba a veces (test_kb1): kb.cambios_del_proyecto ordenaba por ID suponiendo orden de creación, y desde los IDs con letras al azar dos del mismo segundo no lo cumplen; ahora ordena por la hora del primer evento (unir.hora) y después por ID. Mirá también que ese orden no cambie nada más (resumen, rag, el índice del vault). Revisá el cambio, contra los 2 requisitos de su spec: ahora() en oracle_factory/cli.py (la hora con microsegundos), cómo se comparan y ordenan las horas en el resto del código (unir.py, kb.py, resumen.py, tablero.py, la extensión de VS Code), tools/banco.py (a4 sin esperar entre días), tests/test_hora.py, tools/verify_hora.py, catalogos/factory_hora.*.oracle y docs/colaboracion.md. Mirá especialmente: comparaciones de horas como texto que fallen al mezclar horas en segundos y con microsegundos, horas que se muestren o se corten mal, eventos iguales que antes se deduplicaban y ahora no, y si las pruebas prueban lo que prometen los requisitos. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-hora/.venv/bin/python -m unittest tests.test_hora </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
