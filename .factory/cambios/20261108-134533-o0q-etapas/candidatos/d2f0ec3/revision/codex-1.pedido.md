Sos un revisor independiente del cambio 20261108-134533-o0q-etapas de un proyecto que usa Oracle Factory: «Autonomía por etapa: construcción, integración, publicación y producción». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-autonomia-etapas/openspec/changes/20261108-134533-o0q-etapas/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-autonomia-etapas/openspec/changes/20261108-134533-o0q-etapas/specs/modos/spec.md

Qué revisar:
- Checkout del candidato d2f0ec3 (sólo lectura): /home/workstation/Dev/factory-autonomia-etapas/.factory/local/revisiones/d2f0ec3-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-autonomia-etapas/.factory/cambios/20261108-134533-o0q-etapas/candidatos/d2f0ec3/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 2 línea(s) quitada(s)
- tests/test_agentes.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-134533-o0q-etapas.md, kb/requisitos/modos_ce25b1098e45c53ae.autonomia_muestra_las_etapas_y_quien_decide_en_cada_una.md, kb/requisitos/modos_ce25b1098e45c53ae.desplegar_autorizar_respeta_la_autonomia_de_produccion.md, kb/requisitos/modos_ce25b1098e45c53ae.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona.md, kb/requisitos/modos_ce25b1098e45c53ae.solo_una_persona_cambia_la_autonomia_de_una_etapa.md, kb/requisitos/modos_ce25b1098e45c53ae.un_agente_solo_decide_en_una_etapa_autonoma.md, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-autonomia-etapas/.factory/local/revisores/d2f0ec3-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-autonomia-etapas/.factory/local/revisores/d2f0ec3-codex-1/informe.json --paquete /home/workstation/Dev/factory-autonomia-etapas/.factory/cambios/20261108-134533-o0q-etapas/candidatos/d2f0ec3/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-autonomia-etapas/.factory/local/revisiones/d2f0ec3-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Cambio de política: autonomía por etapa. .factory/config.json admite 'autonomia' con integracion, publicacion y produccion en confirmacion|autonomo (lo no declarado: confirmacion; sin la clave nada cambia). 'oracle-factory autonomia [--json]' lee; 'autonomia ETAPA MODO' lo cambia SOLO una persona (confirmación en su terminal, nunca --agente). Efecto real hoy solo en producción: con produccion=autonomo un agente puede correr 'desplegar --autorizar' (la persona sigue pudiendo; quien no es ni persona ni agente no). Plan, puerta, simulación y rollback se exigen igual. Integración y publicación no tienen comando de Factory que las aplique: queda declarada y lo dice la salida. TOCA REGLAS DE DECISIÓN (cli.py, modos.py): revisá con cuidado que un agente NO pueda darse autonomía a sí mismo ni por config, ni por un camino que no pase por la confirmación de persona, y que el cambio por defecto sea cero. DECLARO pruebas existentes tocadas: tests/test_agentes.py suma una orden de persona ('autonomia ETAPA MODO') a las que recorre; tests/datos/ayuda-cli.json regenerado (índice, desplegar, autonomia). Mutaciones propias: 12, 11 detectadas; la que sobrevive (quitar el 'if AGENTE' explícito de comando_autonomia) es equivalente porque confirmar_persona→exigir_terminal ya niega a un agente. Buscá: escritura de config no atómica o que pise otras claves, JSON de config roto, un agente que edite config.json a mano (¿lo permite la guía?), producción autónoma con un plan que debería negarse, y falsos silencios en 'autonomia --json'. Marcá bajos lo heurístico y cerrá la clase entera.
