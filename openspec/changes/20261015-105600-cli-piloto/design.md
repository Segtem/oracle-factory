# Design

- Una medida es del catálogo base cuando su entrada en el catálogo efectivo de Oracle tiene `origen.clase == "catalogo_base"`; el resto es del proyecto.
- «Sin requisito»: una medida que el requisito tenía y ya no tiene, y que ningún otro `.requisito` de `requisitos/` nombra en su `medido_por`. Es un aviso: no impide medir.
- La plantilla sigue teniendo TODO, así que `aprobar-spec` la sigue rechazando hasta que se complete.
