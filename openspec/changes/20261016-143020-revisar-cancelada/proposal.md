# estado avisa cuando una revisión no se pudo registrar y por qué

## Why

El 2026-10-16, en Jam (cambio 20261015-221410-renombrar-nodo), el informe de codex quedó incompleto y «Aprobar» apareció como NO DISPONIBLE. Brian lo eligió, `revisar` cortó con «no se puede aprobar … No registré nada» y eso se perdió entre las comprobaciones del menú. Respondió «Listo» y el agente siguió como si la revisión estuviera registrada: commiteó «revisión registrada por Brian» y corrió juzgar sin revisión. Hoy un intento cortado no deja rastro, así que ni `estado` ni el agente lo pueden ver. Tarea `20261016-003916-revisar-cancelada`.

## What changes

- **Un intento cortado deja constancia**: cuando `revisar` (el paso a paso) corta después de mostrar la revisión sin registrarla —por ejemplo, si se elige un Aprobar no disponible, se cancela, falta el límite de una revisión incompleta o se cierra la entrada—, guarda un evento `revision_cancelada` con la causa, el candidato y quién lo intentó. No registra ninguna decisión.
- **`estado` lo dice**: mientras el último intento sea uno cortado, `estado` muestra un aviso «el último intento de revisión (<fecha>, <persona>) no se registró: <causa>». Termina con «volvé a correr oracle-factory revisar ID» o, si ya hay una revisión anterior registrada, con «sigue valiendo la revisión anterior». `estado --json` lo trae en `avisos`, así un agente puede comprobarlo antes de seguir.

## Out of scope

- Cambiar el menú, por ejemplo que elegir un Aprobar no disponible vuelva a preguntar en vez de cortar.
- Los cortes previos a mostrar la revisión, como que no haya terminal o candidato: ésos ya dicen qué hacer y no hubo ningún intento.

## Human decisions

- Brian eligió esta tarea el 2026-10-16.
