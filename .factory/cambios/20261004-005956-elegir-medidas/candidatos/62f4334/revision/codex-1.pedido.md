Sos un revisor independiente del cambio 20261004-005956-inicio-guiado de un proyecto que usa Oracle Factory: «Inicio guiado». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-cerrar-guiadas/openspec/changes/20261004-005956-inicio-guiado/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-cerrar-guiadas/openspec/changes/20261004-005956-inicio-guiado/specs/onboarding/spec.md

Qué revisar:
- Checkout del candidato 62f4334 (sólo lectura): /home/workstation/Dev/factory-cerrar-guiadas/.factory/local/revisiones/62f4334
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-cerrar-guiadas/.factory/cambios/20261004-005956-inicio-guiado/candidatos/62f4334/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261004-005956-inicio-guiado/candidatos/4295fb1/revision/agy-1.json
- .factory/cambios/20261004-005956-inicio-guiado/candidatos/4295fb1/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-cerrar-guiadas/.factory/local/revisores/62f4334-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-cerrar-guiadas/.factory/local/revisores/62f4334-codex-1/informe.json --paquete /home/workstation/Dev/factory-cerrar-guiadas/.factory/cambios/20261004-005956-inicio-guiado/candidatos/62f4334/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-cerrar-guiadas/.factory/local/revisiones/62f4334
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Cambio viejo (2026-10-04) que se cierra ahora con evidencia, vuelta 2. El candidato reforzó las aserciones de tests/test_guided.py para matar los mutantes que agy dejó vivos en la vuelta 1 (el de --sin-medir de espacios se tomó como equivalente porque Oracle también lo rechaza; verificalo). Revisá si el código actual de oracle_factory/cli.py cumple los requisitos de este cambio (requisitos/ y su spec en openspec/changes/20261004-005956-inicio-guiado/specs/) y si los casos enumerados en tools/verify_contracts.py para este cambio (tests/test_guided.py) prueban de verdad cada requisito o dejan huecos. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-cerrar-guiadas && /home/workstation/Dev/factory-cerrar-guiadas/.venv/bin/python -m unittest tests.test_guided </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
