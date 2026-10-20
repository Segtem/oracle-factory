---
generado: oracle-factory kb
id: "trazabilidad_c03c40840efaaab69.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero"
vigente: true
---

# los commits de un cambio se ven en log estado y el tablero

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `trazabilidad_c03c40840efaaab69.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero`
- Vigente: sí
- Cambio: [[cambios/20261019-182313-commits]]
- Veredicto: cumple
- Medidas: `factory_commits.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero`, `factory_commits.corrida_completa`
- Fuente: openspec/changes/20261019-182313-commits/specs/trazabilidad/spec.md#los commits de un cambio se ven en log, estado y el tablero

Tipo: funcional `oracle-factory log ID` (y `--json`) SHALL listar los commits del cambio con sha, autor, fecha y asunto, cada uno con cómo se lo unió (trailer o deducido) y si fue candidato revisado o con evidencia: los que llevan su trailer y, para los anteriores al trailer, los deducidos de sus candidatos registrados y del merge que los integró. `estado` SHALL mostrar cuántos commits tiene y el último, y `estado --json` SHALL traerlos. El tablero SHALL mostrarlos por cambio y elegir uno SHALL abrir su diff en VS Code sin modificar nada.
