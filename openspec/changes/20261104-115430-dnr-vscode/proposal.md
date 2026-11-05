# Web: capturas reales de VS Code y ejemplos en las guías

## Por qué

Quien llega a la web lee qué hace Factory pero no lo ve: las guías describen el tablero de VS Code con palabras y los comandos no muestran lo que contestan. Para que otra persona se anime a usarlo hace falta ver la herramienta real, con un proyecto de ejemplo, y leer salidas reales de los comandos.

## Qué cambia

- Capturas reales de VS Code (con la extensión 0.5.0 instalada) sobre un proyecto de ejemplo, publicadas en `site/img/` y mostradas en las guías con su texto alternativo y su leyenda: la vista «Factory» en el explorador, el tablero con cambios y responsables, el próximo paso de un cambio y la consulta «por qué».
- Un proyecto de ejemplo y un script reproducible (`tools/capturas_vscode.py`) que lo arma en una carpeta temporal, abre VS Code en un monitor virtual y regenera las capturas, para que se puedan rehacer en cada versión sin tocar el escritorio de nadie.
- Ejemplos con salida real en `desde-cero.html` y `colaboracion.html`: cada bloque «Así se ve» muestra lo que respondió el comando sobre el proyecto de ejemplo, tomado de un archivo generado por el script y no escrito a mano.
- Las capturas y los ejemplos no contienen rutas personales, correos, cuentas ni nombres reales: el proyecto de ejemplo usa personas ficticias.

## Fuera de alcance

- La simulación en pixel art de varias personas y agentes con concurrencia (cambio siguiente).
- Reordenar o rehacer la estructura de las páginas (tercer cambio).
- Cambios en la extensión de VS Code o en la CLI.
- Vídeo o GIF animado: sólo imágenes fijas.

## Decisiones humanas

- Aprobar que las capturas sean de VS Code real sobre un proyecto de ejemplo (ya elegido) y no dibujos.
- Aprobar el tope de peso: cada imagen de hasta 300 KB y el conjunto de hasta 1,5 MB.
