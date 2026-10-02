# Design

Página estática bajo `site/`: HTML semántico, CSS y JavaScript sin framework remoto. Pixel art hecho con CSS/canvas o SVG local; animación narrativa por etapas en vez de movimiento perpetuo. Controles visibles: anterior, reproducir/pausar, siguiente y volver al inicio.

La escena presenta una línea de producción modular: bandeja de entrada de ideas → mesa OpenSpec → estación de trabajo de agentes → banco de pruebas → estación de revisión (Clue) → balanza Oracle con evidencia → entrega. Trackertast aparece como tablero que acompaña etapas, responsables y bloqueos. Un avatar humano inspecciona y decide en las cuatro puertas; una pausa detiene la cinta.

La página explica con texto la misma información, usa etiquetas accesibles, foco visible y `prefers-reduced-motion`. No requiere imágenes descargadas. Las etapas llevan estado `disponible`, `prototipo` o `visión`, a confirmar en el contenido.

Los controles humanos de la escena son una simulación explicativa. No registran aprobaciones reales ni cambian tareas del repositorio. La web debe mostrar esa distinción y el estado actual de cada herramienta.
