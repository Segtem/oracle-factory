# Vista Destinos en el tablero de VS Code

## Por qué

Factory ya sabe desplegar a varios destinos (una workstation, un VPS, una app, un ESP32…) y probar que el conjunto quedó funcionando, pero ese estado sólo se ve en la terminal con `oracle-factory destinos`. Brian pidió pensar cómo lo muestra Factory en el tablero: quien trabaja en VS Code tiene que ver de un vistazo qué destinos hay, cuál está al día, cuál falló o se revirtió, y qué corrida lo dejó así, sin salir del tablero.

## Qué cambia

- El tablero de VS Code suma una sección **Destinos** (arriba de los cambios), armada con `oracle-factory destinos --json`: por cada destino su nombre, tipo, estado (sin desplegar, desplegado, probado, fallido, revertido, inalcanzable), versión desplegada frente a la esperada, si está desactualizado, de qué otros depende y su última prueba; y el resumen de la última corrida (quién autorizó, resultado, motivo).
- Al abrir o repintar el tablero NO se consulta a los destinos (esa consulta corre los comandos `version` declarados, p. ej. por ssh): se muestra lo registrado, con la versión «desconocida» marcada. Un botón **Consultar ahora** hace la consulta una vez.
- Los pasos de despliegue son botones que **escriben el comando en la terminal sin ejecutarlo** (`desplegar --simular`, y `desplegar --autorizar` para la persona), como el resto del tablero: el tablero nunca despliega ni autoriza.
- Un proyecto sin destinos declarados muestra cómo declararlos; una declaración inválida muestra el motivo y el resto del tablero sigue funcionando. Quien se une por Live Share ve la misma sección.
- El contrato entre la CLI y la extensión (`contrato.json`) pasa a cubrir `destinos --json`.

## Fuera de alcance

- Ejecutar un despliegue desde el tablero, o autorizarlo: sigue siendo de una persona en su terminal.
- Una vista de árbol de destinos en el explorador (sólo el panel del tablero).
- Cambiar `destinos --json` o el despliegue mismo.

## Decisiones humanas

- La consulta a los destinos es a pedido (botón), no automática: se eligió porque cada consulta corre comandos del proyecto contra máquinas remotas. Si se prefiere refrescar solo cada cierto tiempo, es otro cambio.
