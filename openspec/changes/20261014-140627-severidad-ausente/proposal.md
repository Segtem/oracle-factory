# Spec de revisores: un informe sin severidad no se guarda

## Why

El requisito «el corte de vueltas sigue la severidad» (cambio `20261013-115616-vueltas-severidad`) promete que, al terminar `pedir-revision`, un hallazgo sin severidad cuenta como medio y pide otra vuelta. Ese escenario no se alcanza: Clue exige la severidad (una de critica, alta, media, baja, informativa) y rechaza el informe antes de que Factory lo guarde. Y si un informe guardado la pierde después, Clue lo rechaza al revalidarlo y `estado` no lo usa, con un aviso. La promesa se probaba sólo sobre la función interna del corte. Lo señaló agy (F-03) en la vuelta 1 de aquel cambio.

Tarea de origen: `20261013-152301-severidad-ausente`.

## What changes

- **El requisito se reescribe (MODIFIED) con lo que pasa de verdad**: un informe con un hallazgo sin severidad o con una desconocida no se guarda; uno guardado que la pierde no se usa para decidir la vuelta, y `estado` avisa por qué. Los escenarios de bajos y medios no cambian.
- **Pruebas de punta a punta** para los dos escenarios nuevos, con Clue real.
- El código no cambia: que el corte cuente como media una severidad ausente queda como defensa interna, sin promesa.

## Out of scope

- Cambiar qué severidades acepta Clue.

## Human decisions

- Ninguna: corrige una promesa que no se cumplía tal como estaba escrita.
