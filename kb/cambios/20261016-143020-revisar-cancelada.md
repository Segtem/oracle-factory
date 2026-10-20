---
generado: oracle-factory kb
id: "20261016-143020-revisar-cancelada"
fase: "cerrada"
capacidad: "revision-guiada"
---

# estado avisa cuando una revisión no se pudo registrar y por qué

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: revision-guiada
- Responsable: nadie
- Spec: [openspec/changes/20261016-143020-revisar-cancelada/specs/revision-guiada/spec.md](../../openspec/changes/20261016-143020-revisar-cancelada/specs/revision-guiada/spec.md)

## Requisitos

- [[requisitos/revision_guiada_c804320abe8bb0c1d.un_intento_de_revision_que_no_se_registro_queda_a_la_vista]] — cumple

## Decisiones

- 2026-10-16 14:30 · Cambio creado · claude-code (agente)
- 2026-10-16 14:31 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-16 14:32 · Requisitos importados · claude-code (agente)
- 2026-10-16 14:42 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-16 16:07 · Revisión registrada · Brian Hollweg (persona) — aprobar: tres vueltas de codex y agy: la 1 marcó dos altos y cuatro medios (un fallo posterior anotado como cancelado, escrituras concurrentes, un registro roto que tapaba el error) y la 2 dos medios (el aviso daba por vigente una revisión vieja), corregidos con pruebas que fallan sobre el código anterior y mutaciones; la carrera entre comparar y reemplazar el registro es de todas las escrituras de Factory y va a una tarea aparte; la 3 sólo trae bajas
- 2026-10-16 16:07 · Juicio de Oracle · claude-code (agente)
- 2026-10-16 16:08 · Cerrado · Brian Hollweg (persona)
- 2026-10-16 16:08 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- `tests/test_revisar_cancelada.py`: test\_rc\_antes\_de\_mostrar\_no\_queda\_intento no prueba candidato existente sin informes ni evidencia — aceptado por Brian Hollweg: Acepto el riesgo: test\_rc\_antes\_de\_mostrar\_no\_queda\_intento no prueba candidato existente sin informes ni evidencia
- `tests/test_revisar_cancelada.py`: test\_rc3\_una\_revision\_registrada\_despues no prueba la no vigencia por problemas en documentos de revisión — aceptado por Brian Hollweg: Acepto el riesgo: test\_rc3\_una\_revision\_registrada\_despues no prueba la no vigencia por problemas en documentos de revisión
- `oracle_factory/cli.py`: Un registro JSON válido pero con forma incorrecta puede tapar el error de la revisión — aceptado por Brian Hollweg: Acepto el riesgo: Un registro JSON válido pero con forma incorrecta puede tapar el error de la revisión

## Commits

- `38f3611` revisar-cancelada: medidas confirmadas por Brian (deducido)
- `22b5a78` revisar-cancelada: un fallo después de registrar la revisión (la nota del tracker) no se anota como intento cortado (agy-1, codex CXL-1); el intento se escribe sólo si el registro no cambió desde que se leyó (agy-2, CXL-2); un registro roto o de sólo lectura deja el error de la revisión y avisa que no se anotó (agy-3, CXL-3); prueba de Ctrl-C (agy-4) (deducido)
- `bf77a11` revisar-cancelada: el aviso dice que sigue valiendo la revisión anterior sólo si está vigente para el producto actual (codex CXL2-2); los límites del sensor ya no dicen que Ctrl-C no tiene prueba y nombran la carrera sin bloqueo del registro (agy-6, codex CXL2-1) (deducido)
- Todos, también los que se deducen al integrarlo: `oracle-factory log 20261016-143020-revisar-cancelada`.

## Mensajes

- Ninguno.
