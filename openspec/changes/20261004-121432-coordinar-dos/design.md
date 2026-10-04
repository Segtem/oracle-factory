# Diseño propuesto y diagnóstico

## Fuentes inspeccionadas

Lectura local el 2026-10-04, sin cambios pendientes en los repositorios fuente al inspeccionarlos:

| Componente | Revisión | Fuentes relevantes |
| --- | --- | --- |
| Factory 0.1.0a3 | `5907a3e` | `oracle_factory/cli.py`: guardar, contexto_producto, pendientes_actuales, bloqueo_medidas, cerrar; README |
| Oracle Task 0.2.0 | `a44fa45a954e59d4fc657b36aecea0eea65431dd` | `../trackertast/oracle_task/tasks.py`: guardar_documento_atomico, crear_carpeta_tarea_atomica; `docs/tareas.md` |
| Oracle Clue 0.1.0a1 | `6b93a9b3f85b2a79d50f4b72f6d418019753dc89` | `../oracle-clue/oracle_clue/cli.py`: prepare, validate_report, validate_triage, write_bundle; README |

El diagnóstico inicial se basó en código/documentación. Tras la aceptación se ejecutaron los casos descritos abajo; el piloto humano sigue pendiente.

## Qué resuelve cada pieza

| Pieza | Disponible | Límite que el protocolo debe cubrir |
| --- | --- | --- |
| Task | Tarea por carpeta, notas, adjuntos, metadatos adicionales, referencias/grafo y hechos Git; creación local con mkdir exclusivo | Reemplazar TAREA.md atómicamente evita escrituras parciales, pero no serializa dos escritores; IDs desambiguados en un directorio no son una reserva entre clones; referencias no son dependencias validadas |
| Clue | Contexto de base/HEAD, huellas, validación del informe y triage separado | No asigna tareas ni aprueba; el paquete incluye ruta absoluta del repo y se compara completo al validar; no es portable sin más entre checkouts |
| Factory | Spec aceptada, importación, asociación de medidas, revisión y juicio ligados a HEAD/huella del producto | guardar escribe factory.json sin bloqueo general; medir tiene un lock local por cambio, no un lock distribuido ni para todas las mutaciones; notas del tracker y estado no son una transacción |
| Git | Ramas, commits e intercambio de contribuciones | No evita conflictos semánticos ni acredita revisión o autoridad humana |
| Oracle | Evalúa hechos respecto de medidas elegidas | No coordina escritores ni demuestra propiedades sin medir; Task facts no prueba corrección del producto |

La huella de Factory abarca el checkout: excluye tareas y algunos registros generados, pero incluye propuestas/specs y otros archivos no ignorados. Trabajar simultáneamente en cambios distintos dentro del mismo checkout puede invalidar gates del otro frente aun sin tocar el mismo código. Cambiar HEAD también los invalida. La huella no debe reducirse artificialmente para conservar un verde.

## Protocolo mínimo recomendado

1. A y B acuerdan reparto, dependencias y quién integra. Los nombres reales quedan pendientes para el piloto. La asignación se comunica y confirma: Git por sí solo no es una reserva inmediata.
2. Cada cambio conserva su tarea/OpenSpec. Los campos adicionales y el cuerpo de Task pueden registrar responsable, sesión y alcance sin modificar su parser. Un solo escritor actualiza TAREA.md/factory.json de cada copia activa; los otros entregan notas/informes con nombres distintos para incorporación acordada.
3. Cada frente usa rama y checkout propios. Un mismo cambio sólo tiene un ejecutor que muta sus registros; el otro puede revisar una instantánea. Si requiere dos implementaciones independientes, se dividen en cambios enlazados y se acuerda una interfaz/base común.
4. Antes de editar una ruta/interfaz compartida, detener sólo el trabajo afectado, acordar orden o nuevo reparto y anotarlo. Sin conectividad se puede explorar en aislamiento, pero no asumir que una asignación local quedó aceptada globalmente.
5. Al entregar, confirmar el producto y adjuntar el relevo. Confirmar recepción antes de transferir escritura. Conservar trabajo pendiente; nunca limpiar el checkout ajeno como método de coordinación.
6. B y su agente revisan el candidato de A, o viceversa. Clue se ejecuta en un checkout estable, con base explícita y salida nueva fuera del repo revisado. La otra persona puede leer ese paquete; su validación posterior se realiza contra el mismo checkout. Si se usa otra ruta, se genera otro paquete y un informe vinculado a él.
7. Archivar paquete, informe y triage sin sobrescribir versiones. Elegir el lugar y momento de archivado antes de fijar el candidato final: agregar contexto al producto o crear un commit posterior cambia su identidad. Guardar adjuntos bajo tareas evita incluirlos en la huella de archivos de Factory, pero un nuevo commit igualmente cambia HEAD. Conservar siempre el hash del informe usado por el triage.
8. El integrador incorpora entregas de una en una en su checkout, resuelve conflictos con las personas afectadas y verifica también incompatibilidades sin conflicto textual. Los estados Factory provenientes de ramas son antecedentes: no fusionar JSON eligiendo el estado más avanzado ni reutilizar sus verdes. Consultar estado, reconciliar registros con historia y renovar los gates del candidato resultante.
9. Sobre el commit final, ejecutar pruebas/sensor, preparar revisión, registrar la decisión humana y correr Oracle según las medidas acordadas. Factory hoy no ejecuta el sensor ni prueba procedencia del JSON; registrar comando y versión observada conserva trazabilidad, sin adjudicarle una garantía automática nueva.
10. La persona decide cierre mediante Factory. El commit que guarda registros/cierre puede cambiar HEAD otra vez; documentar cuál fue el commit del producto juzgado y cuál guardó el cierre, sin presentarlos como idénticos ni auto-renovar evidencia.

