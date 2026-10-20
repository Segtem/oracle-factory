# La sesión de Live Share desde el tablero: compartir, unirse, terminar e instalar

## Why

Brian usa VS Code con una interfaz reducida y no ve el botón de Live Share en la barra de estado (2026-10-20). Para
trabajar de a dos tiene que encontrar comandos en la paleta. El tablero ya sabe si hay Live Share y si hay sesión:
puede ofrecer la acción que sigue.

## What changes

- Sin Live Share instalado, el tablero ofrece «Instalar Live Share», que abre la extensión en VS Code para instalarla.
- Con Live Share y sin sesión, ofrece «Compartir sesión» (la empieza y Live Share copia el enlace, como siempre) y
  «Unirse a una sesión» (pide el enlace y entra como invitado).
- Como anfitrión, ofrece «Terminar sesión»; como invitado, «Salir de la sesión».

## Out of scope

- Cambiar la configuración de Live Share (permisos de los invitados, sólo lectura).

## Human decisions

- Brian lo pidió el 2026-10-20: «que el tablero ponga un icono para acceder rápido».
