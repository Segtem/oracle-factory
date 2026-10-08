# Riesgos aceptados que persisten entre vueltas y candidatos

- ESTADO: ABIERTA
- PRIORIDAD: 6
- ETIQUETAS: revision, autoproduccion


## Objetivo

Hoy aceptar un riesgo (`riesgo_aceptado`) vale para un candidato. En los cambios revisores y decisiones-guiadas el mismo hallazgo volvió en varias vueltas, y el agente escribía a mano en cada `--pedir` «Límites asumidos, no los reportes: …». Un registro de aceptados (del cambio o del proyecto: qué, quién, por qué, hasta cuándo) que Factory incluye solo en el pedido de cada revisor, y que `revisar` usa para mostrar como «ya aceptado» un hallazgo que coincide en vez de preguntar otra vez.

Origen: video «AI Coding Agents + Static Code Analysis for Safer Code» (IBM Developer, 2026-10-08), que Brian pidió aplicar a Factory. Es su consejo de «configurar exclusiones / compensaciones aceptables conocidas».

## Notas

- Coincidencia: por regla/kind + archivo + texto normalizado, no por id (los ids cambian entre vueltas).
- Aceptar es decisión de persona (menú); el agente puede proponer.
- Encaja con vueltas-severidad.
