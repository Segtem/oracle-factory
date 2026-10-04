# Revisar la web de Factory con precisión y recorrido para principiantes

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 


## Pedido y alcance

El usuario pidió, tras publicar los tres paquetes de migración, usar agy1 y agy2 para mejorar
la web de Factory y explicar con rigor cómo trabajar con la herramienta. Autorizó mejorar la
web; pidió informar si hacen falta cambios de Factory para que alguien sin experiencia lo use.
La revisión de documentación y sus correcciones están aceptadas por ese pedido. Cambios
funcionales de la CLI se propondrán con sus hallazgos y límites antes de ampliar el alcance.

## Trabajo delegado

- agy1: contrastar portada, recorrido y guía con el comportamiento real del paquete publicado.
- agy2: recorrer la guía en proyecto vacío y detectar pasos ambiguos para principiantes.
- Codex: verificar las citas y corregir la web; pruebas de navegador y reproducción de la guía.
Los informes de modelos no reemplazan un piloto con una persona sin experiencia.

### Nota (2026-10-04 01:03:16 UTC)

Auditorías reales de agy1/agy2 completas y segunda lectura de correcciones adjuntas. Corregidas capacidades actuales/futuras, ejemplo vs app, revisión externa, selección manual de medidas, alcance de verde y procedencia, cierre local, instalación publicada, rutas/copias/confirmaciones/recuperación e informe pendiente. Segunda ronda: sincronizado fallback HTML, explicitada selección manual y rótulo Evidencia. 23 tests Python y 11 comprobaciones Chromium verdes. Comandos extraídos de guía ejecutados desde PyPI en carpeta temporal hasta cierre fixture; no piloto humano. Propuestas de producto en cuatro tareas nuevas.

- Adjunto: [factory-guide-rigurosa-resultados.json](factory-guide-rigurosa-resultados.json)

### Nota (2026-10-04 01:07:11 UTC)

Requisitos documentales importados directamente con Oracle desde el alcance autorizado por conversación. Nacen sin medir: los tests funcionales y auditorías no se presentan como una medida formal de claridad humana. No se simula confirmación escrita de la CLI. Implementación de las correcciones y verificaciones terminadas; aceptación humana formal y piloto se coordinan con 20261002-222858-explicar-oracle.

- Adjunto: [portada.png](portada.png)

- Adjunto: [acuerdo-mobile.png](acuerdo-mobile.png)

- Adjunto: [revision-mobile.png](revision-mobile.png)

## Próximo paso

Comprobar el despliegue de esta revisión en Pages. Después, coordinar el piloto y acuerdo de medidas de claridad con 20261002-222858-explicar-oracle. Las correcciones de web y verificaciones técnicas están terminadas; no hay cierre humano formal simulado. Las cuatro mejoras de CLI registradas requieren revisar su propuesta antes de implementación.
