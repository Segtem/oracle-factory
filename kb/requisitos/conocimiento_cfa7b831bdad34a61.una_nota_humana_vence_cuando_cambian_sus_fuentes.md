---
generado: oracle-factory kb
id: "conocimiento_cfa7b831bdad34a61.una_nota_humana_vence_cuando_cambian_sus_fuentes"
vigente: true
---

# una nota humana vence cuando cambian sus fuentes

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_cfa7b831bdad34a61.una_nota_humana_vence_cuando_cambian_sus_fuentes`
- Vigente: sí
- Cambio: [[cambios/20261020-140603-kb]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «una guía cuyo archivo cambió», «revisar sin terminal o una fuente que no existe»
- Fuente: openspec/changes/20261020-140603-kb/specs/conocimiento/spec.md#una nota humana vence cuando cambian sus fuentes

Tipo: funcional Una nota en `kb/notas/` con `fuentes:` en su frontmatter SHALL quedar «por revisar» cuando cambia el contenido de alguna fuente desde que se marcó revisada; `kb --verificar` SHALL listarla y fallar, y `estado` SHALL avisarla en los cambios abiertos que tocaron esa fuente. `oracle-factory kb revisada NOTA` SHALL marcarla revisada sólo desde la terminal de una persona, y una fuente que no existe SHALL ser un error que nombra la nota.
