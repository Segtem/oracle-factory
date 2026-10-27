# El tablero y el trabajo de a dos

Factory se puede seguir entero desde VS Code: una vista con los cambios abiertos y un **tablero de comando** que dice qué
te necesita a vos, qué pasó en cada cambio y quién está trabajando en qué. Las decisiones siguen tomándose en la terminal:
el tablero escribe el comando, no lo ejecuta.

## Instalar la extensión

La extensión está en el repositorio (`editores/vscode/`), no en el Marketplace. Se arma sin `npm` y se instala una vez:

```bash
python3 editores/vscode/empaquetar.py
code --install-extension editores/vscode/oracle-factory-0.5.0.vsix
```

Usa `.venv/bin/oracle-factory` del proyecto si existe, si no `oracle-factory` del `PATH`; la configuración de usuario
`factory.comando` elige otra (un proyecto no puede cambiarla desde su `.vscode/settings.json`). Sólo corre en espacios de
trabajo de confianza.

## La vista y el tablero

La vista «Factory» del explorador muestra cada cambio abierto con sus requisitos (medidas, decisión y veredicto), su
revisión, sus artefactos (un clic los abre; el que falta aparece marcado) y el próximo paso. El botón de terminal escribe
ese paso en una terminal del proyecto sin ejecutarlo.

El botón de tablero (o *Factory: Abrir el tablero*) abre, por cada cambio abierto:

- **Lo que te necesita**: la decisión pendiente con su comando listo y las alternativas.
- **Los hallazgos** de los revisores por severidad; un clic abre `archivo:línea`.
- **Los requisitos** con sus medidas y su veredicto, y **los commits** del cambio (un clic abre el diff).
- **La línea de tiempo**: cada decisión con quién la tomó (persona o agente), cuándo y cómo.
- **Las métricas** del cambio y del proyecto: cambios abiertos y cerrados, horas hasta el cierre, cuántos cerraron en una
  vuelta de revisión, qué encontró cada revisor.

El tablero se rehace solo cuando cambia un registro. Lo arma `oracle-factory tablero --json`, que cualquier otro panel
puede usar.

**Preguntar al proyecto.** El botón «Preguntar al proyecto» del tablero (también *Factory: Preguntar al proyecto* en la
paleta y en la vista) pide una pregunta y abre la respuesta de la CLI, con sus fuentes y advertencias; ver
[el conocimiento del proyecto](conocimiento.md). **¿Por qué existe esta línea?** (en el menú del editor) abre el cambio
que escribió la línea del cursor.

## Cada commit dice de qué cambio es

`init` (o `oracle-factory hooks` en un proyecto que ya existía, una vez por clon) instala los hooks de Git
`prepare-commit-msg` y `commit-msg`, que agregan `Cambio: <ID>` a cada commit: el cambio que nombra el mensaje (un merge
«Integrar <ID>»), si no el único abierto, y con varios abiertos el que tomaste. Si ya tenés un hook propio no lo tocan y
te dicen la línea para encadenarlo; nunca impiden un commit. `oracle-factory log ID` (o `--json`) lista los commits de un
cambio. (`oracle-factory trailer` es lo que llama el hook para escribir el trailer: no se corre a mano.)

## Quién trabaja en qué

`oracle-factory tomar ID --con claude-code` te registra como responsable del cambio, con el agente con el que trabajás.
Si otra persona ya lo tiene, hace falta `--relevo` (queda constancia de quién lo tenía), y `soltar ID` lo libera. Un
agente que corre `--agente NOMBRE tomar ID` se suma sin quedar como responsable. Es un acuerdo registrado, no un candado. El tablero compara tu nombre de Git con el del responsable: la decisión de un cambio que tiene otra persona dice «LA DECIDE ANA» y no «TE NECESITA», y «Actividad reciente» lista los últimos diez eventos de los cambios abiertos (quién, qué, en qué cambio, cuándo). Un invitado de Live Share ve el tablero de quien comparte, con el nombre de Git de esa persona. «Qué falta» dice, de cada pendiente, qué es en lenguaje común y si lo hacés vos o lo hace un agente; cuando lo que sigue lo corre un agente, arriba dice «Ahora no te toca nada».
`estado` y el tablero muestran la persona responsable, sus agentes (los declarados y los que actuaron en las últimas 24
horas, con su última acción) y los revisores en curso.

## De a dos, con Live Share

Con [Live Share](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare) en una sesión, el
tablero muestra quién está conectado y con qué rol. Quien comparte publica su tablero: un invitado lo ve aunque no tenga
la CLI ni el proyecto, sus enlaces abren los archivos compartidos y el botón de un comando lo escribe, sin Enter, en la
terminal «Factory» de quien comparte. Cada cambio tiene un **chat**: los mensajes quedan en su registro (no escribas
secretos: se versionan). Desde la terminal, `oracle-factory mensaje ID "texto"` deja un mensaje como persona o, con
`--agente`, como agente.

Los botones del tablero manejan la sesión aunque no veas la barra de estado: «Instalar Live Share», «Compartir sesión»
(copia el enlace), «Unirse a una sesión», «Terminar sesión» y «Salir de la sesión». Factory no autentica a nadie: quien
comparte sólo acepta el nombre de un invitado conectado.

## Integrar sin chocar

Dos personas pueden trabajar en el mismo cambio en ramas distintas. Los hooks de Factory instalan también dos drivers de
merge (en `.gitattributes`, versionado, y en la configuración del clon) y los hooks `post-merge` y `post-commit`:

- El **registro** de un cambio editado en dos ramas se une solo: quedan los eventos de las dos, en el orden de su hora (con
  microsegundos; a la misma hora exacta, un desempate que es igual en todos los clones), y lo que cambió una sola rama.
- Lo que **las dos decidieron distinto** (dos responsables, dos fases, dos cierres) no lo elige Factory: queda lo de la rama
  que integra, `estado` avisa qué falta decidir, y lo resuelve la decisión que corresponde o
  `oracle-factory decidir-union ID CAMPO nuestro|suyo`, desde la terminal de una persona.
- **`resumen.md` y `kb/`** no chocan: se rehacen después del merge (también de uno con conflictos que se termina con
  `git commit`), en un commit aparte. Lo hacen `unir-registro`, `unir-generado` y `rehacer-generado`, que llama Git: no se
  corren a mano.

Cómo se reparte el trabajo entre dos personas, cómo se releva y cómo se integra está en la
[guía de colaboración](colaboracion.md), con el banco de concurrencia que lo prueba.
