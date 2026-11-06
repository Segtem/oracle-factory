# Diseño

- `site/concurrencia.js` (UMD, como `juego.js`): `nuevo(escenario, semilla)`, `paso(estado)`, `reiniciar`, `escenarios`. El
  estado es datos planos: actores (persona o agente, con su rama), cambios, un tronco, un registro de eventos con quién y por qué.
  Sin `Math.random` ni reloj: la semilla fija el orden en que dos acciones simultáneas se aplican.
- Reglas del motor (cada una con la cita del doc que la respalda): una decisión de persona (`aprobar-spec`, `medir --confirmar`,
  `revisar`, `cerrar`, `decidir-union`) no la toma un agente: el agente propone y la acción queda pendiente; los registros de dos
  ramas se unen y quedan los eventos de ambas; lo que dos ramas decidieron distinto no lo elige el motor; un archivo de producto
  editado por dos ramas es un conflicto de Git; una revisión o un juicio dejan de valer si el producto cambió desde que se hicieron.
- La escena (`site/concurrencia.html` + estilos y dibujo en el mismo JS o en `viva.js`): sprites de `pixel.js`, SVG en línea. El
  registro es una lista `aria-live="polite"`. Con movimiento reducido cada escenario muestra su estado final sin animar.
- Pruebas: `tests/test_concurrencia.cjs` (motor, con node) y `tests/test_web_concurrencia.cjs` (página, con Chromium) más
  `tests/test_web_concurrencia.py` que las corre y comprueba citas y comandos contra `docs/colaboracion.md` y la CLI.

Rondas de revisión: el motor valida cada paso del guion, no sólo los guiones fijos. Un agente sólo edita y trae main; tomar,
decidir e integrar los propone y no cambian nada. Cada actor trabaja en su propio checkout (sólo se revisa el cambio de otro).
Cerrar exige una revisión vigente. Los eventos del registro llevan su rama y su número de orden. Una acción, un actor o una
decisión que la simulación no modela es un error del guion (se lanza), no algo que se acepte en silencio.
