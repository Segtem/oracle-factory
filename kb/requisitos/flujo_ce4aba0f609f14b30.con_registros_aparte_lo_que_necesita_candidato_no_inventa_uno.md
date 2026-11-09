---
generado: oracle-factory kb
id: "flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno"
vigente: true
---

# con registros aparte lo que necesita candidato no inventa uno

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno`
- Vigente: sí
- Cambio: [[cambios/20261109-212224-xo0-registros-raiz]]
- Veredicto: sin juicio
- Medidas: `factory_registros_raiz.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno`, `factory_registros_raiz.corrida_completa`
- Fuente: openspec/changes/20261109-212224-xo0-registros-raiz/specs/flujo/spec.md#con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno

Tipo: funcional El sistema DEBE, con `--registros` distinto de la raíz del producto, rechazar `pedir-revision`, `revision-preparar`, `revision`, `revisar`, `juzgar` y `cerrar` con un mensaje que diga que todavía no se admiten con registros aparte (etapa 3 de 6), sin escribir nada y con código de salida distinto de cero, y DEBE hacer que `estado` muestre el cambio sin candidato vigente en vez de fallar.
