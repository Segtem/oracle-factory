# Corregir los controles de la POC

## Why

La revisión solicitada por el usuario encontró que un exit code 0 de Oracle podía representar falta de juicio, que aprobaciones antiguas sobrevivían a cambios del producto y que cancelar una revisión podía sobrescribir el informe anterior.

## What changes

Corregir esos defectos del flujo existente y agregar pruebas de regresión e integración con las herramientas reales. Vincular aprobación, revisión y evidencia a los documentos y al producto comprobados. Este cambio de mantenimiento no aprueba la spec pendiente de la web ni implementa esa web.
