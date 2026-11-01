Sos un revisor independiente del cambio 20261101-205730-dm3-alarmasflujo de un proyecto que usa Oracle Factory: «Avisar de los bucles de revisión y de los cambios demasiado grandes». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-alarmas-flujo/openspec/changes/20261101-205730-dm3-alarmasflujo/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-alarmas-flujo/openspec/changes/20261101-205730-dm3-alarmasflujo/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 9edd02d (sólo lectura): /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisiones/9edd02d-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-alarmas-flujo/.factory/cambios/20261101-205730-dm3-alarmasflujo/candidatos/9edd02d/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261101-205730-dm3-alarmasflujo.md, kb/requisitos/practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado.md, kb/requisitos/practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto.md, kb/requisitos/practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisores/9edd02d-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisores/9edd02d-codex-1/informe.json --paquete /home/workstation/Dev/factory-alarmas-flujo/.factory/cambios/20261101-205730-dm3-alarmasflujo/candidatos/9edd02d/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-alarmas-flujo/.factory/local/revisiones/9edd02d-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio alarmas-flujo: oracle_factory/alarmas.py (rondas, lineas_de_producto, avisos_de_flujo, del_flujo, avisos_del_flujo), su cableado en cli.py (mostrar) y lecturas.py (datos_estado, claves bucle_de_revision y cambio_grande), docs/tests.md, tools/verify_alarmas_flujo.py y tests/test_alarmas_flujo.py. Son avisos: no deben bloquear ni cambiar pendientes ni próximo paso, y un fallo de Git o un registro raro no debe romper el estado. Buscá errores reales: el parseo de `git diff --numstat -z -M` (renombres, binarios, rutas raras, copias), qué cuenta como producto y como prueba, la definición de ronda (candidatos distintos, eventos raros), falsos avisos o silencios, divergencias entre documento y código, y pruebas que pasan por construcción. Clasificá por severidad.
