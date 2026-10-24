---
generado: oracle-factory kb
id: "conocimiento_cc12f23b7134ebe23.preguntar_cuenta_y_lista_cambios_desde_el_registro_vigente"
vigente: true
---

# preguntar cuenta y lista cambios desde el registro vigente

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_cc12f23b7134ebe23.preguntar_cuenta_y_lista_cambios_desde_el_registro_vigente`
- Vigente: sí
- Cambio: [[cambios/20261024-020022-0b3-preguntar]]
- Veredicto: cumple
- Medidas: `factory_preguntar.preguntar_cuenta_y_lista_cambios_desde_el_registro_vigente`, `factory_preguntar.corrida_completa`, `factory_preguntar.calidad_registro`
- Fuente: openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md#preguntar cuenta y lista cambios desde el registro vigente

Tipo: funcional `oracle-factory preguntar` SHALL reconocer consultas de cantidad y listado de tareas o cambios de Factory, para todos, abiertos, cerrados o abandonados, sin distinguir tildes ni mayúsculas, y SHALL dar el resultado exacto desde el mismo registro y clasificación que `listar`. SHALL explicar el filtro y dar fuentes comprobables, incluso para cero cambios. Un cerrado archivado SHALL contar como cerrado; un abandonado SHALL NOT contar como cerrado ni abierto. SHALL leer el estado en cada consulta sin depender de embeddings ni de un índice documental anterior.
