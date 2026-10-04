# Elegir medidas sin editar sintaxis a mano

## Why
La asociación actual exige editar un .requisito con indentación sensible. Un comando puede validar la edición, pero no decidir si una medida demuestra la promesa.

## What changes
- `medir ID --listar`: listar requisitos importados del cambio y medidas disponibles, con enlaces/límites actuales. No escribir archivos.
- `medir ID --requisito ID_REQUISITO --medida ID_MEDIDA [--medida ...]`: asociación explícita; no usar sufijos ambiguos ni seleccionar automáticamente por nombre.
- Exigir spec vigente y requisito que pertenezca al cambio. Validar sintaxis del requisito y existencia de medidas en el catálogo real usando Oracle, sin duplicar su semántica.
- Conservar id, texto, fuente y campos no modificados; escribir atómicamente tras validar el resultado. Rechazar rutas inseguras, medidas duplicadas/inexistentes y cambios concurrentes. No ocultar un alcance parcialmente medido ni eliminar límites sin decisión explícita.
- Una asociación distinta invalida revisión/juicio del cambio y registra una nota. No crear veredicto, aceptar cobertura semántica ni confirmar cierre automáticamente.

## Human decisions
La persona elige y defiende las medidas. La propuesta está lista para revisar; no hay autorización de implementación ni aprobación de pertinencia fabricada. La futura guía debe seguir explicando que enlazar reglas no prueba cumplimiento.

## Out of scope
Recomendar/crear medidas por IA, prometer cobertura completa por existencia de reglas, editar requisitos de otro cambio, inferir evidencia del código.
