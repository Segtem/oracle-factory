Sos un revisor independiente del cambio 20261028-235529-lhi-uvlock de un proyecto que usa Oracle Factory: «Rastrear el uv.lock de Factory y no dar por no confiable un paquete que el entorno no instala». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-uv-lock/openspec/changes/20261028-235529-lhi-uvlock/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-uv-lock/openspec/changes/20261028-235529-lhi-uvlock/specs/procedencia/spec.md

Qué revisar:
- Checkout del candidato 7ae0c36 (sólo lectura): /home/workstation/Dev/factory-uv-lock/.factory/local/revisiones/7ae0c36-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-uv-lock/.factory/cambios/20261028-235529-lhi-uvlock/candidatos/7ae0c36/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261028-235529-lhi-uvlock.md, kb/requisitos/procedencia_cadae59b33b0c0b2c.el_lock_de_factory_coincide_con_su_pyproject.md, kb/requisitos/procedencia_cadae59b33b0c0b2c.el_lock_de_factory_viaja_con_el_repositorio.md, kb/requisitos/procedencia_cadae59b33b0c0b2c.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-uv-lock/.factory/local/revisores/7ae0c36-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-uv-lock/.factory/local/revisores/7ae0c36-agy-1/informe.json --paquete /home/workstation/Dev/factory-uv-lock/.factory/cambios/20261028-235529-lhi-uvlock/candidatos/7ae0c36/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-uv-lock/.factory/local/revisiones/7ae0c36-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio uv-lock: uv.lock versionado, propiedad factory:instalado en procedencia.py, tests/test_uv_lock.py y docs. Buscá errores reales; clasificá por severidad.
