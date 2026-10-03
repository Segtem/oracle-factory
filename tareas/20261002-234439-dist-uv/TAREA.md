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


### Nota (2026-10-03 12:37:35 UTC)

Usuario autorizó preparar paquete, commit, push, tag y GitHub Release; publicación PyPI a cargo del usuario. Corte alpha 0.1.0a1: proyecto seleccionable, dependencias incluidas y flujo humano conservado. Alcance transcrito en openspec/changes/20261002-234439-dist-uv.

### Nota (2026-10-03 12:56:50 UTC)

Requisitos importados: distribution_c01af4be8811ed3bb.conservar_el_flujo_humano_instalado, distribution_c01af4be8811ed3bb.entregar_artefactos_verificables, distribution_c01af4be8811ed3bb.instalar_y_seleccionar_proyecto. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-03 12:56:50 UTC)

Factory: 23 tests Python y 11 comprobaciones Chromium OK. Wheel instalado con uv/Python 3.11.16: flujo completo en otro proyecto, con PATH sin oracle/tasks globales; dependencias del entorno verificadas. Se probaron rechazo de aprobación fixture y conservación de configuración. Twine valida wheel y sdist.


### Nota (2026-10-03 13:12:20 UTC)

Release alpha publicado y verificado: https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a1. Tag v0.1.0a1 sobre 400dce8110c672089c4da58340a9107272601294; main empujado. Wheel, sdist y SHA256SUMS remotos coinciden con los artefactos probados. PyPI queda pendiente del usuario.

## Próximo paso

El usuario publica en PyPI los artefactos probados del release v0.1.0a1 (también en dist/), siguiendo NOTAS-DE-RELEASE.md. Tras su aviso, verificar instalación desde PyPI con uv en un entorno limpio y actualizar la guía para usar el índice. El cierre formal del cambio queda sujeto a revisión humana y medidas acordadas; no se simula un veredicto Oracle.
