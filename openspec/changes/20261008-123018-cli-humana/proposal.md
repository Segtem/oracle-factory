# La CLI cómoda para la persona: errores claros, comando propio, salidas legibles y próximo paso

## Why

Las decisiones guiadas (0.1.0a7) sacaron las frases y los JSON, pero quedan fricciones medidas al cerrar revisores y decisiones-guiadas:

- **Errores sin causa.** La compuerta de aprobación dijo «revisión incompleta, hallazgos abiertos o comprobaciones falla/no_ejecutada» sin decir cuál. `revision-preparar` dejó un informe vacío en silencio cuando no había candidato vigente. Con el `python` del sistema, la CLI cayó con un traceback de `ModuleNotFoundError`.
- **El comando.** En un clon de desarrollo hay que escribir `.venv/bin/python fabrica.py …`; con `python fabrica.py` se usa el intérprete equivocado.
- **El Markdown en la terminal.** `.factory/resumen.md` se lee como texto plano.
- **El próximo paso.** `estado` sugiere pasos viejos o incompletos. Con Oracle en verde dice `estado` en vez de `cerrar`, no conoce `revisar` ni `medir --confirmar`, y propone `juzgar --con RUTA` cuando los hechos ya están en el candidato. Además, para seguir hay que copiar el comando.

Pedido de Brian: «Tenemos que mejorar y facilitar la parte cli-humana».

## What changes

- **Los errores dicen qué pasó y cómo seguir.**
  - La compuerta de aprobación nombra las comprobaciones que no cumplen, los hallazgos abiertos o la revisión incompleta.
  - `revision-preparar` avisa cuando no hay candidato vigente.
  - Si falta `oracle-metalenguaje`, la CLI lo dice y explica cómo seguir.
- **`python fabrica.py` usa el entorno del proyecto.** Si el intérprete no tiene las dependencias y el clon tiene `.venv`, se vuelve a ejecutar con ese entorno. Con el entorno activado se usa `oracle-factory`.
- **`resumen --ver`** muestra el resumen con formato si `glow` está instalado, y como texto si no.
- **`estado` calcula el próximo paso según lo que falta.**
  - Los pasos son: aprobar la spec, importar, confirmar las medidas propuestas, pedir una revisión, revisar, juzgar y cerrar.
  - En una terminal, `estado` ofrece ejecutarlo desde un menú.

## Out of scope

- La tarea `avanzar`, que recorre el flujo entero; acá se ofrece sólo el próximo paso.
- `estado` y `donde` con formato Markdown.
- Instalar `oracle-factory` globalmente desde el clon.

## Human decisions

- ¿El menú de `estado` ejecuta pasos de agente (como `pedir-revision`) o sólo los de persona? Propuesta: cualquier paso que esté completo, sin rutas por completar; el paso se ejecuta como persona, igual que si se tipeara.
