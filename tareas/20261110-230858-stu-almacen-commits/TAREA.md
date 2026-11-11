# Registros fuera del repo del producto, etapa 4a: Factory commitea en el almacén tras cada comando que escribe registros

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-10 23:08:58 UTC)

OpenSpec: openspec/changes/20261110-230858-stu-almacen-commits. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-10 23:19:27 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261110-230858-stu-almacen-commits/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-10 23:19:41 UTC)

Requisitos importados: flujo_c3d4de75771af14ec.con_almacen_cada_comando_que_escribe_deja_su_commit (funcional), flujo_c3d4de75771af14ec.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-10 23:22:40 UTC)

Medidas de flujo_c3d4de75771af14ec.con_almacen_cada_comando_que_escribe_deja_su_commit: factory_almacen_commits.con_almacen_cada_comando_que_escribe_deja_su_commit, factory_almacen_commits.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 23:22:43 UTC)

Medidas de flujo_c3d4de75771af14ec.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar: factory_almacen_commits.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar, factory_almacen_commits.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 23:27:56 UTC)

Medidas de flujo_c3d4de75771af14ec.con_almacen_cada_comando_que_escribe_deja_su_commit: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 23:27:56 UTC)

Medidas de flujo_c3d4de75771af14ec.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 11:27:25 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 4a de «registros fuera del repo del producto»: Factory commitea en el almacén lo que escribió cada comando. Candidato 758f789 (camino completo): evidencia verde (1409 pruebas, 10 casos de contrato). QUIÉN LO HIZO: un agente lanzado por el conductor escribió las pruebas e implementó (almacenes.foto/commitear: foto de lo cambiado antes del comando y commit de lo que cambió después, con git add/commit por pathspec desde stdin; mensaje con Cambio/Comando/Actor; limpia GIT_DIR y afines; no escribe configuración de Git; no sube nada; si git falla avisa y no falla) y se quedó sin cuota antes de la evidencia; la evidencia, las mutaciones (33, reales detectadas; equivalentes declaradas: pathspecs literales, --only implícito de git commit con rutas, sin repo y sin almacén salen solos, y la guarda de una foto previa fallida si git se recupera a mitad de comando) y las correcciones las hice yo. REVISIÓN: sólo codex, 5 rondas, todas sobre QUÉ ARCHIVOS ENTRAN EN EL COMMIT: ignorados por el .gitignore del almacén (no entran, Factory AVISA salvo lo local), lo local de cada máquina (.factory/local/ y paquetes clue/: no entra NUNCA, aunque esté versionado), el bit de ejecución (cuenta) y una falla de git al sacar la foto (se avisa). DECIDE BRIAN: (1) F2 de la ronda 1, riesgo a aceptar: sin --agente y sin terminal el pie dice «Actor: sin identificar (sin_identificar)», fuera del persona|agente que promete la spec; inventar uno de los dos mentiría en el registro; la redacción de la spec se corrige en otro cambio. (2) F1 de la ronda 5, riesgo a aceptar para 4a: dos comandos de Factory A LA VEZ sobre el mismo almacén (dos worktrees, o un agente y una persona) pueden mezclar sus archivos en un solo commit y el otro avisa del index.lock; no se pierde nada; arreglarlo necesita un bloqueo entre comandos, que ya estaba en el plan de la 4b. (3) Apartado de la spec, ya dicho: lo que el .gitignore del almacén ignora no se commitea (manda el almacén) y se avisa. (4) Límite declarado en el código: un archivo editado a mano que el comando vuelve a cambiar entra entero. (5) Costo: con --untracked-files=all Git enumera también .factory/local en cada comando (sólo se hashea lo no local). (6) Ya existía antes: init del modo normal escribe los drivers de unión en la configuración de Git del repo; en el almacén ya no. Camino completo con un solo proveedor revisor (agy sin cuota). No edité ninguna prueba existente.); 0 abiertos derivados; commit 7e70be88a0d5b8e9a8ed5a59dcab75063a0a8da1; informe tareas/20261110-230858-stu-almacen-commits/revisiones/registro-wbkns3vi/informe.json; decisiones tareas/20261110-230858-stu-almacen-commits/revisiones/registro-wbkns3vi/decisiones.json.

### Nota (2026-11-11 11:27:51 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261110-230858-stu-almacen-commits/oracle-veredicto.txt.

### Nota (2026-11-11 11:28:26 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
