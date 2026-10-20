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

- `tests/test_revisar_cancelada.py`: test_rc_antes_de_mostrar_no_queda_intento no prueba candidato existente sin informes ni evidencia — aceptado por Brian Hollweg: Acepto el riesgo: test_rc_antes_de_mostrar_no_queda_intento no prueba candidato existente sin informes ni evidencia
- `tests/test_revisar_cancelada.py`: test_rc3_una_revision_registrada_despues no prueba la no vigencia por problemas en documentos de revisión — aceptado por Brian Hollweg: Acepto el riesgo: test_rc3_una_revision_registrada_despues no prueba la no vigencia por problemas en documentos de revisión
- `oracle_factory/cli.py`: Un registro JSON válido pero con forma incorrecta puede tapar el error de la revisión — aceptado por Brian Hollweg: Acepto el riesgo: Un registro JSON válido pero con forma incorrecta puede tapar el error de la revisión

## Commits

- `accf2ec` revisar-cancelada: propuesta y spec (deducido)
- `223f201` revisar-cancelada: spec aprobada por Brian e importada (deducido)
- `3301013` revisar-cancelada: un corte de revisar después de mostrar la revisión guarda revision_cancelada con la causa y el candidato; estado y estado --json avisan hasta que se registre una revisión; pruebas rc1–rc3, k5 sigue pidiendo que no se registre ninguna decisión; docs, sensor y catálogos (deducido)
- `f789ff9` revisar-cancelada: medidas propuestas por claude-code (deducido)
- `38f3611` revisar-cancelada: medidas confirmadas por Brian (deducido)
- `27ead34` revisar-cancelada: evidencia del candidato 38f3611 (deducido)
- `22b5a78` revisar-cancelada: un fallo después de registrar la revisión (la nota del tracker) no se anota como intento cortado (agy-1, codex CXL-1); el intento se escribe sólo si el registro no cambió desde que se leyó (agy-2, CXL-2); un registro roto o de sólo lectura deja el error de la revisión y avisa que no se anotó (agy-3, CXL-3); prueba de Ctrl-C (agy-4) (deducido)
- `3eaec48` revisar-cancelada: evidencia del candidato 22b5a78 (deducido)
- `bf77a11` revisar-cancelada: el aviso dice que sigue valiendo la revisión anterior sólo si está vigente para el producto actual (codex CXL2-2); los límites del sensor ya no dicen que Ctrl-C no tiene prueba y nombran la carrera sin bloqueo del registro (agy-6, codex CXL2-1) (deducido)
- `393fb4f` revisar-cancelada: evidencia del candidato bf77a11 (deducido)
- `de3f227` revisar-cancelada: informes de la vuelta 3 (codex y agy, sólo bajas) (deducido)
- `c135a74` revisar-cancelada: revisión preparada y propuesta de claude-code (aprobar) (deducido)
- `517e125` revisar-cancelada: revisión registrada por Brian (aprobar; tres bajas aceptadas como riesgo) (deducido)
- `a3eb073` revisar-cancelada: veredicto Oracle (deducido)

## Mensajes

- Ninguno.
