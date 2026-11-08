---
generado: oracle-factory kb
id: "practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora"
vigente: true
---

# una excepcion mal escrita no se ignora

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora`
- Vigente: sí
- Cambio: [[cambios/20261108-115714-ohv-noaplica]]
- Veredicto: cumple
- Medidas: `factory_noaplica.una_excepcion_mal_escrita_no_se_ignora`, `factory_noaplica.corrida_completa`
- Fuente: openspec/changes/20261108-115714-ohv-noaplica/specs/practicas/spec.md#una_excepcion_mal_escrita_no_se_ignora

Tipo: funcional El sistema DEBE rechazar, al derivar el contrato, una línea «Pruebas:» mal escrita (sin motivo, repetida o distinta de «no aplica — motivo») con el mensaje del lector de excepciones de Factory, en vez de ignorarla y pedir casos como si no existiera.
