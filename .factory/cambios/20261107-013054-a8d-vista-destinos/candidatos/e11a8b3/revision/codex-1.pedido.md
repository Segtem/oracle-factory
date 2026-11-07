Sos un revisor independiente del cambio 20261107-013054-a8d-vista-destinos de un proyecto que usa Oracle Factory: «Vista Destinos en el tablero de VS Code». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tablero-destinos/openspec/changes/20261107-013054-a8d-vista-destinos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tablero-destinos/openspec/changes/20261107-013054-a8d-vista-destinos/specs/tablero/spec.md

Qué revisar:
- Checkout del candidato e11a8b3 (sólo lectura): /home/workstation/Dev/factory-tablero-destinos/.factory/local/revisiones/e11a8b3-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tablero-destinos/.factory/cambios/20261107-013054-a8d-vista-destinos/candidatos/e11a8b3/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261107-013054-a8d-vista-destinos/candidatos/87a6bfc/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/contrato_en_node.cjs, modificado: 5 línea(s) quitada(s)
- tests/tablero_en_node.cjs, modificado: 7 línea(s) quitada(s)
- tests/test_contrato_vscode.py, modificado: 3 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261107-013054-a8d-vista-destinos.md, kb/requisitos/tablero_c67ccc28106a13a74.el_contrato_de_la_extension_cubre_destinos.md, kb/requisitos/tablero_c67ccc28106a13a74.el_tablero_muestra_cada_destino_con_su_estado.md, kb/requisitos/tablero_c67ccc28106a13a74.el_tablero_no_consulta_los_destinos_sin_que_se_pida.md, kb/requisitos/tablero_c67ccc28106a13a74.el_tablero_no_despliega_ni_autoriza.md, kb/requisitos/tablero_c67ccc28106a13a74.sin_destinos_o_con_error_el_tablero_sigue.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tablero-destinos/.factory/local/revisores/e11a8b3-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-tablero-destinos/.factory/local/revisores/e11a8b3-codex-1/informe.json --paquete /home/workstation/Dev/factory-tablero-destinos/.factory/cambios/20261107-013054-a8d-vista-destinos/candidatos/e11a8b3/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-tablero-destinos/.factory/local/revisiones/e11a8b3-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 2 de la revisión de la sección Destinos del tablero. Se cerraron destinos-cache-pintura-concurrente y destinos-cache-compartida-entre-proyectos: la consulta ahora se hace en consultarLosDestinos (extension.js), que guarda la respuesta {raiz, datos} y recién después repinta; una generación invalida las consultas que empezaron antes de registrarse un despliegue o cerrarse el panel. Probado en test_td2 con el arnés CONCURRENTE (un registro cambia durante la consulta) y 13 mutaciones, salvo el cambio de raíz con el panel abierto, que el arnés no puede ejercitar (límite declarado). Buscá la clase entera: cualquier otro estado compartido de la extensión que sobreviva entre pinturas, proyectos o sesiones de Live Share (por ejemplo, qué pasa si la consulta falla, si hay dos 'Consultar ahora' seguidos o si el panel se cierra a mitad de la consulta). Marcá como baja lo que sólo ocurra con estados inyectados a mano. Declarado como antes: tres pruebas existentes editadas de forma aditiva.
