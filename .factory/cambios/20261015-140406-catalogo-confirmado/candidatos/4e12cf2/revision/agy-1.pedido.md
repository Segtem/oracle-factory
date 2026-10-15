Sos un revisor independiente del cambio 20261015-140406-catalogo-confirmado de un proyecto que usa Oracle Factory: «Una medida confirmada cuyo catálogo cambia vuelve a pedir decisión». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-catalogo-confirmado/openspec/changes/20261015-140406-catalogo-confirmado/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-catalogo-confirmado/openspec/changes/20261015-140406-catalogo-confirmado/specs/modos/spec.md

Qué revisar:
- Checkout del candidato 4e12cf2 (sólo lectura): /home/workstation/Dev/factory-catalogo-confirmado/.factory/local/revisiones/4e12cf2
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-catalogo-confirmado/.factory/cambios/20261015-140406-catalogo-confirmado/candidatos/4e12cf2/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261015-140406-catalogo-confirmado/candidatos/0e22578/revision/agy-1.json
- .factory/cambios/20261015-140406-catalogo-confirmado/candidatos/0e22578/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-catalogo-confirmado/.factory/local/revisores/4e12cf2-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-catalogo-confirmado/.factory/local/revisores/4e12cf2-agy-1/informe.json --paquete /home/workstation/Dev/factory-catalogo-confirmado/.factory/cambios/20261015-140406-catalogo-confirmado/candidatos/4e12cf2/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-catalogo-confirmado/.factory/local/revisiones/4e12cf2
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. La 1 (agy un alto, tres medios, un bajo; codex un medio) quedó corregida: decidir con --requisito tras un catálogo cambiado queda como decisión, no confirmación; una propuesta sin huellas no se confirma tal cual; la medida que falta o el catálogo ilegible se nombran con su archivo relativo, distinguiendo cambió, falta e ilegible; un catálogo por llamada; pruebas de esos casos con mutaciones. Las medidas de este cambio se volvieron a confirmar porque sus catálogos cambiaron. Revisá la implementación (oracle_factory/cli.py: archivos_de_medidas, huellas_de_catalogo, catalogos_cambiados, registrar_medidas, medidas_sin_decision, propuestas_confirmables, confirmar_medidas y las ramas de medir que dicen «Sin cambios» o registran propuestas) contra los 2 requisitos de la spec, y si tests/test_catalogo_confirmado.py prueba de verdad cada escenario; revisá también tools/verify_catalogo_confirmado.py, los catálogos factory_catalogo y el README. Mirá especialmente: caminos que registran o confirman una decisión sin la huella o con una vieja, decisiones anteriores sin huella que dejen de valer por error, medidas que desaparecen del catálogo, catálogos que no se pueden leer, y el costo de resolver el catálogo en estado. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-catalogo-confirmado && /home/workstation/Dev/factory-catalogo-confirmado/.venv/bin/python -m unittest tests.test_catalogo_confirmado tests.test_cli_piloto tests.test_modos </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
