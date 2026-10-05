# Candidato para revisión humana

Estado: pendiente. Este documento organiza la entrega; no es un informe de revisión ni una aprobación.

- Candidato del producto: `109e2b579ec29c3bc87ba30c92599f81c9a6a79f`.
- Base del diff: `65e6815`, contrato presentado.
- Rama: `tarea/20261004-005956-revision-guiada`.
- Checkout estable: `/home/workstation/Dev/_revisiones/factory-revision-guiada-109e2b5`.
- [Contexto de Clue](contexto-clue-109e2b5-durable.json) (el original con ruta en /tmp, [contexto-clue-109e2b5.json](contexto-clue-109e2b5.json), queda como histórico; mismo diff y contextos), sin omisiones.
- [Resultado del sensor](evidencia/resultado.json), [suite completa](evidencia/suite.txt), [trazas del contrato](evidencia/trazas.json) y [hechos](evidencia/hechos.json).
- [Reglas propuestas evaluadas por Oracle](evidencia/oracle-medidas-propuestas.txt) y [cobertura real](evidencia/oracle-cobertura.txt).

## Qué cambió y cómo se verificó

`revision-preparar` crea dos documentos pendientes. `revision --formato guiado` valida el informe y decisiones vinculadas, calcula abiertos, exige confirmación humana y archiva nuevas copias. Estado/cierre comprueban sus hashes. El formato libre conserva su flujo, requiere conteo explícito y se muestra como declaración sin validación estructural; los registros anteriores se rotulan históricos.

Pasaron 66 pruebas: 48 regresiones existentes y 18 casos nuevos de G1–G8. Hay pruebas de cancelación, cambios durante lectura/confirmación, entradas malformadas, revisión incompleta, resoluciones inconsistentes, conservación ante fallas y un recorrido completo de CLI con Oracle/Task reales en un fixture temporal. El sensor exige todos los nombres exactos sin omisiones/duplicados y guarda fuentes y huellas del candidato.

Las ocho reglas propuestas pasan sobre esos hechos. Los siete requisitos reales siguen sin medir porque el mapeo aún no fue elegido. Ese resultado de reglas no se registró como gate Oracle de Factory. La calidad del análisis, identidad de actores y claridad humana no se prueban con los fixtures.

## Puntos para quien revisa

- Comprobar que los campos pendientes nunca se transformen en cero hallazgos o decisiones por defecto.
- Evaluar validación estricta de JSON, IDs, fechas, rutas declaradas y vínculo exacto al informe.
- Revisar qué comprueban las revalidaciones y qué carreras con editores externos quedan fuera de una transacción.
- Comprobar conservación de documentos/registros ante fallas y el mensaje de nota pendiente después de registrar.
- Revisar compatibilidad libre/histórica y el alcance real de las medidas propuestas.
- Evaluar la guía con una persona principiante antes de afirmar claridad o facilidad de uso.

## Documentos pendientes para aplicar el propio flujo

Se ejecutó `revision-preparar` sobre el candidato, sin registrar revisión ni decisiones. Los originales están en:

```text
/home/workstation/Dev/_revisiones/factory-revision-guiada-109e2b5/tareas/20261004-005956-revision-guiada/revisiones/preparacion-znbsxziu/informe.json
/home/workstation/Dev/_revisiones/factory-revision-guiada-109e2b5/tareas/20261004-005956-revision-guiada/revisiones/preparacion-znbsxziu/decisiones.json
```

Se conservan copias de consulta: [informe pendiente](revision-pendiente/informe.json) y [decisiones pendientes](revision-pendiente/decisiones.json). Los campos humanos y el hash del informe siguen en null. La persona revisora debe completarlos con observaciones reales y la persona responsable debe decidir antes de registrar.

Clue puede ayudar a validar un informe externo sobre su paquete; ese informe tiene un schema distinto. La preparación de contexto aquí fue manual con Clue 0.1.0a1, no una integración automática agregada a Factory.

El commit posterior que archiva estos documentos es distinto del candidato probado. Si cambia el producto o el contexto que se desea aprobar, corresponde un candidato y una revisión nuevos. El checkout estable conserva este candidato; si se elimina, habrá que preparar nuevamente el paquete de Clue en el nuevo checkout.
