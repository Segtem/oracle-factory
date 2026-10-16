# estado avisa cuando una revisión no se pudo registrar y por qué

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: 

### Nota (2026-10-16 00:39:26 UTC)

Visto el 2026-10-16 en Jam (cambio 20261015-221410-renombrar-nodo): el informe de codex de la vuelta 4 quedó incompleto (su sandbox no abría sockets locales para las pruebas), Factory lo mostró como comprobación no ejecutada y «Aprobar» quedó NO DISPONIBLE; Brian lo eligió dos veces, revisar cortó con «no se puede aprobar … No registré nada», y no lo notó: respondió «Listo» y el agente siguió como si la revisión estuviera registrada (hasta commiteó «revisión registrada por Brian», corregido después). Propuesta: que revisar deje constancia de un intento cancelado (evento con la causa, sin decisión) y que estado diga «la última revisión no se registró: <causa>; qué hacer». Además, que un agente compruebe el evento revision_registrada antes de seguir al juicio. Relacionado: el NO DISPONIBLE del menú ya dice la causa, pero se pierde entre las comprobaciones.
