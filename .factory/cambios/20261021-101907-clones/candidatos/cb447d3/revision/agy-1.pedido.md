Sos un revisor independiente del cambio 20261021-101907-clones de un proyecto que usa Oracle Factory: «Dos clones sin tropiezos: init versionable, IDs que no chocan y escrituras simultáneas que se reintentan». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-clones/openspec/changes/20261021-101907-clones/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-clones/openspec/changes/20261021-101907-clones/specs/colaboracion/spec.md

Qué revisar:
- Checkout del candidato cb447d3 (sólo lectura): /home/workstation/Dev/factory-clones/.factory/local/revisiones/cb447d3-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-clones/.factory/cambios/20261021-101907-clones/candidatos/cb447d3/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261021-101907-clones/candidatos/ab26db1/revision/agy-1.json
- .factory/cambios/20261021-101907-clones/candidatos/ab26db1/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261021-101907-clones.md, kb/requisitos/colaboracion_cf52b3f5822578a8a.dos_clones_no_generan_el_mismo_id.md, kb/requisitos/colaboracion_cf52b3f5822578a8a.escribir_a_la_vez_no_obliga_a_repetir.md, kb/requisitos/colaboracion_cf52b3f5822578a8a.un_clon_recien_hecho_puede_trabajar.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-clones/.factory/local/revisores/cb447d3-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-clones/.factory/local/revisores/cb447d3-agy-1/informe.json --paquete /home/workstation/Dev/factory-clones/.factory/cambios/20261021-101907-clones/candidatos/cb447d3/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-clones/.factory/local/revisiones/cb447d3-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron CLONES-01 (init avisa si Git ignora una carpeta de Factory; no pisa la regla del proyecto), CLONES-001 (prueba determinista del reintento de tomar, soltar y mensaje) y CLONES-02. Revisá el cambio: en oracle_factory/cli.py, los .gitkeep que deja inicializar, las carpetas que crea nuevo si faltan y los tres caracteres al azar antes del sufijo del ID, ArchivoCambiado (que lanza escribir_atomico) y reintentar_si_cambia en mensaje, tomar y soltar; tests/test_clones.py, los ajustes de tests/test_archivo.py y tests/test_guided.py (que contaban .gitkeep), tools/verify_clones.py y catalogos/factory_clones.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente: que el reintento vuelva a comprobar las reglas (un tomar sin --relevo que gana otro no debe pisarlo), que no reintente decisiones que no son de agregar, IDs que sigan cumpliendo ID_RE y el largo del sufijo, .gitkeep en carpetas ignoradas, y que nada itere .gitkeep como si fuera un cambio o una tarea. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-clones/.venv/bin/python -m unittest tests.test_clones </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
