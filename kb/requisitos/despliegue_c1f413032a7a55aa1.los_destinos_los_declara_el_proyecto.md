---
generado: oracle-factory kb
id: "despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto"
vigente: true
---

# los destinos los declara el proyecto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto`
- Vigente: sí
- Cambio: [[cambios/20261106-205202-8od-destinos]]
- Veredicto: sin juicio
- Medidas: `factory_despliegue.los_destinos_los_declara_el_proyecto`, `factory_despliegue.corrida_completa`
- Fuente: openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md#los_destinos_los_declara_el_proyecto

Tipo: funcional El sistema DEBE leer los destinos de despliegue de `.factory/destinos.json` —cada uno con nombre, tipo, comandos de construir, desplegar, probar, versión y volver, las dependencias con otros destinos y los nombres de los secretos que necesita—, sin conocer ninguna tecnología concreta, y DEBE rechazar una declaración inválida nombrando el destino y el campo.
