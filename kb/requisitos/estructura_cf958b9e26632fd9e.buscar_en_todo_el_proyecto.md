---
generado: oracle-factory kb
id: "estructura_cf958b9e26632fd9e.buscar_en_todo_el_proyecto"
vigente: true
---

# buscar en todo el proyecto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_cf958b9e26632fd9e.buscar_en_todo_el_proyecto`
- Vigente: sí
- Cambio: [[cambios/20261015-001533-evidencia-fuera]]
- Veredicto: cumple
- Medidas: `factory_busqueda.buscar_en_todo_el_proyecto`, `factory_busqueda.corrida_completa`
- Fuente: openspec/changes/20261015-001533-evidencia-fuera/specs/estructura/spec.md#buscar en todo el proyecto

Tipo: funcional `oracle-factory buscar TEXTO` SHALL buscar en propuestas, specs, requisitos, tareas y registros de Factory, y SHALL mostrar por resultado la ruta, la línea y el cambio al que pertenece. SHALL NOT recorrer la evidencia ni los paquetes de Clue de los candidatos (`evidencia/` y `clue/`), ni los JSON de `tareas/`: están atados a hashes y no se leen de corrido; los informes y pedidos de `revision/` sí se recorren.
