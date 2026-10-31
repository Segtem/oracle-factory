Sos un revisor independiente del cambio 20261031-220741-vts-listaprevia de un proyecto que usa Oracle Factory: «Una lista previa a la revisión con las clases de problema que más rondas cuestan». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-lista-previa/openspec/changes/20261031-220741-vts-listaprevia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-lista-previa/openspec/changes/20261031-220741-vts-listaprevia/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 5bdd65d (sólo lectura): /home/workstation/Dev/factory-lista-previa/.factory/local/revisiones/5bdd65d-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-lista-previa/.factory/cambios/20261031-220741-vts-listaprevia/candidatos/5bdd65d/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261031-220741-vts-listaprevia.md, kb/requisitos/practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa.md, kb/requisitos/practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente.md, kb/requisitos/practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-lista-previa/.factory/local/revisores/5bdd65d-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-4-argon-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-lista-previa/.factory/local/revisores/5bdd65d-agy2-1/informe.json --paquete /home/workstation/Dev/factory-lista-previa/.factory/cambios/20261031-220741-vts-listaprevia/candidatos/5bdd65d/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-lista-previa/.factory/local/revisiones/5bdd65d-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio lista-previa: oracle_factory/lista_previa.py (las preguntas y comprobar_documento), su uso en flujo_revision.pedir_revision (se imprime antes de lanzar al revisor, no entra al pedido), docs/lista-previa.md, la línea de la guía en oracle_factory/agentes.py y AGENTS.md, y tests/test_lista_previa.py. Es un recordatorio que no bloquea. Buscá errores reales: afirmaciones falsas en el documento (cifras, claims de la medición), preguntas ambiguas o que se contradicen, que la lista llegue al revisor sin querer, divergencia entre documento, código y guía, pruebas que pasan por construcción; clasificá por severidad.
