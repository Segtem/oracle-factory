# Conductor autopilot: decide el siguiente paso por reglas (sin actuar)

## Por qué

Brian pidió que Factory pueda construir de principio a fin sin interrupciones humanas, con su propio bucle de razonar y actuar (react). Los cambios 1 y 2 ya están: la autonomía por etapa y los frenos de `estado`. Falta el conductor. Se parte en dos: este cambio es la mitad que observa y razona (un bucle de control de proceso determinista, sin modelo de lenguaje); la mitad que actúa es el siguiente. Primero se mide qué decidiría el conductor sin tocar nada.

## Qué cambia

`oracle-factory autopilot ID [--json]`, de solo lectura. Observa `estado`, razona por reglas fijas y dice qué viene: `terminado`; `frenar` (hay un freno, un paso que no reconoce o faltan archivos); `pedir_a_persona` (una decisión que es solo de una persona, con su comando listo para pegar); `delegar_al_agente` (trabajo creativo: construir, corregir o elegir medidas, con la instrucción); o `actuar` (un comando mecánico de Factory que un agente puede correr con `--agente`, también con su comando). Cada respuesta lleva el porqué de la regla que la decidió.

## Fuera de alcance

Actuar: correr los comandos, lanzar al agente, repetir el bucle (siguiente cambio). Registrar el porqué en el cambio con `mensaje` (también el siguiente, cuando haya algo que registrar). Cambiar `estado` o los frenos. La autonomía de integración, publicación y producción: siguen en `confirmacion`.

## Decisiones humanas

Ninguna nueva. Brian dejó integración, publicación y producción en `confirmacion` y las decisiones suyas (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, integrar y pushear) no se saltan: el conductor las clasifica como `pedir_a_persona` aunque una etapa estuviera en `autonomo`.
