---
generado: oracle-factory kb
id: "20261110-230858-stu-almacen-commits"
fase: "requisitos_importados"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 4a: Factory commitea en el almacén tras cada comando que escribe registros

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: requisitos_importados
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261110-230858-stu-almacen-commits/specs/flujo/spec.md](../../openspec/changes/20261110-230858-stu-almacen-commits/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c3d4de75771af14ec.con_almacen_cada_comando_que_escribe_deja_su_commit]] — sin juicio
- [[requisitos/flujo_c3d4de75771af14ec.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar]] — sin juicio

## Decisiones

- 2026-11-10 23:08 · Cambio creado · claude-code (agente)
- 2026-11-10 23:19 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-10 23:19 · Requisitos importados · claude-code (agente)
- 2026-11-10 23:27 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 23:27 · Medidas confirmadas · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `53d3845` almacen-commits: propuesta y spec (etapa 4a) (trailer)
- `07d0668` almacen-commits: spec aprobada por Brian (trailer)
- `8f8ffdd` almacen-commits: pruebas de los escenarios (antes del código), catálogos y medidas propuestas (trailer)
- `9a72af6` almacen-commits: medidas confirmadas por Brian (trailer)
- `74d8f7b` almacen-commits: Factory commitea en el almacén lo que escribió cada comando (trailer)
- `7504e5d` almacen-commits: evidencia del candidato (trailer)
- `4010151` almacen-commits: casos de las mutaciones propias (GIT\_DIR ajeno, almacén dentro de otro repo o sin repo, archivo editado dos veces, error de sistema al commitear) (trailer)
- `4537091` almacen-commits: evidencia del candidato tras las mutaciones propias (trailer)
- `618b9de` almacen-commits: lo que el almacén ignora (.factory/local/, paquetes) no entra en ningún commit (fijado por el hallazgo F1 de codex) (trailer)
- `f8260e0` almacen-commits: evidencia del candidato tras F1 (trailer)
- `7dd111d` almacen-commits: avisa de los registros que el .gitignore del almacén deja afuera, salvo lo local de Factory (hallazgo F1 de codex) (trailer)
- `5931ab0` almacen-commits: evidencia del candidato tras F1 (aviso) (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261110-230858-stu-almacen-commits`.

## Mensajes

- 2026-11-10 23:19 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-10 23:23 · claude-code: autopilot se detuvo: confirmar las medidas es sólo de una persona. Comando para una persona: oracle-factory medir 20261110-230858-stu-almacen-commits --confirmar
- 2026-11-10 23:28 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261110-230858-stu-almacen-commits --a agy
- 2026-11-10 23:44 · claude-code: autopilot se detuvo: el paso falló (código 1): La suite entera corre en segundo plano; no edito nada hasta que termine. You've hit your 5-hour limit · resets 12am (America/Argentina/Salta)
