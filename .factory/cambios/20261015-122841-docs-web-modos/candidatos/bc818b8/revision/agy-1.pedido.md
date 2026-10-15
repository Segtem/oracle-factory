Sos un revisor independiente del cambio 20261015-122841-docs-web-modos de un proyecto que usa Oracle Factory: «Docs y web: los modos de trabajo y quién decide qué». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-docs-web-modos/openspec/changes/20261015-122841-docs-web-modos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-docs-web-modos/openspec/changes/20261015-122841-docs-web-modos/specs/web/spec.md

Qué revisar:
- Checkout del candidato bc818b8 (sólo lectura): /home/workstation/Dev/factory-docs-web-modos/.factory/local/revisiones/bc818b8
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-docs-web-modos/.factory/cambios/20261015-122841-docs-web-modos/candidatos/bc818b8/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261015-122841-docs-web-modos/candidatos/39c6c2c/revision/agy-1.json
- .factory/cambios/20261015-122841-docs-web-modos/candidatos/39c6c2c/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-docs-web-modos/.factory/local/revisores/bc818b8-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-docs-web-modos/.factory/local/revisores/bc818b8-agy-1/informe.json --paquete /home/workstation/Dev/factory-docs-web-modos/.factory/cambios/20261015-122841-docs-web-modos/candidatos/bc818b8/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-docs-web-modos/.factory/local/revisiones/bc818b8
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. La 1 (agy F1-F8, codex F1-F2) quedó corregida: estado contado como sale (una propuesta aparece en Pendiente y en los eventos, no como decisión; orden real de las líneas), el cierre en confirmacion lo toma una persona, el nombre es el de Git o el usuario del sistema; la tabla de la página se prueba por su texto visible y sus encabezados, y con celdas cambiadas en el HTML y en el Markdown; el enlace se exige en la tarjeta de los modos; cada catálogo nombra sólo sus escenarios. Revisá docs/modos.md, site/modos.html, el enlace en site/index.html, el README y los estilos nuevos de site/style.css contra los 2 requisitos de la spec, y si tests/test_modos_web.py prueba de verdad cada escenario; revisá también tools/verify_docs_web_modos.py y los catálogos factory_modos_web. Mirá especialmente: afirmaciones del documento o la página que no coinciden con el código (oracle_factory/modos.py, oracle_factory/cli.py: decidir, cambiar_modo, actor, quien, importar, abandonar), la tabla de quién decide, el ejemplo de estado, accesibilidad básica de la página (encabezados, tabla con th y scope) y que la página funcione en un teléfono. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-docs-web-modos && /home/workstation/Dev/factory-docs-web-modos/.venv/bin/python -m unittest tests.test_modos_web tests.test_web </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
