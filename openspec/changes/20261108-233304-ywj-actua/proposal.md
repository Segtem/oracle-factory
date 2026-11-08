# Autopilot que actúa: corre lo mecánico, delega lo creativo, con topes y rastro

## Por qué

El conductor `autopilot` (cambio 3a) ya dice qué haría ahora, sin tocar nada. Brian pidió que Factory pueda construir de principio a fin sin interrupciones humanas, con su propio bucle de razonar y actuar. Este es el cambio 3b: el conductor actúa, dentro de los límites que Brian fijó. Las decisiones de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, integrar y pushear) no se saltan: el bucle se detiene ahí y deja el comando listo para pegar. Integración, publicación y producción quedan en `confirmacion`.

## Qué cambia

`oracle-factory --agente NOMBRE autopilot ID --ejecutar [--lanzar COMANDO] [--max-pasos N] [--max-minutos M]` repite este bucle hasta que algo lo detenga:

1. **Observar y razonar:** la decisión de `autopilot.decidir` sobre el estado del cambio.
2. **Dejar el porqué:** un `mensaje` en el registro del cambio, a nombre del agente, con la acción, el motivo y el comando, antes de actuar.
3. **Actuar:** `actuar` corre el comando de Factory con `--agente NOMBRE` en un proceso aparte; `delegar_al_agente` lanza el comando que se dio en `--lanzar` (por ejemplo `claude -p`) con la instrucción como último argumento; sin `--lanzar`, el bucle se detiene ahí.
4. **Volver a observar.**

Se detiene, y lo dice, cuando el cambio está terminado, hay un freno, toca una decisión de una persona (con su comando), el comando o el agente lanzado fallan, no hay progreso (la misma decisión dos veces seguidas), o se acaba un tope (10 pasos y 120 minutos por defecto). Al final deja un `mensaje` con el motivo de la detención y muestra el resumen de los pasos.

## Fuera de alcance

Autonomía en integración, publicación o producción (siguen en `confirmacion`). Elegir o instalar un agente: `--lanzar` es explícito en cada corrida y no se guarda en la configuración del proyecto. Ejecutar sin `--agente`: una persona no usa `--ejecutar`. Hacer que el agente lanzado sea determinista o confiable: lo que haga es trabajo suyo y se verifica con la evidencia, Oracle y la revisión de siempre.

## Decisiones humanas

Ninguna nueva. Brian dejó integración, publicación y producción en `confirmacion` y las decisiones suyas no se saltan. Los topes por defecto (10 pasos, 120 minutos) son una propuesta: si prefiere otros se cambian en la spec.
