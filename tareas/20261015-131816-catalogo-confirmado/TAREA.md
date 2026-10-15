# Una medida confirmada cuyo catálogo cambia vuelve a pedir confirmación

- ESTADO: ABIERTA
- PRIORIDAD: 25
- ETIQUETAS: 

### Nota (2026-10-15 13:18:21 UTC)

Visto en 20261015-122841-docs-web-modos (2026-10-15): después de que Brian confirmara las medidas, el agente cambió el alcance de dos catálogos (factory_modos_web.*) por un hallazgo de revisión, y estado siguió dando la confirmación por vigente. La decisión de medidas guarda el sha256 del .requisito, no el de los catálogos que nombra; medir compara el catálogo sólo durante la operación. Propuesta: guardar en la decisión la huella de cada catálogo asociado (umbral, filtro, alcance) y, si cambia, que estado lo marque como pendiente de confirmar con medir ID --confirmar, nombrando la medida y qué cambió. Revisar también qué hace juzgar con un catálogo distinto del confirmado.
