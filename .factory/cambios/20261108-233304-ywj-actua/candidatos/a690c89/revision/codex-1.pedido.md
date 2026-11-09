Sos un revisor independiente del cambio 20261108-233304-ywj-actua de un proyecto que usa Oracle Factory: «Autopilot que actúa: corre lo mecánico, delega lo creativo, con topes y rastro». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-autopilot-actua/openspec/changes/20261108-233304-ywj-actua/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-autopilot-actua/openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato a690c89 (sólo lectura): /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisiones/a690c89-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-autopilot-actua/.factory/cambios/20261108-233304-ywj-actua/candidatos/a690c89/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-233304-ywj-actua.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo.md, tareas): 8 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisores/a690c89-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisores/a690c89-codex-1/informe.json --paquete /home/workstation/Dev/factory-autopilot-actua/.factory/cambios/20261108-233304-ywj-actua/candidatos/a690c89/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisiones/a690c89-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá el candidato a690c89 del cambio actua (capacidad flujo): el conductor autopilot ahora actúa. Spec: openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md. Producto: oracle_factory/conductor.py (nuevo: bucle, ejecutor), autopilot.argumentos_mecanicos en oracle_factory/autopilot.py, comando_autopilot en cli.py (--ejecutar, --lanzar, --max-pasos, --max-minutos), el parser y docs/modos.md. Pruebas: tests/test_conductor.py (co1–co4). Sin pruebas existentes editadas; se regenera tests/datos/ayuda-cli.json. Evidencia: 1326 pruebas OK; 36 mutaciones propias, 34 detectadas y 2 equivalentes declaradas (len(nombre) < 3 y la verificación final del subcomando en argumentos_mecanicos, ambas defensas redundantes con el parser). Mirá sobre todo, por ser la parte de más riesgo: (1) que el bucle jamás corra una decisión de persona (aprobar-spec, medir --confirmar, revisar, cerrar, abandonar, modo, autonomia, soltar, decidir-union), ni por una forma rara de escribir el comando, ni por argumentos que cambien el subcomando, ni integre/publique/despliegue; (2) el lanzamiento del agente externo con --lanzar (inyección: la instrucción va como un solo argumento y sin shell; el entorno; el plazo; qué pasa si el agente ignora FACTORY_AGENTE); (3) que el porqué se deje antes de actuar y que sin poder dejarlo no se actúe; (4) los topes (pasos, minutos, sin progreso, comando que falla) y que nunca haya un bucle infinito ni un plazo mal calculado; (5) que con datos ilegibles o frenos nunca se actúe; (6) la salida de --json y el código de salida. Dos cosas que ya sé: el plazo de un paso es lo que queda del tope de minutos con un mínimo de 1 s; y --lanzar ejecuta lo que se le pase con los permisos del usuario, por eso no se guarda en la configuración.
