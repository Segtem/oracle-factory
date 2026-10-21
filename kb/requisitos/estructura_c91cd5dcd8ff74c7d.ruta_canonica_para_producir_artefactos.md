---
generado: oracle-factory kb
id: "estructura_c91cd5dcd8ff74c7d.ruta_canonica_para_producir_artefactos"
vigente: true
---

# ruta canonica para producir artefactos

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_c91cd5dcd8ff74c7d.ruta_canonica_para_producir_artefactos`
- Vigente: sí
- Cambio: [[cambios/20261012-214104-ruta-vigente]]
- Veredicto: cumple
- Medidas: `factory_ruta.ruta_canonica_para_producir_artefactos`, `factory_ruta.corrida_completa`
- Fuente: openspec/changes/20261012-214104-ruta-vigente/specs/estructura/spec.md#ruta canonica para producir artefactos

Tipo: funcional `oracle-factory ruta ID TIPO` SHALL imprimir la ruta canónica para producir un artefacto de ese tipo (evidencia, clue, revision o checkout) sobre el candidato vigente del cambio —el commit con carpeta de candidato más cercano a HEAD, si el producto no cambió desde él— o sobre HEAD si no hay candidato vigente, nombrando la carpeta del candidato con los 7 primeros caracteres del hash completo del commit, sin crear ni modificar archivos.
