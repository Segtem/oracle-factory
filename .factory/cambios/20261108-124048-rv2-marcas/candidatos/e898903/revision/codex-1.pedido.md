Sos un revisor independiente del cambio 20261108-124048-rv2-marcas de un proyecto que usa Oracle Factory: «El comprobador del sitio detecta bloques marcados duplicados». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-marcadores-duplicados/openspec/changes/20261108-124048-rv2-marcas/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-marcadores-duplicados/openspec/changes/20261108-124048-rv2-marcas/specs/web/spec.md

Qué revisar:
- Checkout del candidato e898903 (sólo lectura): /home/workstation/Dev/factory-marcadores-duplicados/.factory/local/revisiones/e898903-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-marcadores-duplicados/.factory/cambios/20261108-124048-rv2-marcas/candidatos/e898903/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-124048-rv2-marcas.md, kb/requisitos/web_c5280d3ce46f7827d.el_comprobador_del_sitio_rechaza_un_bloque_marcado_duplicado.md, tareas): 5 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-marcadores-duplicados/.factory/local/revisores/e898903-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-marcadores-duplicados/.factory/local/revisores/e898903-codex-1/informe.json --paquete /home/workstation/Dev/factory-marcadores-duplicados/.factory/cambios/20261108-124048-rv2-marcas/candidatos/e898903/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-marcadores-duplicados/.factory/local/revisiones/e898903-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Cambio chico (WPG-007): tools/sitio_paginas.py problemas() ahora rechaza que los marcadores de un bloque generado (menu, pie, leer, ruta) aparezcan más de una vez (apertura o cierre repetidos), nombrando página y bloque; antes sólo se comparaba la primera pareja. Pruebas nuevas en tests/test_marcas.py; no edité pruebas existentes. Mutaciones propias: 6 sobre el control (umbral, cierre, cada bloque), las 6 detectadas. Buscá: marcadores con otro espaciado o mayúsculas que el escritor no genera pero el comprobador no ve, falsos avisos en el sitio real, y otra forma de duplicar un bloque sin marcadores iguales. Marcá bajos lo heurístico y cerrá la clase entera.