No se proponen comandos `claim`, `assign`, `handoff` ni locks distribuidos en este corte. Las convenciones de escritor e integrador son acuerdos humanos. Si el piloto necesita enforcement, abrir propuestas en Task (actualizaciones concurrentes), Clue (portabilidad de paquetes) o Factory (coordinación general), con sus propias aprobaciones.

## Matriz de comprobación propuesta

| Caso | Observación requerida | Requisito |
| --- | --- | --- |
| C1: frentes disjuntos | HEAD, índice y archivos de B permanecen intactos mientras A edita; ambos aportes llegan al candidato | aislamiento y sincronizacion explicitos |
| C2: solapamiento | Registro de conflicto de ruta o interfaz y decisión; sin sobrescritura silenciosa | reparto explicito del trabajo |
| C3: relevo/interrupción | Plantilla completa, recepción y trabajo pendiente conservado; recuperación de lock verificada | relevo recuperable |
| C4: clones divergentes | Colisión/identidades reconciliadas con referencias conservadas antes de integrar | aislamiento y sincronizacion explicitos |
| C5: revisión obsoleta/otra ruta | Clue rechaza paquete incompatible; nuevo paquete/informe o validación en origen documentados | revision vinculada a una version |
| C6: merge/rebase tras revisión | Factory señala gates obsoletos y el cierre no avanza; renovación sobre candidato final | integracion serializada y evidencia vigente |
| C7: contrato/medidas cambiados | Aceptación/importación o revisión/juicio se renuevan según corresponda | integracion serializada y evidencia vigente |
| C8: falta aprobación/cobertura | Cierre rechazado y tareas reales abiertas; fixtures de aprobación aislados | integracion serializada y evidencia vigente |
| C9: arnés y piloto | Casos declarados = ejecutados, artefactos/errores registrados; informe humano separado | demostracion reproducible con limites |

Tras la aceptación se asociaron medidas parciales del catálogo `factory_colaboracion`, elegidas por el agente para los casos observados. Cada requisito enlaza su medida de casos y `corrida_completa`; el sensor comprueba identidad, unicidad, completitud, hashes y estabilidad de sus fuentes. La pertinencia y suficiencia requieren revisión humana. Los seis requisitos conservan `sin_medir`, porque el arnés no observa acuerdos reales, criterio humano ni experiencia de uso.

## Entregable implementado

- `docs/colaboracion.md`, enlazada desde README, y cuatro plantillas bajo `docs/plantillas/colaboracion/`.
- `tools/verify_collaboration.py`: nueve casos con comandos reales y repositorios temporales, versiones fijadas, artefactos y hashes. Se ejecuta con Python que tenga Oracle 0.38.1 y Task 0.2.0; Clue 0.1.0a1 se selecciona con `--clue`.
- `tests/test_collaboration_sensor.py`: regresiones ante caso omitido/duplicado/desconocido/fallido, artefactos alterados/ausentes/externos y relevo incompleto.
- Catálogos y requisitos con asociaciones parciales mediante la CLI `medir`. El resultado Oracle se conserva como observación parcial, sin registrar un gate verde.

C4 observa clones locales que divergen sobre la misma tarea y la conciliación de ambos aportes. No simula ni declara probada la migración completa de dos cambios Factory nuevos con IDs colisionados; esa parte está explicitada como sin medir. C3 controla un proceso fixture que ya terminó, nunca identifica ni mata sesiones reales. Los acuerdos y triage de los casos son fixtures; no sustituyen el piloto.

Los artefactos se guardan bajo la tarea, separados del candidato del producto. El commit candidato y el de archivo posterior se registrarán por separado. Se prepara contexto de Clue para una revisión humana posterior; no se registra como informe ni aprobación.

## Relación con trabajo existente

- `20261004-005956-evidencia-origen`: procedencia del sensor; este protocolo declara su límite y no implementa esa mejora.
- `20261004-005956-revision-guiada`: consultar al diseñar la experiencia de revisión; no asumir integración de Clue ya disponible.
- Cada futura modificación de herramientas hermanas necesita tarea/spec propias en su repositorio; esta propuesta reside en Factory.
