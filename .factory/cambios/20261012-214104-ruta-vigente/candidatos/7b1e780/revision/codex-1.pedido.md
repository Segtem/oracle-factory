Sos un revisor independiente del cambio 20261012-214104-ruta-vigente de un proyecto que usa Oracle Factory: «ruta apunta al candidato vigente, no a HEAD». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-ruta-vigente/openspec/changes/20261012-214104-ruta-vigente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-ruta-vigente/openspec/changes/20261012-214104-ruta-vigente/specs/estructura/spec.md

Qué revisar:
- Checkout del candidato 7b1e780 (sólo lectura): /home/workstation/Dev/factory-ruta-vigente/.factory/local/revisiones/7b1e780
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-ruta-vigente/.factory/cambios/20261012-214104-ruta-vigente/candidatos/7b1e780/clue/paquete-codex-1.json


Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-ruta-vigente/.factory/local/revisores/7b1e780-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-ruta-vigente/.factory/local/revisores/7b1e780-codex-1/informe.json --paquete /home/workstation/Dev/factory-ruta-vigente/.factory/cambios/20261012-214104-ruta-vigente/candidatos/7b1e780/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-ruta-vigente/.factory/local/revisiones/7b1e780
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: timeout 200 /home/workstation/Dev/factory-ruta-vigente/.venv/bin/python -m unittest tests.test_ruta_vigente tests.test_estructura </dev/null (el checkout no tiene .venv; ese intérprete tiene las dependencias). No corras tools/verify_*.py ni la suite entera. En los límites, escribí rutas relativas al repositorio. Foco: que ruta use el mismo candidato que pedir-revision y juzgar, casos borde de candidato_vigente (sin candidatos, cambios locales de producto, commits de registros) y si las pruebas cubren los escenarios de la spec.
