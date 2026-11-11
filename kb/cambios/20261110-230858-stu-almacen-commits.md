---
generado: oracle-factory kb
id: "20261110-230858-stu-almacen-commits"
fase: "oracle_verde"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 4a: Factory commitea en el almacén tras cada comando que escribe registros

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: oracle_verde
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261110-230858-stu-almacen-commits/specs/flujo/spec.md](../../openspec/changes/20261110-230858-stu-almacen-commits/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c3d4de75771af14ec.con_almacen_cada_comando_que_escribe_deja_su_commit]] — cumple
- [[requisitos/flujo_c3d4de75771af14ec.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar]] — cumple

## Decisiones

- 2026-11-10 23:08 · Cambio creado · claude-code (agente)
- 2026-11-10 23:19 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-10 23:19 · Requisitos importados · claude-code (agente)
- 2026-11-10 23:27 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 23:27 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-11 11:27 · Revisión registrada · Brian Hollweg (persona) — aprobar: Propuesta del agente claude-code. Etapa 4a de «registros fuera del repo del producto»: Factory commitea en el almacén lo que escribió cada comando. Candidato 758f789 (camino completo): evidencia verde (1409 pruebas, 10 casos de contrato). QUIÉN LO HIZO: un agente lanzado por el conductor escribió las pruebas e implementó (almacenes.foto/commitear: foto de lo cambiado antes del comando y commit de lo que cambió después, con git add/commit por pathspec desde stdin; mensaje con Cambio/Comando/Actor; limpia GIT\_DIR y afines; no escribe configuración de Git; no sube nada; si git falla avisa y no falla) y se quedó sin cuota antes de la evidencia; la evidencia, las mutaciones (33, reales detectadas; equivalentes declaradas: pathspecs literales, --only implícito de git commit con rutas, sin repo y sin almacén salen solos, y la guarda de una foto previa fallida si git se recupera a mitad de comando) y las correcciones las hice yo. REVISIÓN: sólo codex, 5 rondas, todas sobre QUÉ ARCHIVOS ENTRAN EN EL COMMIT: ignorados por el .gitignore del almacén (no entran, Factory AVISA salvo lo local), lo local de cada máquina (.factory/local/ y paquetes clue/: no entra NUNCA, aunque esté versionado), el bit de ejecución (cuenta) y una falla de git al sacar la foto (se avisa). DECIDE BRIAN: (1) F2 de la ronda 1, riesgo a aceptar: sin --agente y sin terminal el pie dice «Actor: sin identificar (sin\_identificar)», fuera del persona\|agente que promete la spec; inventar uno de los dos mentiría en el registro; la redacción de la spec se corrige en otro cambio. (2) F1 de la ronda 5, riesgo a aceptar para 4a: dos comandos de Factory A LA VEZ sobre el mismo almacén (dos worktrees, o un agente y una persona) pueden mezclar sus archivos en un solo commit y el otro avisa del index.lock; no se pierde nada; arreglarlo necesita un bloqueo entre comandos, que ya estaba en el plan de la 4b. (3) Apartado de la spec, ya dicho: lo que el .gitignore del almacén ignora no se commitea (manda el almacén) y se avisa. (4) Límite declarado en el código: un archivo editado a mano que el comando vuelve a cambiar entra entero. (5) Costo: con --untracked-files=all Git enumera también .factory/local en cada comando (sólo se hashea lo no local). (6) Ya existía antes: init del modo normal escribe los drivers de unión en la configuración de Git del repo; en el almacén ya no. Camino completo con un solo proveedor revisor (agy sin cuota). No edité ninguna prueba existente.
- 2026-11-11 11:27 · Juicio de Oracle · claude-code (agente)

## Riesgos aceptados

- `oracle_factory/cli.py`: Comandos concurrentes pueden compartir el commit y dejar uno sin commit — aceptado por Brian Hollweg: Acepto el riesgo: Comandos concurrentes pueden compartir el commit y dejar uno sin commit

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
- `57017da` almacen-commits: lo local de cada máquina no entra nunca, aunque esté versionado (hallazgo F1 de codex, ronda 3) (trailer)
- `f31b46b` almacen-commits: evidencia del candidato tras F1 (local versionado) (trailer)
- `758f789` almacen-commits: el modo de los archivos cuenta en la foto y una falla de git al sacarla se avisa (hallazgos F1 y F2 de codex, ronda 4) (trailer)
- `0b4caff` almacen-commits: evidencia del candidato tras la ronda 4 (trailer)
- `61148e3` almacen-commits: informe de codex (ronda 5) (trailer)
- `7e70be8` almacen-commits: propuesta de revisión (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261110-230858-stu-almacen-commits`.

## Mensajes

- 2026-11-10 23:19 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-10 23:23 · claude-code: autopilot se detuvo: confirmar las medidas es sólo de una persona. Comando para una persona: oracle-factory medir 20261110-230858-stu-almacen-commits --confirmar
- 2026-11-10 23:28 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261110-230858-stu-almacen-commits --a agy
- 2026-11-10 23:44 · claude-code: autopilot se detuvo: el paso falló (código 1): La suite entera corre en segundo plano; no edito nada hasta que termine. You've hit your 5-hour limit · resets 12am (America/Argentina/Salta)
