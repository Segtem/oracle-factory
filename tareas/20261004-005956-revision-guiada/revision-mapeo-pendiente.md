# Candidato actualizado para revisión humana

Pendiente de análisis y decisión humana. Candidato: `5b54dc88fc5d6d4bf1e3768d9ba423032eb0f1e8`, en la rama `tarea/20261004-005956-revision-guiada` y el checkout estable `/home/workstation/Dev/_revisiones/factory-revision-guiada-5b54dc8`.

## Cambio y evidencia

Se asociaron los siete requisitos a la medida de su mismo sufijo y a `factory_revision_guiada.corrida_completa`, mediante `fabrica.py medir`. Se conservan límites explícitos `sin_medir`. La continuidad solicitada por el usuario habilita aplicar el mapeo presentado; no registra revisión aprobada ni cierre.

- [Mapeo aplicado](../../openspec/changes/20261004-005956-revision-guiada/medicion-propuesta.md).
- [Sensor del candidato](evidencia-mapeo/resultado.json): 66 pruebas y 18 casos G1–G8 pasan; fuentes estables.
- [Cobertura Oracle](evidencia-mapeo/oracle-cobertura.txt): siete requisitos parciales, con ambas medidas cumplidas. No hay juicio aprobado de Factory.
- [Continuidad de fuentes](evidencia-mapeo/continuidad.json): los 31 archivos enumerados por el sensor son idénticos a los del candidato de implementación `109e2b5`.
- [Ejecución descartada](evidencia-mapeo-descartada/LEEME.md): cambio de HEAD durante la primera corrida; no se utiliza como evidencia favorable.

## Alcance de Clue

Clue rechazó un paquete único desde `65e6815` porque el archivo de contexto anterior supera su límite de 256000 bytes. Se conserva el análisis preparatorio en dos paquetes, sin afirmar que uno contenga todo:

1. [Implementación: 65e6815 → 109e2b5](contexto-clue-109e2b5-durable.json), con el [dossier original](revision-pendiente.md).
2. [Mapeo: b89340f → 5b54dc8](contexto-clue-5b54dc8-durable.json): once archivos, cero omisiones. Los paquetes originales, con ruta en /tmp, quedan como histórico: mismo diff y contextos.

El commit intermedio `b89340f` archiva evidencia y documentos pendientes. Sus adjuntos siguen disponibles en Git y deben inspeccionarse si se usan para sustentar la revisión. Ambos paquetes son contexto, no informes. La comparación de fuentes y la nueva ejecución apoyan la continuidad del producto, sin sustituir la evaluación del revisor sobre el candidato actual.

## Acción humana pendiente

Revisar implementación, suficiencia del mapeo y evidencia sobre `5b54dc8`; prestar atención a los puntos del dossier original y a que los conteos sólo acreditan los casos seleccionados. Evaluar la claridad de la guía con una persona principiante antes de afirmar esa propiedad. El análisis y la identidad o competencia de los actores no se prueban con fixtures.

La CLI creó originales pendientes en:

```text
/home/workstation/Dev/_revisiones/factory-revision-guiada-5b54dc8/tareas/20261004-005956-revision-guiada/revisiones/preparacion-avpb2b64/informe.json
/home/workstation/Dev/_revisiones/factory-revision-guiada-5b54dc8/tareas/20261004-005956-revision-guiada/revisiones/preparacion-avpb2b64/decisiones.json
```

Copias de consulta: [informe](revision-mapeo-pendiente/informe.json) y [decisiones](revision-mapeo-pendiente/decisiones.json). Completar con observaciones reales; después calcular el SHA-256 del informe y resolver sus hallazgos. La persona elige `aprobar` o `cambios` y confirma el registro mediante `revision --formato guiado` en ese checkout. Si cambia el producto, debe renovarse el contexto antes de registrar.

No se encontró CodeRabbit instalado. No se envió el código a un servicio externo. El próximo paso requiere el informe del revisor y la decisión humana previstos por AGENTS.md; la tarea permanece abierta.
