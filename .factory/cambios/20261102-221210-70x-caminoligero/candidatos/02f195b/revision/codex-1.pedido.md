Sos un revisor independiente del cambio 20261102-221210-70x-caminoligero de un proyecto que usa Oracle Factory: «Un camino ligero de revisión para los cambios chicos». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-camino-ligero/openspec/changes/20261102-221210-70x-caminoligero/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-camino-ligero/openspec/changes/20261102-221210-70x-caminoligero/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 02f195b (sólo lectura): /home/workstation/Dev/factory-camino-ligero/.factory/local/revisiones/02f195b-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-camino-ligero/.factory/cambios/20261102-221210-70x-caminoligero/candidatos/02f195b/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261102-221210-70x-caminoligero/candidatos/144ad8b/revision/agy2-flash-1.json
- .factory/cambios/20261102-221210-70x-caminoligero/candidatos/144ad8b/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261102-221210-70x-caminoligero.md, kb/requisitos/practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente.md, kb/requisitos/practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero.md, kb/requisitos/practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero.md, tareas): 19 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-camino-ligero/.factory/local/revisores/02f195b-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-camino-ligero/.factory/local/revisores/02f195b-codex-1/informe.json --paquete /home/workstation/Dev/factory-camino-ligero/.factory/cambios/20261102-221210-70x-caminoligero/candidatos/02f195b/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-camino-ligero/.factory/local/revisiones/02f195b-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la segunda ronda de camino-ligero. La primera trajo 7 hallazgos: alarmas.py no estaba entre las reglas de decisión (ahora sí, por decisión de Brian: es donde vive el clasificador; la lista tiene nueve archivos), la prueba de la guía comparaba el código contra sí mismo (ahora hay otra con literales: «hasta 150 líneas de producto» y los nueve archivos), docs/agentes.md no tenía prueba (hay una), y cuatro huecos de cómputo declarados como límite en un párrafo «Límites conocidos» de docs/agentes.md: archivos binarios sin líneas, lo borrado no resta, renombres puros de pruebas a producto y copias sin modificar su origen. Esos cuatro NO son defectos del candidato a menos que el documento y el código se contradigan o que el límite oculte algo de impacto práctico: decí si te parece que el límite está bien dicho. También: tests/datos/cli_texto/estado.txt recibió una línea nueva (sin quitar ninguna) por la línea «Camino de revisión» del estado. Verificá que los arreglos cubren la CLASE entera y buscá errores reales nuevos y de impacto práctico en oracle_factory/alarmas.py, cli.py (mostrar), lecturas.py, agentes.py, docs/agentes.md, tests/test_camino_ligero.py y los catálogos; marcá los exóticos. Clasificá por severidad.
