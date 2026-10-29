Sos un revisor independiente del cambio 20261029-164101-xux-avisososv de un proyecto que usa Oracle Factory: «Bajar avisos OSV de las dependencias de Factory y marcar qué candidatos quedan expuestos». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-avisos-osv/openspec/changes/20261029-164101-xux-avisososv/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-avisos-osv/openspec/changes/20261029-164101-xux-avisososv/specs/procedencia/spec.md

Qué revisar:
- Checkout del candidato e9a0371 (sólo lectura): /home/workstation/Dev/factory-avisos-osv/.factory/local/revisiones/e9a0371-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-avisos-osv/.factory/cambios/20261029-164101-xux-avisososv/candidatos/e9a0371/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261029-164101-xux-avisososv.md, kb/requisitos/procedencia_c1e221f291fd3697a.la_consulta_a_osv_guarda_avisos_validos_y_audita.md, kb/requisitos/procedencia_c1e221f291fd3697a.sin_autorizacion_de_red_no_se_consulta_osv.md, kb/requisitos/procedencia_c1e221f291fd3697a.un_fallo_de_consulta_no_se_lee_como_sin_afectados.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-avisos-osv/.factory/local/revisores/e9a0371-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-avisos-osv/.factory/local/revisores/e9a0371-agy-1/informe.json --paquete /home/workstation/Dev/factory-avisos-osv/.factory/cambios/20261029-164101-xux-avisososv/candidatos/e9a0371/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-avisos-osv/.factory/local/revisiones/e9a0371-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio avisos-osv: oracle_factory/osv.py (consulta a OSV.dev con --red), su cableado en cli.py y parser.py, tests/test_avisos_osv.py y docs/procedencia.md. Buscá errores reales (seguridad: SSRF/URL, rutas, escritura; manejo de fallos; que un fallo nunca se lea como sin afectados); clasificá por severidad.
