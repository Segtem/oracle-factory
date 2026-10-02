# Oracle Factory — prueba de concepto

Una factory que coordina herramientas sin quitarle decisiones a la persona. Esta POC une **OpenSpec** (intención y requisitos), **trackertast** (trabajo y bloqueos), un revisor de diff como **CodeRabbit** (hallazgos) y **Oracle** (veredicto reproducible sobre evidencia declarada).

Es una CLI local y un flujo visible en Git. No hace commits ni publica ramas por cuenta propia. La aprobación de alcance, la resolución de hallazgos y el cierre son acciones humanas.

## Flujo probado

1. `python3 fabrica.py nuevo --capacidad <slug> "<pedido>"` crea una tarea y el paquete OpenSpec enlazado. La persona edita la propuesta, la spec y las tareas.
2. `python3 fabrica.py aprobar-spec <id>` muestra qué se aprueba y exige escribir `APROBAR ESPECIFICACION <id>`. El agente espera; no puede aceptar por la persona.
3. `python3 fabrica.py importar <id>` llama al importador real de Oracle. Los requisitos nacen **sin medir**. Persona y agente acuerdan qué se puede medir; la persona crea o revisa las medidas.
4. Implementar y probar. Abrir el PR; CodeRabbit u otro revisor comenta el diff. Guardar su informe en el paquete OpenSpec. Una persona registra decisión, hallazgos pendientes y revisor con `fabrica.py revision`.
5. `python3 fabrica.py juzgar <id> --con <hechos.json>` exige cobertura completa de los requisitos importados y corre `oracle cobertura --con`. Un requisito parcialmente medido bloquea el paso.
6. `python3 fabrica.py cerrar <id>` sólo ofrece cerrar si la revisión fue aprobada, no quedan hallazgos abiertos y Oracle salió 0. La persona confirma escribiendo `CERRAR <id>`. Trackertast queda cerrado con referencia a la evidencia.

En todo momento se puede ver el estado con `python3 fabrica.py estado <id>`. Los documentos OpenSpec son archivos comunes editables por una persona.

## Ejemplo mínimo

El repositorio incluye una tarea de demostración (`20261002-204916-validar-el-flujo`) detenida antes de la aprobación. Completá sus TODO y usá el id impreso por Trackertast; no hay aprobación ni medición simulada.


```bash
python3 fabrica.py nuevo --capacidad gestor-de-notas "Rechazar títulos vacíos"
# Editar proposal.md, specs/gestor-de-notas/spec.md y tasks.md
python3 fabrica.py aprobar-spec <id-impreso>
python3 fabrica.py importar <id-impreso>
```

Luego crear medidas desde cada escenario con `oracle medida nueva <id-medida> --escenario-de <spec.md> "<escenario>" --requisito <requisito>`. Revisar `oracle cobertura`: hasta mapear todos los requisitos, la factory no acepta evidencia ni deja cerrar.

## Alcance y límites de esta POC

- Usa los comandos instalados de Oracle y trackertast; no implementa copias de sus reglas.
- No instala ni invoca CodeRabbit. Recibe su informe exportado o pegado y hace explícita la decisión humana. El siguiente paso sería conectar el estado del PR y sus checks cuando el repo remoto esté operativo.
- Oracle evalúa hechos que produce un sensor; no lee el código para demostrar cualquier afirmación. La cobertura completa de una spec requiere criterio humano y medidas defendibles.
- No archiva automáticamente el cambio OpenSpec ni modifica código del producto.

## Pruebas

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```
