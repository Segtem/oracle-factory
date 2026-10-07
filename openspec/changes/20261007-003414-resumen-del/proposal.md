# Resumen del estado actual: una vista corta y regenerable de lo vigente

## Why

Con la spec consolidada (`openspec/specs/`, 0.1.0a5) ya hay un documento por capacidad. Pero para saber cómo está el proyecto hoy (qué requisitos rigen y con qué evidencia, qué cambios siguen abiertos y qué les falta, qué riesgos aceptó una persona y qué límites se declararon) todavía hay que leer siete specs, trece registros de cambio y los informes de revisión. Es la segunda pieza del plan «comprimir lo que se lee, no lo que se guarda» (tarea `20261006-160411-resumen`): una vista derivada de los registros, sin LLM, que cabe en una lectura y se sabe cuándo quedó vieja.

## What changes

1. **`oracle-factory resumen`** genera `.factory/resumen.md` con cuatro secciones:
   - **Lo vigente, por capacidad:** cada requisito con su tipo, su requisito de Oracle, el cambio del que viene, sus medidas y el veredicto con el que se cerró ese cambio. Sin escenarios: para el detalle, enlaza la spec consolidada.
   - **Cambios abiertos:** fase, modo, capacidad de destino y lo que les falta para cerrar.
   - **Riesgos aceptados:** las decisiones de revisión con estado `riesgo_aceptado` de los cambios cerrados, con su motivo y quién las tomó; separados según el cambio que los trajo siga teniendo requisitos vigentes o no.
   - **Límites declarados:** los de los informes de revisión de los cambios cerrados, agrupados igual.
2. **Determinista:** las mismas entradas dan los mismos bytes; no lleva fecha ni HEAD. Una línea de cabecera guarda la huella de lo que resume.
3. **`resumen --verificar`** dice si el resumen falta o quedó viejo respecto de los registros, sin escribir. `--salida RUTA` lo escribe en otro lugar (por ejemplo un `RESUMEN.md` para leer en GitHub).
4. **Se actualiza solo al cerrar y al archivar**, que son los momentos en que cambia lo vigente.
5. El veredicto que muestra es el registrado al cerrar cada cambio, con el cambio y la fecha, y lo dice: no es una corrida nueva.
6. `.factory/resumen.md` queda fuera de la huella del producto (como todo `.factory/`): generarlo no vence ninguna revisión. Este repositorio queda con su resumen al día.

## Out of scope

- Una corrida nueva de Oracle sobre todos los requisitos vigentes (necesita hechos de todos los sensores juntos: tarea `hechos-varios`).
- Resúmenes escritos por un modelo (tarea `resumen-llm`) y el servidor MCP (tarea `factory-mcp`).
- Los 6 cambios viejos que nunca se cerraron: aparecen como abiertos, con lo que les falta.

## Human decisions

Respondidas por Brian el 2026-10-07:

1. **Dónde:** *`.factory/resumen.md`*, con `--salida RUTA` para volcarlo en otro lugar.
2. **Cuándo se actualiza:** *al cerrar y al archivar*; `resumen --verificar` dice si quedó viejo.
3. **Riesgos y límites:** *todos los de cambios cerrados, separando los de cambios con requisitos vigentes de los históricos*.
4. **Veredicto:** *el del cierre, con fecha y cambio*, diciendo que no es una corrida nueva.

Decidido por el agente, a revisar con la spec: la vista es corta (sin escenarios; enlaza la spec consolidada) y no lleva fecha ni HEAD, para que regenerarla sin cambios no ensucie Git. El diseño tomó como borrador la propuesta de Agy2 (Gemini), guardada en la tarea.
