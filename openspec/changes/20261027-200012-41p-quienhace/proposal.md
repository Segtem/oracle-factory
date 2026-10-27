# El tablero dice qué hace cada quien y cuándo no te toca nada

## Why

Con la extensión nueva, Brian abrió el tablero del cambio `largo` del piloto y vio «Qué falta» con tres pendientes técnicos («importación OpenSpec → requisitos Oracle», «revisión humana aprobada y sin hallazgos abiertos», «veredicto Oracle exitoso con evidencia») y dijo: «no tengo mucho para hacer en vs code». La lista no dice quién hace cada cosa ni qué hace él. El próximo paso era `importar`, que corre un agente: no había nada para él, pero el tablero no lo decía.

## What changes

- `oracle-factory tablero --json` suma, en cada cambio, `faltan`: cada pendiente con una frase en lenguaje humano («Importar los requisitos de la spec») y quién lo hace (`persona` o `agente`). Lo que Factory no reconoce queda con su texto original y sin responsable. `pendientes` no cambia.
- La sección «Qué falta» de la página muestra cada pendiente con su frase y la marca «tuyo» o «de un agente».
- Cuando el próximo paso es un comando que corre un agente (no una decisión de una persona), arriba de «Qué falta» aparece «Ahora no te toca nada: sigue <frase del paso> (lo hace un agente)». Cada paso del JSON suma `humano`, su frase.

## Out of scope

- Cambiar el texto de `pendientes` o de `proximo_paso` en la CLI.
- Ejecutar los comandos desde el tablero.
- Saber qué agente tiene cada cosa: sólo se dice «un agente».

## Human decisions

- Si el aviso «Ahora no te toca nada» debe aparecer también cuando el cambio lo tiene otra persona (propongo que no: ahí ya dice «LA DECIDE …»).
