Sos un revisor independiente del cambio 20261102-221210-70x-caminoligero de un proyecto que usa Oracle Factory: «Un camino ligero de revisión para los cambios chicos». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-camino-ligero/openspec/changes/20261102-221210-70x-caminoligero/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-camino-ligero/openspec/changes/20261102-221210-70x-caminoligero/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 144ad8b (sólo lectura): /home/workstation/Dev/factory-camino-ligero/.factory/local/revisiones/144ad8b-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-camino-ligero/.factory/cambios/20261102-221210-70x-caminoligero/candidatos/144ad8b/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261102-221210-70x-caminoligero.md, kb/requisitos/practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente.md, kb/requisitos/practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero.md, kb/requisitos/practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero.md, tareas): 11 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-camino-ligero/.factory/local/revisores/144ad8b-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-camino-ligero/.factory/local/revisores/144ad8b-codex-1/informe.json --paquete /home/workstation/Dev/factory-camino-ligero/.factory/cambios/20261102-221210-70x-caminoligero/candidatos/144ad8b/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-camino-ligero/.factory/local/revisiones/144ad8b-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio camino-ligero: oracle_factory/alarmas.py (UMBRAL_LIGERO, REGLAS_DE_DECISION, archivos_tocados, camino_del_candidato, linea_camino), su cableado en cli.py (mostrar: la línea «Camino de revisión»), lecturas.py (clave camino del JSON), agentes.py (el bullet de la guía; AGENTS.md está regenerado), docs/agentes.md, tests/test_camino_ligero.py y los catálogos. La evidencia de ESTE cambio la produjo tools/verificar_cambio.py (no hay verify_<x>.py a mano). Es una orientación: no debe cambiar pendientes, próximo paso ni quién decide, y un fallo de Git o la falta de candidato no deben afirmar un camino ni romper el estado. Este cambio toca cli.py (una regla de decisión), así que él mismo es «completo». Buscá errores reales y de impacto práctico: qué cuenta como producto/prueba, renombres y copias, rutas raras, la lista de reglas (¿falta alguna que decida quién puede qué? ¿sobra alguna?), falsos «ligero» (un cambio que debería ser completo), divergencias entre la guía, el documento y el código, y pruebas que pasan por construcción. Marcá cuáles hallazgos son exóticos y por qué. Clasificá por severidad.
Dato del candidato: tests/datos/cli_texto/estado.txt (la referencia de texto de `estado`, que usa tests/test_cli_json.py::test_cj3_el_texto_sigue_igual) recibió una línea nueva, la de «Camino de revisión: ligero (0 líneas de producto, …)», porque el estado de ese fixture tiene un candidato; no se quitó ninguna línea. Decí si te parece justificado.
