---
generado: oracle-factory kb
id: "conocimiento_cc12f23b7134ebe23.la_recuperacion_documental_expone_si_hay_respaldo_suficiente"
vigente: true
---

# la recuperacion documental expone si hay respaldo suficiente

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_cc12f23b7134ebe23.la_recuperacion_documental_expone_si_hay_respaldo_suficiente`
- Vigente: sí
- Cambio: [[cambios/20261024-020022-0b3-preguntar]]
- Veredicto: cumple
- Medidas: `factory_preguntar.la_recuperacion_documental_expone_si_hay_respaldo_suficiente`, `factory_preguntar.corrida_completa`, `factory_preguntar.calidad_documental`, `factory_preguntar.calidad_abstencion`, `factory_preguntar.respaldo_documental`
- Fuente: openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md#la recuperación documental expone si hay respaldo suficiente

Tipo: funcional Las consultas de conocimiento SHALL conservar búsqueda híbrida sobre fuentes vigentes con sus citas y exclusiones, y SHALL aplicar un criterio explícito y probado de respaldo para no presentar candidatos irrelevantes como respuesta. Si no encuentra respaldo suficiente SHALL decirlo. Una consulta de estado con filtros no admitidos SHALL comunicar su alcance en vez de afirmar un cálculo distinto o deducirlo de pasajes. Un puntaje de ranking SHALL NOT presentarse como probabilidad de certeza. SHALL NOT enviar texto a un proveedor que el proyecto no haya configurado explícitamente.
