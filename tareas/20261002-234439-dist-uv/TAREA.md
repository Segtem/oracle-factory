# Preparar distribución de Factory con uv y selección de proyecto

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS:

## Alcance

Preparar Factory como paquete instalable con uv tool install/uvx, con selección explícita de la carpeta del proyecto. Hoy fabrica.py fija ROOT a su propio checkout: instalarlo sin resolver eso escribiría las tareas y acuerdos dentro de la herramienta. La guía actual instala Oracle y Trackertast desde PyPI y descarga Factory con Git.

## Criterios

- Separar código instalado y proyecto de trabajo; soportar una carpeta elegida por el operador.
- Definir pyproject.toml, entry point, versión y dependencias reales.
- Probar instalación aislada y flujo completo contra un proyecto nuevo sin modificar el paquete instalado.
- Documentar y preparar artefactos de distribución; no anunciar instalación pública hasta publicar una versión real.

## Próximo paso

Diseñar el selector de proyecto y la estructura del paquete; acordar ese alcance antes de implementar la distribución.
