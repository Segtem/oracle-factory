Sos un revisor independiente del cambio 20261106-205202-8od-destinos de un proyecto que usa Oracle Factory: «Despliegue a varios destinos con prueba de que todo quedó funcionando». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-despliegue/openspec/changes/20261106-205202-8od-destinos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-despliegue/openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md

Qué revisar:
- Checkout del candidato ee11492 (sólo lectura): /home/workstation/Dev/factory-despliegue/.factory/local/revisiones/ee11492-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-despliegue/.factory/cambios/20261106-205202-8od-destinos/candidatos/ee11492/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261106-205202-8od-destinos/candidatos/1915e91/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
- tests/test_web_paginas.py, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261106-205202-8od-destinos.md, kb/requisitos/despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos.md, kb/requisitos/despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto.md, kb/requisitos/despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto.md, kb/requisitos/despliegue_c1f413032a7a55aa1.sirve_para_cualquier_proyecto.md, kb/requisitos/despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona.md, kb/requisitos/despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho.md, tareas): 16 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-despliegue/.factory/local/revisores/ee11492-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Si el paquete omite un archivo porque no es texto (una imagen, por ejemplo), abrilo vos en el checkout y declaralo con una línea de
limitations por archivo, exactamente `abierto: RUTA` (la ruta tal como figura en el paquete). Clue te obliga a marcar review_status
"incompleto" por esa omisión; Factory la acepta sólo si cada binario omitido está declarado así. No declares uno que no abriste.
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-despliegue/.factory/local/revisores/ee11492-codex-1/informe.json --paquete /home/workstation/Dev/factory-despliegue/.factory/cambios/20261106-205202-8od-destinos/candidatos/ee11492/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-despliegue/.factory/local/revisiones/ee11492-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 2. Se cerraron DPL-01 (version obligatoria), DPL-02 (tope del conjunto validado), DPL-03 (rollback también con seguir) y DPL-04 (el tope mata el grupo de procesos). Cerrá la CLASE: qué otra promesa de la spec o del diseño no verifica el código o las pruebas, y listalo todo junto. Si exige inyectar a mano un estado imposible (registros editados), marcalo bajo. Declarado: se editó tests/datos/ayuda-cli.json (sólo entradas nuevas) y el conteo de guías de tests/test_web_paginas.py (12 a 13); ningún otro test existente. No se implementó 'alcance' del diseño.
