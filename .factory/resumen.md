<!-- oracle-factory resumen sha256:eff0a64f5959848634704cf7726abbc8864a6903d4aa93e9a6185953bc439af4 -->
# Estado actual

Generado por `oracle-factory resumen` a partir de los registros; no se edita a mano. `oracle-factory resumen --verificar` dice si quedó viejo.

12 capacidades · 82 requisitos vigentes · 6 cambios abiertos

## Lo vigente

El veredicto es el registrado al cerrar el cambio de origen, no una corrida nueva de Oracle sobre todo el sistema.

### archivo

Spec completa: [openspec/specs/archivo/spec.md](../openspec/specs/archivo/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| la spec de un cambio se fusiona al cerrarlo | funcional | `archivo_cbf6802991c3ba673.la_spec_de_un_cambio_se_fusiona_al_cerrarlo` | factory_archivo.la_spec_de_un_cambio_se_fusiona_al_cerrarlo, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |
| un conflicto impide cerrar | funcional | `archivo_cbf6802991c3ba673.un_conflicto_impide_cerrar` | factory_archivo.un_conflicto_impide_cerrar, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |
| lo cerrado no se mueve ni se reescribe | no funcional | `archivo_cbf6802991c3ba673.lo_cerrado_no_se_mueve_ni_se_reescribe` | factory_archivo.lo_cerrado_no_se_mueve_ni_se_reescribe, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |
| se distingue lo vigente de lo reemplazado | funcional | `archivo_cbf6802991c3ba673.se_distingue_lo_vigente_de_lo_reemplazado` | factory_archivo.se_distingue_lo_vigente_de_lo_reemplazado, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |
| una capacidad con un solo nombre | funcional | `archivo_cbf6802991c3ba673.una_capacidad_con_un_solo_nombre` | factory_archivo.una_capacidad_con_un_solo_nombre, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |
| este repositorio queda archivado | no funcional | `archivo_cbf6802991c3ba673.este_repositorio_queda_archivado` | factory_archivo.este_repositorio_queda_archivado, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |
| los comandos de lectura muestran el archivo | funcional | `archivo_cbf6802991c3ba673.los_comandos_de_lectura_muestran_el_archivo` | factory_archivo.los_comandos_de_lectura_muestran_el_archivo, factory_archivo.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-161029-archivar-al |

### autoproduccion

Spec completa: [openspec/specs/autoproduccion/spec.md](../openspec/specs/autoproduccion/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| juzgar encuentra la evidencia del candidato | funcional | `autoproduccion_c73955279aeb460eb.juzgar_encuentra_la_evidencia_del_candidato` | factory_autoproduccion.juzgar_encuentra_la_evidencia_del_candidato, factory_autoproduccion.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-150043-autoproduccion |
| revision-preparar arma el informe desde los revisores | funcional | `autoproduccion_c73955279aeb460eb.revision_preparar_arma_el_informe_desde_los_revisores` | factory_autoproduccion.revision_preparar_arma_el_informe_desde_los_revisores, factory_autoproduccion.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-150043-autoproduccion |
| el borrador de decisiones no decide | funcional | `autoproduccion_c73955279aeb460eb.el_borrador_de_decisiones_no_decide` | factory_autoproduccion.el_borrador_de_decisiones_no_decide, factory_autoproduccion.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-150043-autoproduccion |
| los informes se validan o se marcan | funcional | `autoproduccion_c73955279aeb460eb.los_informes_se_validan_o_se_marcan` | factory_autoproduccion.los_informes_se_validan_o_se_marcan, factory_autoproduccion.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-150043-autoproduccion |
| este repositorio produce en la carpeta del candidato | no funcional | `autoproduccion_c73955279aeb460eb.este_repositorio_produce_en_la_carpeta_del_candidato` | factory_autoproduccion.este_repositorio_produce_en_la_carpeta_del_candidato, factory_autoproduccion.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-150043-autoproduccion |

### decisiones

Spec completa: [openspec/specs/decisiones/spec.md](../openspec/specs/decisiones/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| las confirmaciones son un menú | funcional | `decisiones_c59754a250f5b3593.las_confirmaciones_son_un_menu` | factory_decisiones.las_confirmaciones_son_un_menu, factory_decisiones.corrida_completa | verde al cerrar el 2026-10-08 | 20261007-223645-decisiones-guiadas |
| revisar guía la revisión de punta a punta | funcional | `decisiones_c59754a250f5b3593.revisar_guia_la_revision_de_punta_a_punta` | factory_decisiones.revisar_guia_la_revision_de_punta_a_punta, factory_decisiones.corrida_completa | verde al cerrar el 2026-10-08 | 20261007-223645-decisiones-guiadas |
| el motivo se elige | funcional | `decisiones_c59754a250f5b3593.el_motivo_se_elige` | factory_decisiones.el_motivo_se_elige, factory_decisiones.corrida_completa | verde al cerrar el 2026-10-08 | 20261007-223645-decisiones-guiadas |
| confirmar las medidas propuestas de una vez | funcional | `decisiones_c59754a250f5b3593.confirmar_las_medidas_propuestas_de_una_vez` | factory_decisiones.confirmar_las_medidas_propuestas_de_una_vez, factory_decisiones.corrida_completa | verde al cerrar el 2026-10-08 | 20261007-223645-decisiones-guiadas |
| sin terminal no hay decisión de persona | no funcional | `decisiones_c59754a250f5b3593.sin_terminal_no_hay_decision_de_persona` | factory_decisiones.sin_terminal_no_hay_decision_de_persona, factory_decisiones.corrida_completa | verde al cerrar el 2026-10-08 | 20261007-223645-decisiones-guiadas |

### estructura

Spec completa: [openspec/specs/estructura/spec.md](../openspec/specs/estructura/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| estructura documentada | funcional | `estructura_cd7e5b6c4f15e5d8b.estructura_documentada` | factory_estructura.estructura_documentada, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| carpeta propia de Factory | funcional | `estructura_cd7e5b6c4f15e5d8b.carpeta_propia_de_factory` | factory_estructura.carpeta_propia_de_factory, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| descubrir la raíz del proyecto | funcional | `estructura_cd7e5b6c4f15e5d8b.descubrir_la_raiz_del_proyecto` | factory_estructura.descubrir_la_raiz_del_proyecto, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| lo versionado y lo local | no funcional | `estructura_cd7e5b6c4f15e5d8b.lo_versionado_y_lo_local` | factory_estructura.lo_versionado_y_lo_local, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| la huella del producto excluye lo que Factory produce | funcional | `estructura_cd7e5b6c4f15e5d8b.la_huella_del_producto_excluye_lo_que_factory_produce` | factory_estructura.la_huella_del_producto_excluye_lo_que_factory_produce, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| donde esta cada artefacto | funcional | `estructura_cd7e5b6c4f15e5d8b.donde_esta_cada_artefacto` | factory_estructura.donde_esta_cada_artefacto, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| ruta canonica para producir artefactos | funcional | `estructura_cd7e5b6c4f15e5d8b.ruta_canonica_para_producir_artefactos` | factory_estructura.ruta_canonica_para_producir_artefactos, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| buscar en todo el proyecto | funcional | `estructura_cd7e5b6c4f15e5d8b.buscar_en_todo_el_proyecto` | factory_estructura.buscar_en_todo_el_proyecto, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| listar con filtros | funcional | `estructura_cd7e5b6c4f15e5d8b.listar_con_filtros` | factory_estructura.listar_con_filtros, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| respetar lo existente | no funcional | `estructura_cd7e5b6c4f15e5d8b.respetar_lo_existente` | factory_estructura.respetar_lo_existente, factory_estructura.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-132144-jerarquia-de |
| el estado de un cambio nuevo vive en .factory | funcional | `estructura2_c1bed25594460b383.el_estado_de_un_cambio_nuevo_vive_en_factory` | factory_estructura2.el_estado_de_un_cambio_nuevo_vive_en_factory, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| un proyecto no migrado sigue funcionando | funcional | `estructura2_c1bed25594460b383.un_proyecto_no_migrado_sigue_funcionando` | factory_estructura2.un_proyecto_no_migrado_sigue_funcionando, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| migrar mueve el estado sin cambiar su contenido | funcional | `estructura2_c1bed25594460b383.migrar_mueve_el_estado_sin_cambiar_su_contenido` | factory_estructura2.migrar_mueve_el_estado_sin_cambiar_su_contenido, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| migrar no pierde ni pisa nada | funcional | `estructura2_c1bed25594460b383.migrar_no_pierde_ni_pisa_nada` | factory_estructura2.migrar_no_pierde_ni_pisa_nada, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| la migración conserva el significado | no funcional | `estructura2_c1bed25594460b383.la_migracion_conserva_el_significado` | factory_estructura2.la_migracion_conserva_el_significado, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| la configuración del proyecto vive en .factory | funcional | `estructura2_c1bed25594460b383.la_configuracion_del_proyecto_vive_en_factory` | factory_estructura2.la_configuracion_del_proyecto_vive_en_factory, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| los comandos de lectura entienden los dos lugares | funcional | `estructura2_c1bed25594460b383.los_comandos_de_lectura_entienden_los_dos_lugares` | factory_estructura2.los_comandos_de_lectura_entienden_los_dos_lugares, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |
| este repositorio queda migrado y verificado | no funcional | `estructura2_c1bed25594460b383.este_repositorio_queda_migrado_y_verificado` | factory_estructura2.este_repositorio_queda_migrado_y_verificado, factory_estructura2.corrida_completa | verde al cerrar el 2026-10-06 | 20261006-004456-fase-2-de-la |

### limpieza

Spec completa: [openspec/specs/limpieza/spec.md](../openspec/specs/limpieza/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| los registros no llevan la ruta privada | funcional | `limpieza_c6ac32e7f17eb48b5.los_registros_no_llevan_la_ruta_privada` | factory_limpieza.los_registros_no_llevan_la_ruta_privada, factory_limpieza.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-193914-quitar-la-ruta |
| las decisiones conservan su integridad | funcional | `limpieza_c6ac32e7f17eb48b5.las_decisiones_conservan_su_integridad` | factory_limpieza.las_decisiones_conservan_su_integridad, factory_limpieza.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-193914-quitar-la-ruta |
| la evidencia no se reescribe | no funcional | `limpieza_c6ac32e7f17eb48b5.la_evidencia_no_se_reescribe` | factory_limpieza.la_evidencia_no_se_reescribe, factory_limpieza.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-193914-quitar-la-ruta |
| limpieza repetible y verificable | no funcional | `limpieza_c6ac32e7f17eb48b5.limpieza_repetible_y_verificable` | factory_limpieza.limpieza_repetible_y_verificable, factory_limpieza.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-193914-quitar-la-ruta |

### modos

Spec completa: [openspec/specs/modos/spec.md](../openspec/specs/modos/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| modo explicito por cambio | funcional | `modos_c45a4802846932222.modo_explicito_por_cambio` | factory_modos.modo_explicito_por_cambio, factory_modos.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-105331-modos-de-trabajo |
| tipo de requisito | funcional | `modos_c45a4802846932222.tipo_de_requisito` | factory_modos.tipo_de_requisito, factory_modos.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-105331-modos-de-trabajo |
| decisiones segun el modo | funcional | `modos_c45a4802846932222.decisiones_segun_el_modo` | factory_modos.decisiones_segun_el_modo, factory_modos.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-105331-modos-de-trabajo |
| actor registrado sin aparentar humanos | funcional | `modos_c45a4802846932222.actor_registrado_sin_aparentar_humanos` | factory_modos.actor_registrado_sin_aparentar_humanos, factory_modos.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-105331-modos-de-trabajo |
| cambio de modo con invalidacion | funcional | `modos_c45a4802846932222.cambio_de_modo_con_invalidacion` | factory_modos.cambio_de_modo_con_invalidacion, factory_modos.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-105331-modos-de-trabajo |

### portabilidad

Spec completa: [openspec/specs/portabilidad/spec.md](../openspec/specs/portabilidad/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| hechos con ruta relativa al proyecto | funcional | `portabilidad_cbe858e976e618573.hechos_con_ruta_relativa_al_proyecto` | factory_portabilidad.hechos_con_ruta_relativa_al_proyecto, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |
| advertir cuando los hechos no viajan | funcional | `portabilidad_cbe858e976e618573.advertir_cuando_los_hechos_no_viajan` | factory_portabilidad.advertir_cuando_los_hechos_no_viajan, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |
| fuente de los requisitos relativa | funcional | `portabilidad_cbe858e976e618573.fuente_de_los_requisitos_relativa` | factory_portabilidad.fuente_de_los_requisitos_relativa, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |
| pendiente que explica cómo recuperarse | funcional | `portabilidad_cbe858e976e618573.pendiente_que_explica_como_recuperarse` | factory_portabilidad.pendiente_que_explica_como_recuperarse, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |
| un cambio juzgado en una máquina se cierra desde otra | funcional | `portabilidad_cbe858e976e618573.un_cambio_juzgado_en_una_maquina_se_cierra_desde_otra` | factory_portabilidad.un_cambio_juzgado_en_una_maquina_se_cierra_desde_otra, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |
| sin rutas privadas en lo versionado | no funcional | `portabilidad_cbe858e976e618573.sin_rutas_privadas_en_lo_versionado` | factory_portabilidad.sin_rutas_privadas_en_lo_versionado, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |
| respetar los registros existentes | no funcional | `portabilidad_cbe858e976e618573.respetar_los_registros_existentes` | factory_portabilidad.respetar_los_registros_existentes, factory_portabilidad.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-184427-los-registros-de |

### resumen

Spec completa: [openspec/specs/resumen/spec.md](../openspec/specs/resumen/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| el resumen muestra lo vigente y lo pendiente | funcional | `resumen_cd337f49861c862e9.el_resumen_muestra_lo_vigente_y_lo_pendiente` | factory_resumen.el_resumen_muestra_lo_vigente_y_lo_pendiente, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |
| riesgos aceptados y límites declarados | funcional | `resumen_cd337f49861c862e9.riesgos_aceptados_y_limites_declarados` | factory_resumen.riesgos_aceptados_y_limites_declarados, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |
| el veredicto es el del cierre y lo dice | funcional | `resumen_cd337f49861c862e9.el_veredicto_es_el_del_cierre_y_lo_dice` | factory_resumen.el_veredicto_es_el_del_cierre_y_lo_dice, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |
| el resumen es determinista y no cambia nada más | no funcional | `resumen_cd337f49861c862e9.el_resumen_es_determinista_y_no_cambia_nada_mas` | factory_resumen.el_resumen_es_determinista_y_no_cambia_nada_mas, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |
| se sabe cuándo quedó viejo | funcional | `resumen_cd337f49861c862e9.se_sabe_cuando_quedo_viejo` | factory_resumen.se_sabe_cuando_quedo_viejo, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |
| se actualiza al cerrar y al archivar | funcional | `resumen_cd337f49861c862e9.se_actualiza_al_cerrar_y_al_archivar` | factory_resumen.se_actualiza_al_cerrar_y_al_archivar, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |
| este repositorio tiene su resumen al día | no funcional | `resumen_cd337f49861c862e9.este_repositorio_tiene_su_resumen_al_dia` | factory_resumen.este_repositorio_tiene_su_resumen_al_dia, factory_resumen.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-003414-resumen-del |

### revision-guiada

Spec completa: [openspec/specs/revision-guiada/spec.md](../openspec/specs/revision-guiada/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| preparar documentos pendientes sin aprobar | funcional | `revision_guiada_c5794e24f22c4deb6.preparar_documentos_pendientes_sin_aprobar` | factory_revision_guiada.preparar_documentos_pendientes_sin_aprobar, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |
| validar informe guiado y su alcance declarado | funcional | `revision_guiada_c5794e24f22c4deb6.validar_informe_guiado_y_su_alcance_declarado` | factory_revision_guiada.validar_informe_guiado_y_su_alcance_declarado, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |
| derivar pendientes de decisiones separadas | funcional | `revision_guiada_c5794e24f22c4deb6.derivar_pendientes_de_decisiones_separadas` | factory_revision_guiada.derivar_pendientes_de_decisiones_separadas, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |
| registrar confirmacion humana informada | funcional | `revision_guiada_c5794e24f22c4deb6.registrar_confirmacion_humana_informada` | factory_revision_guiada.registrar_confirmacion_humana_informada, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |
| conservar evidencia y comprobar vigencia | funcional | `revision_guiada_c5794e24f22c4deb6.conservar_evidencia_y_comprobar_vigencia` | factory_revision_guiada.conservar_evidencia_y_comprobar_vigencia, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |
| mantener formato libre con declaracion explicita | funcional | `revision_guiada_c5794e24f22c4deb6.mantener_formato_libre_con_declaracion_explicita` | factory_revision_guiada.mantener_formato_libre_con_declaracion_explicita, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |
| explicar y verificar los limites del recorrido | funcional | `revision_guiada_c5794e24f22c4deb6.explicar_y_verificar_los_limites_del_recorrido` | factory_revision_guiada.explicar_y_verificar_los_limites_del_recorrido, factory_revision_guiada.corrida_completa | verde al cerrar el 2026-10-05 | 20261004-005956-revision-guiada |

### revisores

Spec completa: [openspec/specs/revisores/spec.md](../openspec/specs/revisores/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| pedir una revisión del candidato actual | funcional | `revisores_c466ac292a9f99ce6.pedir_una_revision_del_candidato_actual` | factory_revisores.pedir_una_revision_del_candidato_actual, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |
| revisores configurables | funcional | `revisores_c466ac292a9f99ce6.revisores_configurables` | factory_revisores.revisores_configurables, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |
| el pedido se genera desde el cambio | funcional | `revisores_c466ac292a9f99ce6.el_pedido_se_genera_desde_el_cambio` | factory_revisores.el_pedido_se_genera_desde_el_cambio, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |
| lo que sale mal no se guarda como informe | funcional | `revisores_c466ac292a9f99ce6.lo_que_sale_mal_no_se_guarda_como_informe` | factory_revisores.lo_que_sale_mal_no_se_guarda_como_informe, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |
| el revisor no decide | no funcional | `revisores_c466ac292a9f99ce6.el_revisor_no_decide` | factory_revisores.el_revisor_no_decide, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |
| las vueltas anteriores se muestran sin decidirse otra vez | funcional | `revisores_c466ac292a9f99ce6.las_vueltas_anteriores_se_muestran_sin_decidirse_otra_vez` | factory_revisores.las_vueltas_anteriores_se_muestran_sin_decidirse_otra_vez, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |
| este cambio se revisa con pedir-revision | no funcional | `revisores_c466ac292a9f99ce6.este_cambio_se_revisa_con_pedir_revision` | factory_revisores.este_cambio_se_revisa_con_pedir_revision, factory_revisores.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-192608-revisores |

### vigencia

Spec completa: [openspec/specs/vigencia/spec.md](../openspec/specs/vigencia/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| vigencia por contenido del producto | funcional | `vigencia_c82d7f5b48fbc29ba.vigencia_por_contenido_del_producto` | factory_vigencia.vigencia_por_contenido_del_producto, factory_vigencia.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-154433-la-vigencia-de |
| el commit observado se conserva y se muestra | funcional | `vigencia_c82d7f5b48fbc29ba.el_commit_observado_se_conserva_y_se_muestra` | factory_vigencia.el_commit_observado_se_conserva_y_se_muestra, factory_vigencia.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-154433-la-vigencia-de |
| informe guiado vinculado al contenido | funcional | `vigencia_c82d7f5b48fbc29ba.informe_guiado_vinculado_al_contenido` | factory_vigencia.informe_guiado_vinculado_al_contenido, factory_vigencia.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-154433-la-vigencia-de |
| respetar los registros existentes | no funcional | `vigencia_c82d7f5b48fbc29ba.respetar_los_registros_existentes` | factory_vigencia.respetar_los_registros_existentes, factory_vigencia.corrida_completa | verde al cerrar el 2026-10-05 | 20261005-154433-la-vigencia-de |

### web

Spec completa: [openspec/specs/web/spec.md](../openspec/specs/web/spec.md)

| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |
|---|---|---|---|---|---|
| la web explica cómo trabajar entre varias personas con sus agentes | funcional | `web_c5a0a7128a6a24b88.la_web_explica_como_trabajar_entre_varias_personas_con_sus_agentes` | factory_web.la_web_explica_como_trabajar_entre_varias_personas_con_sus_agentes, factory_web.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-115805-web-y-docs |
| el sitio cuenta lo que trae la versión publicada | funcional | `web_c5a0a7128a6a24b88.el_sitio_cuenta_lo_que_trae_la_version_publicada` | factory_web.el_sitio_cuenta_lo_que_trae_la_version_publicada, factory_web.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-115805-web-y-docs |
| lo que la web nombra existe | no funcional | `web_c5a0a7128a6a24b88.lo_que_la_web_nombra_existe` | factory_web.lo_que_la_web_nombra_existe, factory_web.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-115805-web-y-docs |
| guía de colaboración sin las fricciones del piloto | funcional | `web_c5a0a7128a6a24b88.guia_de_colaboracion_sin_las_fricciones_del_piloto` | factory_web.guia_de_colaboracion_sin_las_fricciones_del_piloto, factory_web.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-115805-web-y-docs |
| el ID de un cambio termina en un sufijo legible | funcional | `web_c5a0a7128a6a24b88.el_id_de_un_cambio_termina_en_un_sufijo_legible` | factory_web.el_id_de_un_cambio_termina_en_un_sufijo_legible, factory_web.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-115805-web-y-docs |
| la guía desde cero sigue funcionando | no funcional | `web_c5a0a7128a6a24b88.la_guia_desde_cero_sigue_funcionando` | factory_web.la_guia_desde_cero_sigue_funcionando, factory_web.corrida_completa | verde al cerrar el 2026-10-07 | 20261007-115805-web-y-docs |

## Cambios abiertos

Lo que falta se calculó al generar este resumen; un commit posterior puede cambiarlo.

### 20261002-204916-validar-el-flujo — Validar el flujo humano de Oracle Factory

Fase `espera_aprobacion_spec` · modo `confirmacion` · capacidad `software-factory` · [propuesta](../openspec/changes/20261002-204916-validar-el-flujo/proposal.md)

- aprobación humana de spec
- importación OpenSpec → requisitos Oracle
- revisión humana aprobada y sin hallazgos abiertos
- veredicto Oracle exitoso con evidencia
- primero hay que aceptar la propuesta y la spec (aprobar-spec)

### 20261002-222858-explicar-oracle — Explicar Oracle Factory como flujo humano de producción de software

Fase `requisitos_importados` · modo `confirmacion` · capacidad `landing-page` · [propuesta](../openspec/changes/20261002-222858-explicar-oracle/proposal.md)

- revisión humana aprobada y sin hallazgos abiertos
- veredicto Oracle exitoso con evidencia

### 20261002-234439-dist-uv — Preparar distribución de Factory con uv y selección de proyecto

Fase `requisitos_importados` · modo `confirmacion` · capacidad `distribucion` · [propuesta](../openspec/changes/20261002-234439-dist-uv/proposal.md)

- revisión humana aprobada y sin hallazgos abiertos
- veredicto Oracle exitoso con evidencia

### 20261004-005956-elegir-medidas — Elección de medidas

Fase `requisitos_importados` · modo `confirmacion` · capacidad `measurement_choice` · [propuesta](../openspec/changes/20261004-005956-elegir-medidas/proposal.md)

- revisión humana aprobada y sin hallazgos abiertos
- veredicto Oracle exitoso con evidencia

### 20261004-005956-inicio-guiado — Inicio guiado

Fase `requisitos_importados` · modo `confirmacion` · capacidad `onboarding` · [propuesta](../openspec/changes/20261004-005956-inicio-guiado/proposal.md)

- revisión humana aprobada y sin hallazgos abiertos
- veredicto Oracle exitoso con evidencia

### 20261004-121432-coordinar-dos — Coordinar dos personas con sus agentes sin interferencias

Fase `requisitos_importados` · modo `confirmacion` · capacidad `colaboracion` · [propuesta](../openspec/changes/20261004-121432-coordinar-dos/proposal.md)

- revisión humana aprobada y sin hallazgos abiertos
- veredicto Oracle exitoso con evidencia
- medidas de 5 requisitos: sin decisión registrada; registrala con medir y las mismas medidas

Carpetas de `openspec/changes/` sin registro de Factory (anteriores al flujo): `20261002-224749-revision-poc`, `20261003-185925-migrar-task`, `20261003-235610-web-rigurosa`.

## Riesgos aceptados

### De cambios con requisitos vigentes

- **G-03** (20261004-005956-revision-guiada): archivos_revisados es declarativo y no se contrasta con el diff. Aceptado por Brian Hollweg: Se resuelve en la tarea cli-humana: mostrar archivos del diff no revisados.
- **G-04** (20261004-005956-revision-guiada): Las medidas usan umbral de igualdad, distinto de meta.ningun_umbral_de_igualdad. Aceptado por Brian Hollweg: Umbral de igualdad deliberado: exige exactamente los casos enumerados.
- **M-02** (20261005-105331-modos-de-trabajo): importar puede fallar con títulos de requisito acentuados si Oracle normaliza distinto que modos.slug. Aceptado por Brian Hollweg: «Sí, corregí M-01…» sobre la propuesta de mantener M-02, M-03 y M-04 como riesgo aceptado; falla a la vista.
- **M-03** (20261005-105331-modos-de-trabajo): Las guías y la web no mencionan los modos ni --agente. Aceptado por Brian Hollweg: Mismo mensaje; va a la tarea docs-web-modos.
- **M-04** (20261005-105331-modos-de-trabajo): Las medidas usan umbral de igualdad, distinto de meta.ningun_umbral_de_igualdad. Aceptado por Brian Hollweg: Mismo mensaje; umbral de igualdad deliberado.
- **R2-08** (20261005-105331-modos-de-trabajo): La revisión en funcional usa los tipos de todos los requisitos del cambio, no sólo los afectados. Aceptado por Brian Hollweg: Mismo mensaje: queda marcado en el código como simplificación.
- **R2S-09** (20261005-132144-jerarquia-de): `.factory/` entera queda fuera de la huella y es un nombre que también usan otras herramientas. Aceptado por Brian Hollweg: es decisión de la spec que aceptó Brian («Listo con los dos.»): .factory/ entera queda fuera de la huella; la guarda del home y los enlaces cubren el riesgo práctico y el límite quedó declarado en docs/estructura.md
- **R2V-03** (20261005-154433-la-vigencia-de): head_preparacion es lo que el informe dice de sí mismo; no se comprueba contra Git. Aceptado por Brian Hollweg: Mismo mensaje: dato informativo que no condiciona nada.
- **R2V-05** (20261005-154433-la-vigencia-de): Las propuestas de revisión pendientes con la firma anterior nunca se confirman como «confirmo». Aceptado por Brian Hollweg: Mismo mensaje: la persona decide igual y es una transición corta.
- **R2X-01** (20261005-154433-la-vigencia-de): En repositorios con SHA-256 (64 hexadecimales) el HEAD de preparación se descarta siempre. Aceptado por Brian Hollweg: «Vamos con tus recomendaciónes»: se acepta, con el límite declarado, que en repositorios SHA-256 no se guarde head_preparacion.
- **R2P-05** (20261005-184427-los-registros-de): El remoto Git de la prueba acepta push sin autenticación, aunque sólo dentro de una red privada. Aceptado por Brian Hollweg: Mismo mensaje: el remoto de prueba no autentica, pero existe sólo en su red privada.

## Límites declarados

### De cambios con requisitos vigentes

- (20261004-005956-revision-guiada) El análisis lo hizo un agente (Claude Code) y las decisiones las tomó Brian en la conversación; el agente no es independiente de quien implementó (misma familia de modelo, otra sesión).
- (20261004-005956-revision-guiada) tests/test_review_guided.py se revisó por nombres y contrato, no línea por línea; los demás archivos listados se leyeron completos o en su diff.
- (20261004-005956-revision-guiada) No mide claridad para principiantes ni calidad del análisis; la prueba de la guía comprueba presencia de secciones y comandos, no su calidad.
- (20261004-005956-revision-guiada) Brian aceptó los límites inherentes el 2026-10-05 («acepto la revisión guiada»): la calidad del análisis, la autenticación o competencia de los actores y la claridad para un principiante no se miden con pruebas. Se retiran de los requisitos como «sin medir» y siguen documentados aquí. La claridad para un principiante sigue sin observarse con una persona real.
- (20261004-005956-revision-guiada) El producto revisado incluye cambios posteriores a la primera revisión de este cambio (modos de trabajo, colaboración y vigencia por contenido). Se ejecutaron de nuevo el sensor y la suite, pero el código que modificaron se revisó en el cambio de cada uno, no en éste.
- (20261005-105331-modos-de-trabajo) El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo: independiente del autor, no de la familia.
- (20261005-105331-modos-de-trabajo) Factory no autentica actores: un agente que simule una terminal interactiva pasa por persona. El arnés lo declara entre sus límites.
- (20261005-105331-modos-de-trabajo) Las decisiones de medidas anteriores a que se guardara el hash del .requisito (las cinco confirmaciones de Brian sobre este mismo cambio) no se pueden comparar con el archivo: una edición manual posterior no se detecta hasta decidir de nuevo.
- (20261005-105331-modos-de-trabajo) No hay documentación de los modos en las guías ni en la web (tarea docs-web-modos).
- (20261005-105331-modos-de-trabajo) Renovación de la revisión registrada el 2026-10-05 sobre c0e7c3c: Factory vincula la revisión al HEAD (hallazgo G-02) y el commit que archivó el registro anterior la dejó desactualizada. El producto es idéntico: la huella de archivos coincide con la de la revisión anterior (af9bc5e).
- (20261005-132144-jerarquia-de) El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo: independiente del autor, no de la familia.
- (20261005-132144-jerarquia-de) Sólo Linux; no se probó Windows ni otras versiones de Python.
- (20261005-132144-jerarquia-de) La prueba con contenedores Docker entre máquinas (tools/verify_maquinas.py) no se volvió a correr en este candidato; este cambio no toca el código que ejercita (juzgar y la portabilidad de los hechos), pero no está medido.
- (20261005-132144-jerarquia-de) La fase 2 (mover el estado de cada cambio y la configuración a .factory/) no está hecha: es un cambio propio.
- (20261005-132144-jerarquia-de) Los paquetes de Clue y los informes de R2 guardan la ruta de los checkouts revisados; la limpieza de rutas es el cambio 20261005-193914-quitar-la-ruta.
- (20261005-132144-jerarquia-de) Una intermitencia no reproducida (3 apariciones en unas 100 corridas) en pruebas con huellas, de causa desconocida; se agregó diagnóstico.
- (20261005-154433-la-vigencia-de) El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo: independiente del autor, no de la familia. No hay una autorrevisión separada del autor.
- (20261005-154433-la-vigencia-de) La vigencia por contenido mide que el producto no cambió, no que lo revisado fuera correcto. Una revisión vigente no es una revisión buena.
- (20261005-154433-la-vigencia-de) Factory no autentica actores: un agente que simule una terminal interactiva pasa por persona.
- (20261005-154433-la-vigencia-de) Los repositorios con formato de objetos SHA-256 funcionan, pero no guardan head_preparacion (R2X-01).
- (20261005-154433-la-vigencia-de) La regla vive en la rama tarea/vigencia-por-contenido; no está en main. Las revisiones de colaboración y de revisión guiada la usarán cuando se integre.
- (20261005-154433-la-vigencia-de) La revisión se registra sobre un HEAD de archivo posterior al candidato probado 2509c13; el producto es idéntico (la regla nueva lo permite).
- (20261005-184427-los-registros-de) El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo: independiente del autor, no de la familia. No hay una autorrevisión separada del autor.
- (20261005-184427-los-registros-de) Las «máquinas» son contenedores en un solo equipo físico: no se mide latencia de red, relojes distintos ni sistemas operativos distintos. Las personas y sus confirmaciones son fixtures.
- (20261005-184427-los-registros-de) Los registros y la evidencia anteriores a este cambio conservan la ruta privada del autor; su limpieza es el cambio 20261005-193914-quitar-la-ruta, pendiente de aceptación. Los paquetes de Clue guardan la ruta del checkout revisado, límite declarado fuera de alcance.
- (20261005-184427-los-registros-de) La guía del sitio (site/desde-cero.html) sigue guardando los hechos en una carpeta ignorada por Git, lo que ahora genera la advertencia; queda para la tarea guia-v2.
- (20261005-184427-los-registros-de) No se probó Windows. Factory se verifica sólo en Linux.
- (20261005-184427-los-registros-de) La revisión se registra sobre un HEAD de archivo posterior al candidato probado fd1bfe7; el producto es idéntico (la vigencia por contenido lo permite).
- (20261005-193914-quitar-la-ruta) El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo: independiente del autor, no de la familia.
- (20261005-193914-quitar-la-ruta) La ruta privada sigue en el historial de Git público y en tareas/ (evidencia atada a hashes, que no se reescribe); no se reescribe la historia.
- (20261005-193914-quitar-la-ruta) Sólo Linux; las rutas de Windows no se soportan. Una fuente con texto después de la comilla de cierre no se reescribe ni se avisa (forma que Oracle no admite).
- (20261005-193914-quitar-la-ruta) Al integrar, el último cambio integrado (portabilidad) figurará «desactualizado respecto del producto», como con cualquier commit que toque archivos del producto.
- (20261005-193914-quitar-la-ruta) No se corrió el arnés Docker ni los demás arneses sobre este candidato; la herramienta no toca el código del producto.
- (20261006-004456-fase-2-de-la) El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo: independiente del autor, no de la familia.
- (20261006-004456-fase-2-de-la) Sólo Linux; no se probó Windows ni otras versiones de Python.
- (20261006-004456-fase-2-de-la) migrar no se defiende de otro proceso que cree enlaces mientras corre (borra el nombre del temporal y lo abre sin seguir enlaces, sin prueba de concurrencia).
- (20261006-004456-fase-2-de-la) migrar no juzga el contenido de la configuración de la raíz que mueve; config_proyecto la rechaza igual en el lugar nuevo.
- (20261006-004456-fase-2-de-la) La evidencia anterior en tareas/<ID>/evidencia-* no se movió a .factory/cambios/<ID>/candidatos/.
- (20261006-161029-archivar-al) El autor es Claude; la revisión la hicieron Codex (GPT) y Agy (Gemini): independiente del autor y de su familia, pero no humana.
- (20261006-161029-archivar-al) R2A-01 a R2A-04 vienen de las sondas de una sesión de R2 que se cortó antes de escribir su informe de Clue.
- (20261006-161029-archivar-al) Sólo Linux; no se probaron Windows, ACL ni atributos extendidos.
- (20261006-161029-archivar-al) Los 9 cambios que nunca se cerraron no se archivan: queda como tarea decidir si se cierran o se abandonan.
- (20261006-161029-archivar-al) La spec consolidada generada queda fuera de la huella; una edición a mano la detectan Factory al fusionar y el verificador, no la huella.
- (20261007-003414-resumen-del) El autor es Claude; la revisión la hicieron Codex (GPT) y Agy (Gemini): independiente del autor y de su familia, pero no humana.
- (20261007-003414-resumen-del) Sólo Linux.
- (20261007-003414-resumen-del) El veredicto de cada requisito vigente es el del cierre de su cambio: no hay todavía una corrida de Oracle sobre todo el sistema (tarea hechos-varios).
- (20261007-003414-resumen-del) Lo que les falta a los cambios abiertos depende de la huella del producto: un commit que vence una revisión deja el resumen viejo hasta regenerarlo.
- (20261007-003414-resumen-del) Los cambios viejos sin medidas muestran sólo lo que reporta pendientes_actuales (revisión y veredicto), no que falta medir; se revisa en cli-humana.
- (20261007-115805-web-y-docs) El autor es Claude; revisaron Codex (GPT) y Agy (Gemini): independiente del autor y de su familia, pero no humano. Ninguna persona leyó todavía la página como lectora.
- (20261007-115805-web-y-docs) Las pruebas de la web no usan navegador (Playwright no está instalado): no comprueban cómo se ve ni la escena animada.
- (20261007-115805-web-y-docs) El trabajo en equipo que describe la página no se probó con personas reales; la página lo dice.
- (20261007-115805-web-y-docs) Los IDs de los cambios anteriores conservan el sufijo cortado; sólo los nuevos usan la capacidad.
- (20261007-150043-autoproduccion) Evidencia: Escenarios p1–p4 en repositorios temporales, Linux; los informes de revisores son fixtures con el formato de Clue y la validación de Clue se simula. Más la comprobación de que este cambio tiene su paquete de Clue y los informes de sus revisores en la carpeta de su candidato.
- (20261007-150043-autoproduccion) codex (gpt-6-luna): Comparé las 12 entradas de CONTRACTS con los 12 métodos de prueba de tests/test_autoproduccion.py: coincidencia exacta, sin omisiones ni duplicados; la entrada p5 usa el nombre renombrado.
- (20261007-150043-autoproduccion) codex (gpt-6-luna): Ejecuté tools/verify_autoproduccion.py: las 246 pruebas de la suite pasaron y los 12 casos de contrato fueron exactos; el verificador informó éxito=false porque este worktree no contiene la carpeta local del candidato 047cfc7 requerida por su autocontrol.
- (20261007-192608-revisores) Evidencia: Escenarios v1–v6 en repositorios temporales, Linux, con un revisor de prueba y oracle-clue real (sin Clue las pruebas se omiten y la corrida no es completa). Más la comprobación de que este cambio tiene en la carpeta de su candidato vigente un informe de revisor y el pedido con que se obtuvo. No mide la calidad de las revisiones.
- (20261007-192608-revisores) codex (gpt-6-luna): Revisé la propuesta, la spec, el diff incremental completo del paquete y los cambios de registro/requisitos/notas. La implementación funcional no cambió entre base y head.
- (20261007-192608-revisores) codex (gpt-6-luna): Corrí PATH=/tmp/claude-1000/-home-workstation-Dev/factory/d3ffc37f-4c26-4426-b2d7-381bdbfe4609/scratchpad/env/bin:$PATH /home/workstation/Dev/factory-rev/.venv/bin/python -m unittest tests.test_revisores: 16 pruebas, OK.
- (20261007-192608-revisores) codex (gpt-6-luna): Contrasté los hallazgos de las vueltas anteriores con el historial de correcciones y la base 8c59250; no vi reaperturas en el diff incremental.
- (20261007-192608-revisores) codex (gpt-6-luna): No corrí la suite completa ni Oracle end-to-end y no hice mutaciones sobre copias. No evalué propiedades fuera de las promesas de la spec.
- (20261007-223645-decisiones-guiadas) Evidencia: Escenarios d1–d5 en repositorios temporales, Linux, con la entrada de la terminal simulada y sin oracle-clue (los informes de prueba se usan marcados sin validar). Los arneses que corren el CLI instalado en una pseudoterminal (guía, instalado, colaboración, entre máquinas) se corren aparte. No mide que el menú sea cómodo para quien lo usa.
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Contrasté cada una de las promesas de la propuesta y los cinco requisitos de la spec (las confirmaciones son un menú, revisar guía la revisión de punta a punta, el motivo se elige, confirmar las medidas propuestas de una vez, sin terminal no hay decisión de persona) con la implementación en oracle_factory/cli.py, oracle_factory/revision.py, los catálogos y los requisitos.
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Comprobé que los 7 hallazgos de las rondas anteriores permanecen resueltos sin regresiones: DGUI-01 (origen del motivo en resoluciones), DGUI-02 (evidencia mostrada antes de decidir), DGUI-03 (verificación de sha256 de requisitos en confirmar medidas), DGUI-04 (respuesta inválida en de a una cancela en vez de saltear), DGUI-05 (aislamiento de motivos_propuestos sin colisión con propuestas canónicas), DGUI-06 (revisión incompleta sólo permite pedir cambios), y DGUI-07 (validación de dígitos ASCII con regex en vez de isdigit para evitar fallo con superíndices Unicode).
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Ejecuté la suite unitaria de decisiones: .venv/bin/python -m unittest tests.test_decisiones (12 pruebas, OK).
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Ejecuté el sensor de contrato: tools/verify_decisiones.py (274 pruebas, 12 casos de contrato d1–d5 exactos, éxito: True).
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Ejecuté la suite completa de tests de la fábrica descubierta con discover (274 pruebas, OK).
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Ejecuté una batería de 10 mutaciones manuales en copia aislada para verificar la sensibilidad de la suite frente a regresiones (aceptar Enter solo, superíndices Unicode, aprobar con hallazgos abiertos, pérdida de origen_motivo, clave errónea en propuestas, salteo en input inválido de de a una, omisión de comprobación sha256 en medidas cambiadas, orden del motivo propuesto, desactivación de exigir_terminal y motivo persona registrado como confirmo); todas las mutaciones fueron detectadas y rechazadas por las pruebas.
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Comprobé la consistencia de contratos con el registro (factory.json), documentos de revisión (informe.json, decisiones.json, review.md), y la visualización de estado en cli.py y resumen.py.
- (20261007-223645-decisiones-guiadas) agy (gemini-3.8-flash-high): Límites asumidos: no se interactuó con una terminal interactiva física real (la suite simula entrada con mock de input y terminal_interactiva); la base del paquete incluye la migración mecánica de confirmaciones tipeadas a '1' en 17 archivos de tests cubierta por la suite.
- (20261007-223645-decisiones-guiadas) codex (gpt-6-luna): Inspeccioné el diff completo del paquete y contrasté las cinco promesas de la spec con cli.py, revision.py, las pruebas, y los contratos existentes de registro y documentos de revisión.
- (20261007-223645-decisiones-guiadas) codex (gpt-6-luna): Corrí PATH=/tmp/claude-1000/-home-workstation-Dev-factory/d3ffc37f-4c26-4426-b2d7-381bdbfe4609/scratchpad/env/bin:$PATH /home/workstation/Dev/factory-dg/.venv/bin/python -m unittest tests.test_decisiones: 12 pruebas, OK.
- (20261007-223645-decisiones-guiadas) codex (gpt-6-luna): Revisé las siete rondas anteriores solicitadas; sus defectos no aparecen reabiertos en el diff actual.
- (20261007-223645-decisiones-guiadas) codex (gpt-6-luna): No corrí la suite completa ni hice mutaciones; no probé una interacción manual con pseudoterminal.
