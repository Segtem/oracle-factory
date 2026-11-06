---
generado: oracle-factory kb
id: "despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos"
vigente: true
---

# cada ejecucion deja evidencia sin secretos

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos`
- Vigente: sí
- Cambio: [[cambios/20261106-205202-8od-destinos]]
- Veredicto: sin juicio
- Medidas: `factory_despliegue.cada_ejecucion_deja_evidencia_sin_secretos`, `factory_despliegue.corrida_completa`
- Fuente: openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md#cada_ejecucion_deja_evidencia_sin_secretos

Tipo: funcional El sistema DEBE guardar en `.factory/despliegues/` un registro de cada corrida con el commit, quién planeó y quién autorizó, y por destino los estados, las versiones antes y después, los comandos, su salida y los tiempos, DEBE tapar en cualquier salida registrada el valor de los secretos declarados, y DEBE exponer el estado de todos los destinos como `oracle-factory destinos --json` para el tablero.
