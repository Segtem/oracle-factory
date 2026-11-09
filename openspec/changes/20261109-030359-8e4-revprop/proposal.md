# Autopilot: la propuesta de revisión es trabajo del agente, antes de pedírsela a la persona

## Por qué

La primera prueba real del conductor (cambio `eventos`) mostró una brecha: ante `oracle-factory revisar ID` el conductor le pide la decisión a la persona, pero antes le toca al agente preparar el informe (`revision-preparar`) y dejar su propuesta (`revisar --decision --motivo`), que resume rondas, evidencia, mutaciones y límites. Eso lo hubo que hacer a mano. `estado` solo dice «próximo paso: revisar» y no distingue si el agente ya hizo su parte.

## Qué cambia

`estado --json` suma la clave `propuesta_de_revision` (la última propuesta de un agente: decisión, candidato, quién y cuándo, o `null`). El conductor, ante `revisar` con un candidato vigente, mira si hay una propuesta para ese candidato: si no la hay, la acción es `delegar_al_agente` con la instrucción de preparar el informe y proponer la decisión; si la hay, `pedir_a_persona`, como hasta ahora. La decisión sigue siendo solo de la persona.

## Fuera de alcance

Pedir una segunda ronda con otro revisor (`estado` solo sugiere uno). Escribir la propuesta: la hace un agente (con `--lanzar` o a mano); el conductor solo la reconoce. Cambiar `revisar`, `revision-preparar` o la propuesta misma.

## Decisiones humanas

Ninguna nueva: la decisión de revisión es de la persona, como siempre.
