---
generado: oracle-factory kb
id: "trazabilidad_cca95191eb0039b11.trazabilidad_cruza_los_casos_con_el_diff_del_candidato"
vigente: true
---

# trazabilidad cruza los casos con el diff del candidato

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `trazabilidad_cca95191eb0039b11.trazabilidad_cruza_los_casos_con_el_diff_del_candidato`
- Vigente: sí
- Cambio: [[cambios/20261013-180751-trazabilidad]]
- Veredicto: cumple
- Medidas: `factory_trazabilidad.trazabilidad_cruza_los_casos_con_el_diff_del_candidato`, `factory_trazabilidad.corrida_completa`
- Fuente: openspec/changes/20261013-180751-trazabilidad/specs/trazabilidad/spec.md#trazabilidad cruza los casos con el diff del candidato

Tipo: funcional `oracle-factory trazabilidad ID` SHALL leer `trazabilidad.json` de la evidencia del candidato vigente y cruzarlo con las líneas que el candidato cambió respecto de su base: por requisito, las líneas cambiadas que ejecutan sus casos; las líneas cambiadas ejecutables que no ejecuta ningún caso, como sin respaldo; y los archivos cambiados que la traza no puede ver. Las líneas que no son ejecutables (comentarios, en blanco) SHALL NOT figurar sin respaldo. Con `--json` SHALL imprimir un objeto con `esquema` `oracle-factory.trazabilidad/1`, el candidato y la base. Sin trazabilidad.json en la evidencia SHALL fallar diciendo dónde va y cómo generarla.
