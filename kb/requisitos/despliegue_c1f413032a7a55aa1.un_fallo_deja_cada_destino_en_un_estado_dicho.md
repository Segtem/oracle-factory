---
generado: oracle-factory kb
id: "despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho"
vigente: true
---

# un fallo deja cada destino en un estado dicho

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho`
- Vigente: sí
- Cambio: [[cambios/20261106-205202-8od-destinos]]
- Veredicto: sin juicio
- Medidas: `factory_despliegue.un_fallo_deja_cada_destino_en_un_estado_dicho`, `factory_despliegue.corrida_completa`
- Fuente: openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md#un_fallo_deja_cada_destino_en_un_estado_dicho

Tipo: funcional El sistema DEBE, ante el fallo de un destino, cortar la corrida (o seguir con los destinos que no dependen del caído, si el proyecto lo declara), volver atrás con su comando los destinos desplegados en esa corrida, y dejar cada uno en un estado dicho —sin desplegar, desplegado, probado, fallido, revertido o inalcanzable—, avisando de los que quedaron desplegados sin poder volverse atrás; DEBE calcular «desactualizado» comparando la versión que el destino dice que corre con la punta de la rama, mostrándolo «desconocido» si no se alcanza.
