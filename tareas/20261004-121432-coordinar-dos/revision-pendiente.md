# Candidato preparado para revisión humana

Estado: pendiente. Este documento prepara la revisión; no es un informe de CodeRabbit, de Clue ni de otra persona, y no contiene una decisión de aprobación.

- Tarea: `20261004-121432-coordinar-dos`.
- Rama: `tarea/colaboracion-personas-agentes`.
- Base del diff: `a849025` (propuesta original).
- Candidato del producto: `4ceb4b075a50290d014e3d7ec4714774c4417d81`.
- Checkout estable del candidato: `/tmp/factory-colaboracion-revision-4ceb4b0`.
- [Contexto de Clue](contexto-clue-4ceb4b0.json), generado con Clue 0.1.0a1, sin omisiones.
- [Resultados y huellas del arnés](evidencia/resultado.json), [hechos](evidencia/hechos.json), [resumen de validación](evidencia/validacion.json) y [cobertura Oracle](evidencia/oracle-cobertura.txt).

El commit que archive esta evidencia será posterior al candidato. No cambia qué commit ejecutó la demostración ni convierte el archivo posterior en producto revisado. El paquete apunta al checkout estable; si se elimina esa carpeta, se deberá preparar nuevamente el contexto en otro checkout y vincularle el informe correspondiente.

## Resultado y alcance

La implementación entrega una guía de colaboración, cuatro plantillas y un arnés local de nueve casos. Reutiliza las CLI existentes; no agrega coordinación distribuida ni modifica código de Task, Clue o la CLI de Factory.

La suite Python completa pasó 48 pruebas. Los casos C1–C9 pasaron contra Oracle 0.38.1, Task 0.2.0 y Clue 0.1.0a1; el manifiesto registra los comandos, entradas, salidas, hashes y fuentes. Los informes, triage y aprobaciones del arnés están rotulados como fixtures y se ejecutaron sólo en repositorios temporales.

Oracle devuelve seis requisitos que cumplen sólo en lo medido. Todos conservan `sin_medir`. Las medidas se eligieron por el agente para vincular casos enumerados y exigir integridad de la corrida; su suficiencia queda a criterio humano. El piloto humano, la revisión aprobada y el cierre no se registraron.

## Puntos que debe evaluar quien revisa

- Si el reparto y el escritor único están expresados como acuerdos humanos y permiten avanzar en frentes independientes.
- Si el relevo distingue oferta y recepción confirmada y preserva archivos/índice ante interrupción.
- Si queda clara la diferencia entre un conflicto textual y una incompatibilidad de interfaces.
- Si la guía maneja correctamente la ruta del paquete de Clue, las decisiones separadas y la renovación de gates tras integrar.
- Si la evidencia respalda el alcance de cada medida. C4 prueba una tarea común divergente, no la migración completa de dos cambios nuevos con ID colisionado.
- Si los límites de procedencia de hechos, identidad de actores y experiencia humana son suficientes; ninguna de esas propiedades se certifica por un conteo de casos.

## Continuación de la revisión

La persona o su revisor produce el informe sobre este paquete, conserva sus hallazgos como `pendiente` y registra las decisiones humanas en un triage separado. Se puede validar con:

```bash
oracle-clue validar /ruta/informe.json --paquete /home/workstation/Dev/factory/tareas/20261004-121432-coordinar-dos/contexto-clue-4ceb4b0.json --repo /tmp/factory-colaboracion-revision-4ceb4b0 --triage /ruta/decisiones.json
```

Una corrección requiere nuevo candidato y revisión vigente. La decisión en Factory se registra después de resolver los hallazgos y comprobar el contexto aplicable; este paquete preparado no la reemplaza.

Para el piloto, completar [la hoja pendiente](piloto-pendiente.md) con los participantes reales. La pregunta por sus nombres e integrador quedó abierta en la conversación; no se inventaron asignaciones.
