---
generado: oracle-factory kb
id: "modos_cfcd50c150324f5bc.una_decision_de_medidas_deja_de_valer_si_cambia_el_catalogo"
vigente: true
---

# una decision de medidas deja de valer si cambia el catalogo

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `modos_cfcd50c150324f5bc.una_decision_de_medidas_deja_de_valer_si_cambia_el_catalogo`
- Vigente: sí
- Cambio: [[cambios/20261015-140406-catalogo-confirmado]]
- Veredicto: cumple
- Medidas: `factory_catalogo.una_decision_de_medidas_deja_de_valer_si_cambia_el_catalogo`, `factory_catalogo.corrida_completa`
- Fuente: openspec/changes/20261015-140406-catalogo-confirmado/specs/modos/spec.md#una decisión de medidas deja de valer si cambia el catálogo

Tipo: funcional Una decisión de medidas SHALL guardar la huella del archivo de cada medida que el requisito nombra. Si alguno cambia o desaparece del catálogo efectivo, la decisión SHALL dejar de valer: `estado` SHALL mostrarla pendiente nombrando la medida y su archivo, y `juzgar` SHALL NOT usarla. Volver a decidir con las mismas medidas SHALL registrar una decisión nueva. Una decisión sin esa huella, tomada antes de este cambio, SHALL seguir valiendo.
