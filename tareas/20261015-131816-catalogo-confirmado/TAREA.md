# Una medida confirmada cuyo catálogo cambia vuelve a pedir confirmación

- ESTADO: CERRADA
- PRIORIDAD: 25
- ETIQUETAS: 

### Nota (2026-10-15 13:18:21 UTC)

Visto en 20261015-122841-docs-web-modos (2026-10-15): después de que Brian confirmara las medidas, el agente cambió el alcance de dos catálogos (factory_modos_web.*) por un hallazgo de revisión, y estado siguió dando la confirmación por vigente. La decisión de medidas guarda el sha256 del .requisito, no el de los catálogos que nombra; medir compara el catálogo sólo durante la operación. Propuesta: guardar en la decisión la huella de cada catálogo asociado (umbral, filtro, alcance) y, si cambia, que estado lo marque como pendiente de confirmar con medir ID --confirmar, nombrando la medida y qué cambió. Revisar también qué hace juzgar con un catálogo distinto del confirmado.

### Nota (2026-10-15 15:52:26 UTC)

Hecha en el cambio 20261015-140406-catalogo-confirmado (merge 7a426b7): la decisión y la propuesta de medidas guardan la huella y el archivo de cada medida; si cambia, falta, no carga o no se lee, la decisión deja de valer (estado lo nombra, juzgar no la usa) y medir --confirmar no la toma tal cual. Las decisiones anteriores sin huella siguen valiendo. El propio cambio lo usó: sus medidas se reconfirmaron porque sus catálogos cambiaron.
