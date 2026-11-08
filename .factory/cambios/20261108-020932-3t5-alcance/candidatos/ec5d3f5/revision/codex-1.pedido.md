Sos un revisor independiente del cambio 20261108-020932-3t5-alcance de un proyecto que usa Oracle Factory: «Alcance opcional de los destinos: desplegar sólo lo que cambió». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-destinos-alcance/openspec/changes/20261108-020932-3t5-alcance/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-destinos-alcance/openspec/changes/20261108-020932-3t5-alcance/specs/despliegue/spec.md

Qué revisar:
- Checkout del candidato ec5d3f5 (sólo lectura): /home/workstation/Dev/factory-destinos-alcance/.factory/local/revisiones/ec5d3f5-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-destinos-alcance/.factory/cambios/20261108-020932-3t5-alcance/candidatos/ec5d3f5/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 2 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-020932-3t5-alcance.md, kb/requisitos/despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados.md, kb/requisitos/despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada.md, kb/requisitos/despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance.md, kb/requisitos/despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-destinos-alcance/.factory/local/revisores/ec5d3f5-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-destinos-alcance/.factory/local/revisores/ec5d3f5-codex-1/informe.json --paquete /home/workstation/Dev/factory-destinos-alcance/.factory/cambios/20261108-020932-3t5-alcance/candidatos/ec5d3f5/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-destinos-alcance/.factory/local/revisiones/ec5d3f5-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá el alcance opcional de los destinos y 'desplegar --cambios' (oracle_factory/despliegue.py: _destino, _version_previa, elegir_por_cambios, armar_plan, texto_plan, registros; cli.py comando_desplegar; parser.py; docs/despliegue.md y docs/plantillas/destinos.json). Fijate en: (1) falsos silencios: un destino omitido que debería desplegarse (versión previa de otra rama, rollback, renombrados/borrados dentro del alcance, patrones de pathspec como '*.html' o rutas con espacios), (2) la versión previa tomada de la última corrida 'desplegado'/'probado' y si un destino 'fallido'/'revertido' puede quedar mal clasificado, (3) arrastre de depende_de, (4) que sin --cambios nada cambie y que --cambios no ejecute nada si no hay destinos, (5) el cambio en despliegue.registros (desempate por mtime) y si afecta a estados. Mutaciones propias probadas: nunca desplegado ignorado, lista vacía aceptada, sin arrastre, sin alcance omitido, orden de registros viejo, versión previa desconocida, ejecuta sin nada, combina --cambios y --destino. Equivalente (no detectable): invertir el rango del diff, porque --name-only es simétrico.
