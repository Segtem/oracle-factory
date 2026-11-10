---
generado: oracle-factory kb
id: "flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia"
vigente: true
---

# con almacen aparte el candidato es el ancestro con evidencia

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia`
- Vigente: sí
- Cambio: [[cambios/20261110-140719-h7t-registros-candidato]]
- Veredicto: cumple
- Medidas: `factory_registros_candidato.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia`, `factory_registros_candidato.corrida_completa`
- Fuente: openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md#con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia

Tipo: funcional El sistema DEBE, con almacén aparte, tomar como candidato vigente de un cambio el commit del repo del producto más cercano a HEAD (entre los ancestros de HEAD, HEAD incluido) que tenga carpeta de evidencia en el almacén para ese cambio, siempre que no haya diferencias de archivos entre ese commit y HEAD y que el producto no tenga cambios locales (archivos modificados, en el índice o nuevos no ignorados); si no se cumple, el cambio NO DEBE tener candidato vigente; y sin almacén aparte el candidato DEBE seguir calculándose como hasta ahora.
