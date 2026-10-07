# Zonas críticas: rutas que exigen más revisión cuando el cambio las toca

- ESTADO: ABIERTA
- PRIORIDAD: 16
- ETIQUETAS: revision, modos


## Objetivo

Que el proyecto declare sus zonas críticas (por ejemplo `"criticos": ["pagos/**", "auth/**"]` en `.factory/config.json`) y que Factory ajuste cuánto se revisa según lo que tocó el candidato: si el diff toca una zona crítica, el cambio no puede cerrarse en modo autónomo ni funcional sin confirmación, y la revisión guiada exige que esos archivos figuren entre los revisados, con el hallazgo o la comprobación que los cubra.

Origen: el video «Yo leo el código, ¿y tú?» (BettaTech, 2026-10-07), que Brian pidió contrastar con Factory y Clue. Su punto central es que la criticidad no es por cambio sino por parte del código: dentro de un mismo PR hay líneas que importan (el handler de pagos) y líneas que no (gráficos internos). Hoy Factory elige el modo para el cambio entero; esto es «la ceja que se levanta» cuando el agente toca un archivo sensible, pero automática y registrada.

## Notas

- Usar el paquete de Clue del candidato para saber qué archivos tocó, no un diff aparte.
- Encaja con trazabilidad (P12): de la zona crítica al requisito y a las líneas.
- No convierte la criticidad en un número ni en un puntaje: es una lista declarada por personas.
