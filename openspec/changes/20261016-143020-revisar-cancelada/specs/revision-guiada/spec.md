# Capability: revision-guiada

## ADDED Requirements

### Requirement: un intento de revisión que no se registró queda a la vista
Tipo: funcional
Cuando `revisar` corta después de mostrar la revisión sin registrarla, SHALL guardar en el registro un evento `revision_cancelada` con la causa, el candidato y la persona, sin registrar ninguna decisión. Mientras el último intento de revisión sea uno cortado, `estado` y `estado --json` (en `avisos`) SHALL avisar que no se registró, con la causa, y SHALL decir qué hacer: volver a correr revisar o, si ya hay una revisión anterior registrada, que esa sigue valiendo.

#### Scenario: se elige un Aprobar no disponible
- GIVEN un candidato con un hallazgo medio que queda abierto
- WHEN la persona corre revisar y elige Aprobar, que no está disponible
- THEN revisar corta sin registrar la revisión, el registro guarda revision_cancelada con la causa, y estado y estado --json avisan que el último intento no se registró, con esa causa y el comando para volver a revisar

#### Scenario: se cancela o se cierra la entrada
- GIVEN un candidato listo para revisar
- WHEN la persona elige Cancelar, o la entrada se cierra en medio del menú
- THEN queda revision_cancelada con su causa y estado lo avisa

#### Scenario: una revisión registrada después
- GIVEN un intento cortado y después una revisión registrada
- WHEN se pide estado
- THEN ya no avisa del intento cortado; y si el intento cortado vino después de una revisión registrada, el aviso dice que sigue valiendo la anterior
