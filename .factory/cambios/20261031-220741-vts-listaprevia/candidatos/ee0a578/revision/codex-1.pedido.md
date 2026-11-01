Sos un revisor independiente del cambio 20261031-220741-vts-listaprevia de un proyecto que usa Oracle Factory: «Una lista previa a la revisión con las clases de problema que más rondas cuestan». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-lista-previa/openspec/changes/20261031-220741-vts-listaprevia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-lista-previa/openspec/changes/20261031-220741-vts-listaprevia/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato ee0a578 (sólo lectura): /home/workstation/Dev/factory-lista-previa/.factory/local/revisiones/ee0a578-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-lista-previa/.factory/cambios/20261031-220741-vts-listaprevia/candidatos/ee0a578/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261031-220741-vts-listaprevia/candidatos/5bdd65d/revision/agy2-1.json
- .factory/cambios/20261031-220741-vts-listaprevia/candidatos/5bdd65d/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261031-220741-vts-listaprevia.md, kb/requisitos/practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa.md, kb/requisitos/practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente.md, kb/requisitos/practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-lista-previa/.factory/local/revisores/ee0a578-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-lista-previa/.factory/local/revisores/ee0a578-codex-1/informe.json --paquete /home/workstation/Dev/factory-lista-previa/.factory/cambios/20261031-220741-vts-listaprevia/candidatos/ee0a578/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-lista-previa/.factory/local/revisiones/ee0a578-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Segunda vuelta del cambio lista-previa (oracle_factory/lista_previa.py, flujo_revision.py, agentes.py, docs/lista-previa.md, tools/medir_rondas.py, tools/verify_lista_previa.py, tests/test_lista_previa.py, tests/test_medir_rondas.py). La primera vuelta dejó, ya corregido: las cifras de la medición estaban mal (las rondas se ordenaban por la fecha de los archivos; ahora por los eventos, con tools/medir_rondas.py reproducible y una prueba que lo protege) y la proposal.md y docs/lista-previa.md las traen corregidas; comprobar_documento ahora exige que la lista numerada de la sección «Las preguntas» sea exactamente la del código, en el mismo orden, sin preguntas de más; pedir_revision vacía el buffer; una prueba verifica que la lista no viaje en ningún argumento del revisor. Verificá esos arreglos, revisá que las cifras y afirmaciones de docs/lista-previa.md coincidan con lo que imprime tools/medir_rondas.py sobre este repositorio, y buscá errores nuevos reales; clasificá por severidad.
