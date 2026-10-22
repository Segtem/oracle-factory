---
generado: oracle-factory kb
id: "conocimiento_c48413c31f1bcbd66.preguntar_devuelve_pasajes_vigentes_con_su_cita"
vigente: true
---

# preguntar devuelve pasajes vigentes con su cita

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_c48413c31f1bcbd66.preguntar_devuelve_pasajes_vigentes_con_su_cita`
- Vigente: sí
- Cambio: [[cambios/20261021-235127-fjn-rag]]
- Veredicto: cumple
- Medidas: `factory_rag.preguntar_devuelve_pasajes_vigentes_con_su_cita`, `factory_rag.corrida_completa`
- Fuente: openspec/changes/20261021-235127-fjn-rag/specs/conocimiento/spec.md#preguntar devuelve pasajes vigentes con su cita

Tipo: funcional `oracle-factory preguntar \"TEXTO\"` (y `--json`) SHALL devolver los pasajes que mejor responden a la pregunta, tomados del vault (`kb/`), de las propuestas, diseños y specs de los cambios, de las specs vigentes y de `docs/`, cada uno con su cita (archivo y sección) y su cambio cuando lo tiene. SHALL dejar afuera las notas de personas por revisar, nombrándolas aparte, y todo lo de un cambio abandonado, y SHALL ser sólo lectura.
