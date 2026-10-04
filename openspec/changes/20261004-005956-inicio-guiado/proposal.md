# Primer cambio de Factory con menos pasos manuales

## Why
La guía funciona, pero copiar proposal/spec/catálogos y recuperar IDs exige acciones que una persona nueva puede confundir. Preparar ese material no equivale a aprobarlo.

## What changes
- Extender `nuevo` con `--con-ejemplo notas`: copiar la propuesta, spec y catálogos del ejemplo incluido al cambio que acaba de crear. Capacidad notas inferida; una capacidad distinta se rechaza. Conservar `nuevo --capacidad ...` sin ejemplo.
- Verificar todos los destinos antes de crear la tarea: no sobrescribir un ejemplo, documento ni catálogo existente. Si una copia falla, informar qué quedó y cómo recuperar; evitar tareas duplicadas al reintentar.
- `listar` muestra IDs completos/títulos/fases de cambios Factory existentes, sin convertir toda tarea tracker en un cambio Factory.
- `init` muestra pasos propios de Factory y explica Git/.gitignore, sin crear commits ni ejecutar un agente. Conservar configuración del usuario; ignorar salidas temporales y bytecode de los ejemplos de Python.
- Al crear/importar/registrar un paso, mostrar acción siguiente y ruta exacta; mantener las confirmaciones de spec, revisión y cierre.

## Human decisions
Propuesta preparada a partir del pedido de continuar y de la revisión de principiantes. Todavía requiere aceptación del contrato antes de implementar, conforme a AGENTS.md. No hay confirmaciones terminal simuladas. Ejemplos y catálogos se entregan para lectura: importación posterior continúa SIN MEDIR.

## Out of scope
Generar una app completa, elegir medidas por el usuario, aprobar una spec, ejecutar tests/sensores/IA, editar Git o cerrar tareas automáticamente.
