# Preparar distribución de Factory con uv y selección de proyecto

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS:

## Alcance

Preparar Factory como paquete instalable con uv tool install/uvx, con selección explícita de la carpeta del proyecto. Problema original, resuelto en 0.1.0a1: fabrica.py fijaba ROOT a su propio checkout. La versión publicada usa la carpeta actual o --proyecto; la guía instala desde PyPI y exporta el ejemplo incluido.

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


### Nota (2026-10-03 17:28:20 UTC)

Publicación PyPI confirmada por el usuario y verificada: 0.1.0a1. Wheel/sdist del índice coinciden por SHA-256 con el release. Instalación con uv, Python 3.13 y cache nueva; prueba funcional del ejecutable instalado OK. Evidencia en verificacion-pypi.json. README actualizado para usar el índice. La guía ahora crea un proyecto vacío, inicializa Factory y exporta el ejemplo del paquete sin clonar el repositorio; 11 comprobaciones Chromium OK.

### Nota (2026-10-04 01:03:17 UTC)

Sucesor 0.1.0a2 publicado y verificado desde PyPI; wheel/sdist iguales al release, instalación aislada y ejemplo completo hasta cierre fixture. Se conserva el pendiente formal de medidas y revisión humana de esta tarea.

## Próximo paso

Revisión humana del flujo instalado y elección de medidas para los requisitos de distribución antes del cierre formal. PyPI 0.1.0a2 y su instalación están verificados.
