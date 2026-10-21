---
generado: oracle-factory kb
id: "estructura_c01f2e6fb0af5aed6.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara"
vigente: true
---

# los escalares del proyecto se ejecutan solo si el proyecto lo declara

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_c01f2e6fb0af5aed6.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara`
- Vigente: sí
- Cambio: [[cambios/20261015-155346-oracle-en-carpeta]]
- Veredicto: cumple
- Medidas: `factory_carpeta.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara`, `factory_carpeta.corrida_completa`
- Fuente: openspec/changes/20261015-155346-oracle-en-carpeta/specs/estructura/spec.md#los escalares del proyecto se ejecutan sólo si el proyecto lo declara

Tipo: funcional Con `\"confiar_escalares\": true` en la configuración, Factory SHALL correr Oracle con `--confiar-escalares` al evaluar medidas; sin esa clave SHALL NOT pasarlo. Un valor que no sea true o false SHALL rechazarse.
