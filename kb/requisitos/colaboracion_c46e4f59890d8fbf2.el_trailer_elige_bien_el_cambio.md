---
generado: oracle-factory kb
id: "colaboracion_c46e4f59890d8fbf2.el_trailer_elige_bien_el_cambio"
vigente: true
---

# el trailer elige bien el cambio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_c46e4f59890d8fbf2.el_trailer_elige_bien_el_cambio`
- Vigente: sí
- Cambio: [[cambios/20261019-232444-quien]]
- Veredicto: cumple
- Medidas: `factory_quien.el_trailer_elige_bien_el_cambio`, `factory_quien.corrida_completa`
- Fuente: openspec/changes/20261019-232444-quien/specs/colaboracion/spec.md#el trailer elige bien el cambio

Tipo: funcional El hook SHALL elegir el cambio del trailer `Cambio:` en este orden: si el mensaje nombra el ID de un cambio del proyecto, ése (y si nombra varios, ninguno); si no, el único cambio abierto del checkout; si hay varios abiertos, el único que tiene como responsable a la persona que hace el commit (su nombre en la configuración de Git). En cualquier otro caso SHALL NOT agregar el trailer.
