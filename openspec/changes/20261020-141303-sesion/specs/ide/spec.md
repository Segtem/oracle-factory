# Capability: ide

## ADDED Requirements

### Requirement: la sesión de Live Share se maneja desde el tablero
Tipo: funcional
El tablero SHALL ofrecer la acción que sigue para trabajar de a dos: sin la extensión de Live Share, «Instalar Live Share», que abre la extensión para instalarla; con Live Share y sin sesión, «Compartir sesión», que la empieza, y «Unirse a una sesión», que pide el enlace y SHALL aceptar sólo un enlace https de Live Share; como anfitrión, «Terminar sesión»; como invitado, «Salir de la sesión». El tablero SHALL NOT tomar ninguna decisión de Factory con esos botones.

#### Scenario: compartir, terminar y unirse
- GIVEN el tablero abierto con Live Share y sin sesión
- WHEN se elige «Compartir sesión», después «Terminar sesión», y después «Unirse a una sesión» con un enlace de Live Share y con otro que no lo es
- THEN se empezó y se terminó la sesión, se entró con el enlace de Live Share y el otro se rechazó sin entrar

#### Scenario: sin Live Share
- GIVEN VS Code sin la extensión de Live Share
- WHEN se abre el tablero y se elige «Instalar Live Share»
- THEN se abre la extensión de Live Share para instalarla
