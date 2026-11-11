# Registros fuera del repo del producto, etapa 4b1: cada comando commitea sólo lo de su cambio, con un bloqueo corto

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-11 11:46:16 UTC)

OpenSpec: openspec/changes/20261111-114616-81f-almacen-bloqueo. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-11 11:47:58 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261111-114616-81f-almacen-bloqueo/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-11 11:49:35 UTC)

Requisitos importados: flujo_cd33948e0810e1545.con_almacen_cada_comando_commitea_solo_lo_de_su_cambio (funcional), flujo_cd33948e0810e1545.el_commit_del_almacen_se_hace_con_un_bloqueo_corto (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-11 11:55:39 UTC)

Medidas de flujo_cd33948e0810e1545.con_almacen_cada_comando_commitea_solo_lo_de_su_cambio: factory_almacen_bloqueo.con_almacen_cada_comando_commitea_solo_lo_de_su_cambio, factory_almacen_bloqueo.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 11:55:41 UTC)

Medidas de flujo_cd33948e0810e1545.el_commit_del_almacen_se_hace_con_un_bloqueo_corto: factory_almacen_bloqueo.el_commit_del_almacen_se_hace_con_un_bloqueo_corto, factory_almacen_bloqueo.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 11:56:45 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261111-114616-81f-almacen-bloqueo/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-11 12:00:20 UTC)

Requisitos importados: flujo_cd33948e0810e1545.con_almacen_cada_comando_commitea_solo_lo_de_su_cambio (funcional), flujo_cd33948e0810e1545.el_commit_del_almacen_se_hace_con_un_bloqueo_corto (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-11 12:01:12 UTC)

Medidas de flujo_cd33948e0810e1545.con_almacen_cada_comando_commitea_solo_lo_de_su_cambio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 12:01:13 UTC)

Medidas de flujo_cd33948e0810e1545.el_commit_del_almacen_se_hace_con_un_bloqueo_corto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 13:15:10 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 4b1 de «registros fuera del repo del producto»: cada comando commitea sólo lo de su cambio, con un bloqueo corto. Candidato a1c3b35 (camino completo): evidencia verde (1416 pruebas, 7 casos de contrato), corrida SIN FACTORY_AGENTE en el entorno (ver abajo). QUIÉN LO HIZO: un agente lanzado por el conductor escribió las 7 pruebas e implementó en almacenes.py (_cambio_de clasifica cada ruta por cambio; con cambio entra lo suyo y lo común, y lo de otro cambio queda para el comando de ese cambio; bloqueo() es un flock exclusivo sólo durante foto final, add y commit, con 30 s de plazo y aviso si no se consigue); yo corregí una ayuda de la prueba que leía mal git status (le comía el punto de .factory), hice las mutaciones (17; reales detectadas; equivalente: soltar el flock explícitamente, porque cerrar el archivo ya lo suelta) y pedí las revisiones. REVISIÓN: sólo codex, 2 rondas: H-01 (medio: el bloqueo quedaba separado entre worktrees del almacén) corregido: el archivo del bloqueo vive en la carpeta común de Git, con prueba; ronda 2 sin hallazgos. QUÉ TENÉS QUE SABER: (1) para que lo de B quede para el comando de B, LO PENDIENTE DEL PROPIO CAMBIO ENTRA AUNQUE YA ESTUVIERA EDITADO ANTES del comando: afloja la regla de la 4a para los archivos del propio cambio (una edición a mano en un archivo del cambio A la commitea el próximo comando de A). (2) Límite declarado: dos comandos sobre el MISMO cambio a la vez pueden compartir archivos en un commit. (3) Encontré la causa de los errores de test_guided que aparecían en la etapa 3 y en esta evidencia del agente: con FACTORY_AGENTE puesto (como lo tiene el agente lanzado), una prueba anterior llama a f.main sin --agente y deja cli.AGENTE puesto, y test_guided aprueba la spec «como agente»; lo reproduje; es de la suite, no de este cambio: queda para otro cambio, y esta evidencia la corrí sin esa variable. Camino completo con un solo proveedor revisor (agy sin cuota). No edité ninguna prueba existente.); 0 abiertos derivados; commit dc765c5c0d57b59772836942d3fa6bb4f96b24d8; informe tareas/20261111-114616-81f-almacen-bloqueo/revisiones/registro-phw2auz3/informe.json; decisiones tareas/20261111-114616-81f-almacen-bloqueo/revisiones/registro-phw2auz3/decisiones.json.

### Nota (2026-11-11 13:16:04 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261111-114616-81f-almacen-bloqueo/oracle-veredicto.txt.

### Nota (2026-11-11 13:37:29 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
