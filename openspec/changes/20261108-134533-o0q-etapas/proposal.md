# Autonomía por etapa: construcción, integración, publicación y producción

## Por qué

Hoy el modo de trabajo (`confirmacion`, `funcional`, `autonomo`) dice quién decide las cuatro decisiones de **construir** un cambio: spec, medidas, revisión y cierre. Lo que viene después (integrar en main, publicar, desplegar a producción) queda fuera de ese modelo: integrar y empujar se hacen con un menú aparte y `desplegar --autorizar` es siempre de una persona. Brian quiere un modo de piloto automático que construya de principio a fin sin interrupciones, y la forma segura de darlo es separar la autonomía por etapa: poder decir «autónomo para construir, con una persona para publicar y producción», y avanzar etapa por etapa según el riesgo. Este cambio es la política; el conductor que las recorre y los frenos de la construcción son cambios posteriores.

## Qué cambia

- `.factory/config.json` admite una clave opcional `autonomia` con las etapas **integracion**, **publicacion** y **produccion**, cada una en `confirmacion` (una persona decide; es lo que pasa hoy) o `autonomo` (un agente puede decidir). Lo que no se declara es `confirmacion`. Sin la clave, nada cambia.
- La etapa **construccion** no se duplica: sigue siendo el modo del cambio (`modo_por_defecto` y `oracle-factory modo`).
- `oracle-factory autonomia` (de solo lectura, con `--json`) muestra las cuatro etapas, su modo y quién decide, y cuáles tienen hoy un comando de Factory que las aplique.
- `oracle-factory autonomia ETAPA MODO` cambia una etapa: lo decide siempre una persona, con confirmación en su terminal, nunca con `--agente`.
- Una etapa en `autonomo` tiene efecto real hoy en **produccion**: `desplegar --autorizar` lo puede ejecutar un agente, registrado a su nombre. Para integración y publicación no hay todavía un comando de Factory que lo aplique (se hacen con git y gh); la política queda declarada y la usará el conductor.
- `docs/modos.md` explica las etapas.

## Fuera de alcance

- El conductor `autopilot` que recorre las etapas y las condiciones de parada de la construcción (cambios siguientes).
- Que PyPI deje de ser de una persona: subir a PyPI no es una etapa de Factory.
- Los modos `funcional` en las etapas posteriores: no tiene sentido para operaciones y se rechaza.

## Decisiones humanas

Aprobar la spec. Anotado para quien revise: poner `produccion` en `autonomo` permite que un agente despliegue a los destinos declarados; se sigue exigiendo que el plan pase la puerta, la simulación y la prueba del conjunto, y el rollback sigue vigente. Por defecto, y mientras una persona no lo cambie, nada de esto está activo.
