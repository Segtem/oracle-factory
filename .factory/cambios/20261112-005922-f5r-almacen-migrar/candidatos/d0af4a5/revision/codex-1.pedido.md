Sos un revisor independiente del cambio 20261112-005922-f5r-almacen-migrar de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 6: migrar los registros de un proyecto a un almacén». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-migrar/openspec/changes/20261112-005922-f5r-almacen-migrar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-migrar/openspec/changes/20261112-005922-f5r-almacen-migrar/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato d0af4a5 (sólo lectura): /home/workstation/Dev/factory-almacen-migrar/.factory/local/revisiones/d0af4a5-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-migrar/.factory/cambios/20261112-005922-f5r-almacen-migrar/candidatos/d0af4a5/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261112-005922-f5r-almacen-migrar/candidatos/7c8cdcd/revision/codex-1.json
- .factory/cambios/20261112-005922-f5r-almacen-migrar/candidatos/de026c8/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
- tests/test_almacen_vscode.py, modificado: 2 línea(s) quitada(s)
- tests/vscode_en_node.cjs, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261112-005922-f5r-almacen-migrar.md, kb/requisitos/flujo_c3b7c8e521b99f547.el_ensayo_sobre_una_copia.md, kb/requisitos/flujo_c3b7c8e521b99f547.migrar_al_almacen_copia_conecta_y_deja_la_baja.md, kb/requisitos/flujo_c3b7c8e521b99f547.migrar_al_almacen_se_niega_sin_tocar_nada.md, kb/requisitos/flujo_c3b7c8e521b99f547.migrar_verificar_no_escribe.md, tareas): 20 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-migrar/.factory/local/revisores/d0af4a5-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-migrar/.factory/local/revisores/d0af4a5-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-migrar/.factory/cambios/20261112-005922-f5r-almacen-migrar/candidatos/d0af4a5/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-migrar/.factory/local/revisiones/d0af4a5-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Tercera vuelta. MIG-003 y MIG-004 se arreglaron en d0af4a59 (diff contra de026c8): el bloqueo se toma antes de copiar, cualquier falla de copia o commit deshace la copia, el .gitignore y el índice del almacén, y --verificar con una URL sin clon la comprueba en un clon superficial temporal. Revisá la clase entera: ningún paso de migrar, ni --verificar, deja algo a medias o dice éxito en falso. Siguen valiendo los avisos sobre tests/terminal_en_node.cjs y tests/vscode_en_node.cjs (ayudantes existentes editados).
