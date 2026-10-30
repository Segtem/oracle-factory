Sos un revisor independiente del cambio 20261030-100740-f1g-entregaa16 de un proyecto que usa Oracle Factory: «Preparar la distribución 0.1.0a16». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-entrega-a16/openspec/changes/20261030-100740-f1g-entregaa16/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-entrega-a16/openspec/changes/20261030-100740-f1g-entregaa16/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato c1c1426 (sólo lectura): /home/workstation/Dev/factory-entrega-a16/.factory/local/revisiones/c1c1426-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-entrega-a16/.factory/cambios/20261030-100740-f1g-entregaa16/candidatos/c1c1426/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261030-100740-f1g-entregaa16/candidatos/ef2ef67/revision/agy-1.json
- .factory/cambios/20261030-100740-f1g-entregaa16/candidatos/ef2ef67/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261030-100740-f1g-entregaa16.md, kb/requisitos/distribucion_c429661c62d96c96b.el_wheel_a16_instalado_ofrece_lo_nuevo.md, kb/requisitos/distribucion_c429661c62d96c96b.la_entrega_a16_registra_sus_pruebas_y_sus_limites.md, kb/requisitos/distribucion_c429661c62d96c96b.la_version_a16_es_coherente_y_declara_su_estado.md, tareas): 17 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-entrega-a16/.factory/local/revisores/c1c1426-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-entrega-a16/.factory/local/revisores/c1c1426-agy2-1/informe.json --paquete /home/workstation/Dev/factory-entrega-a16/.factory/cambios/20261030-100740-f1g-entregaa16/candidatos/c1c1426/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-entrega-a16/.factory/local/revisiones/c1c1426-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Segunda ronda de la preparación de la distribución 0.1.0a16 de Factory (versión, notas, README, site, guías; tools/probar_entrega_a16.py, verify_entrega_a16.py, mutar_entrega_a16.py; tests/test_entrega_a16.py y test_entrega_integridad_a16.py). La primera ronda dejó: evidencia no atada al commit (ahora se exige árbol limpio), rutas locales en instalacion.json (ahora se sustituyen), una comprobación tautológica, ea3 sin mutaciones y mutaciones_ok fijo. Verificá esos arreglos y buscá errores nuevos reales; clasificá por severidad.
