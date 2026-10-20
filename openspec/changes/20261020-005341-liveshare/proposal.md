# El tablero en pair programming: presencia, tablero compartido y chat con Live Share

## Why

Brian quiere que Factory sirva para trabajar solo o en pair programming: ver en tiempo real si la otra persona está
conectada, hablar con ella y coordinar el trabajo de las personas con sus agentes desde el tablero. «Quién trabaja en
qué» ya dice quién tiene cada cambio; falta la sesión en vivo. Brian eligió Live Share (2026-10-19): ya autentica a las
personas, comparte el espacio de trabajo y deja que una extensión publique un servicio propio, sin servidor nuestro.

## What changes

- **Presencia:** el tablero muestra si hay una sesión de Live Share, quién está conectado y con qué rol (anfitrión o
  invitado), y se actualiza cuando alguien entra o sale. Sin Live Share instalado, o sin sesión, el tablero funciona
  igual que hoy.
- **Tablero compartido:** quien comparte publica su tablero; un invitado lo ve aunque no tenga Factory instalado, y se
  rehace cuando cambia un registro del anfitrión. Los enlaces del invitado abren los archivos compartidos por Live Share.
  El botón de un comando, para un invitado, le pide al anfitrión que lo escriba en su terminal «Factory», sin Enter: si
  esa terminal está compartida, el invitado lo ve; lo ejecuta quien tiene la terminal. El tablero no decide nada.
- **Chat guardado en el cambio:** `oracle-factory mensaje ID "texto"` deja un mensaje en el registro del cambio (una
  persona desde su terminal o un agente con `--agente`), y en una sesión de Live Share el tablero de cada cambio tiene
  un chat: el mensaje llega al instante a todos y el anfitrión lo guarda en el registro con el nombre que da Live Share.
  Los mensajes se ven en la línea de tiempo del cambio.

## Out of scope

- Otro transporte (servidor propio, Git) y chat fuera de una sesión de Live Share desde el panel.
- Que un invitado tome decisiones desde el tablero: cada decisión se sigue tomando desde la terminal de quien decide.
- Probar con dos máquinas de verdad en la evidencia automática: la sesión real la verifica una persona.

## Human decisions

- Brian eligió el 2026-10-19: Live Share; el chat se guarda en el cambio; los invitados escriben comandos sólo en una
  terminal compartida (la API de Live Share no deja escribir en la terminal compartida desde el invitado: por eso el
  pedido va al anfitrión, que lo escribe en su terminal «Factory»).
- Un mensaje guardado queda versionado con el cambio: no escribir secretos en el chat.
