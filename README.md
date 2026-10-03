# Oracle Factory — prueba de concepto

La visión de Oracle Factory es coordinar agentes y herramientas para producir software completo: desde una necesidad aceptada hasta código, pruebas, revisión y entrega. La persona decide el alcance, resuelve hallazgos y acepta la entrega.

Hoy existe una POC de CLI: genera documentos con formato **OpenSpec**, usa **trackertast** para tareas e importa requisitos y evalúa evidencia con **Oracle**. La implementación del producto y las pruebas se ejecutan por fuera de la CLI. Recibe informes manuales de revisión; **Oracle Clue** todavía es un esbozo y CodeRabbit es una alternativa externa.

Es una CLI local y un flujo visible en Git. No hace commits ni publica ramas por cuenta propia. La aprobación de alcance, la resolución de hallazgos y el cierre son acciones humanas.

## Flujo de la POC

1. `python3 fabrica.py nuevo --capacidad <slug> "<pedido>"` crea una tarea y el paquete OpenSpec enlazado. La persona edita la propuesta, la spec y las tareas.
2. `python3 fabrica.py aprobar-spec <id>` muestra la propuesta y la spec que se aprueban y exige escribir `APROBAR ESPECIFICACION <id>`. El agente espera; no puede aceptar por la persona.
3. `python3 fabrica.py importar <id>` llama al importador real de Oracle. Los requisitos nuevos nacen **sin medir**; cada tarea y versión de spec usa su propio dominio para no heredar medidas de otra promesa. Persona y agente acuerdan qué se puede medir; la persona crea o revisa las medidas.
4. Implementar y probar. Abrir el PR; CodeRabbit u otro revisor comenta el diff. Guardar su informe en el paquete OpenSpec. Una persona registra decisión, hallazgos pendientes y revisor con `fabrica.py revision`.
5. `python3 fabrica.py juzgar <id> --con <hechos.json>` exige cobertura completa de los requisitos importados y corre `oracle cobertura --con`. Un requisito parcialmente medido bloquea el paso. Cada requisito importado debe tener juicio explícito de cumplimiento: un exit code 0 con «sin juicio» o fallas en sombra no habilita el cierre.
6. `python3 fabrica.py cerrar <id>` sólo ofrece cerrar si la revisión fue aprobada, no quedan hallazgos abiertos y todos los requisitos importados se cumplen con evidencia vigente. La persona confirma escribiendo `CERRAR <id>`. Trackertast queda cerrado con referencia a la evidencia.

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
- No instala ni invoca CodeRabbit. Recibe su informe exportado o pegado y hace explícita la decisión humana. El siguiente paso sería conectar el estado del PR y sus checks en una futura integración. El remoto ya existe; la integración automática todavía no.
- Oracle evalúa hechos que produce un sensor; no lee el código para demostrar cualquier afirmación. La cobertura completa de una spec requiere criterio humano y medidas defendibles.
- No archiva automáticamente el cambio OpenSpec ni modifica código del producto.

## Preparación y vigencia de la evidencia

Usar Python 3, Git y los comandos `oracle` y `tasks` en PATH. La integración se probó con Oracle 0.38.1 y Trackertast 0.1.0. No se requiere la CLI de OpenSpec para importar estas specs a Oracle; esta POC no valida el ciclo completo del CLI OpenSpec.

Antes de registrar la revisión, terminar los cambios y crear el commit del producto. La CLI guarda HEAD y una huella de archivos versionados y nuevos no ignorados. Si cambia el commit, código, spec, medidas o evidencia, repetir la revisión/juicio. Los registros de tareas y los informes generados en el paquete no se incluyen en la huella del producto, pero los informes se verifican por hash propio. Los archivos ignorados y dependencias externas quedan fuera de esa huella; los submódulos no están soportados.

Renovar la aprobación de propuesta/spec invalida la importación, la revisión y el veredicto anteriores. Las aprobaciones antiguas sin huellas de ambos documentos requieren renovación. Las confirmaciones interactivas son un protocolo del operador: registran el usuario del sistema, sin autenticar de forma independiente a una persona.

## Pruebas

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

La suite incluye regresiones con Git real y una integración temporal de creación de tarea, importación Oracle, rechazo de evidencia insuficiente, juicio y cierre. Las aprobaciones de esa prueba son fixtures; no aprueban ningún cambio real.

## Web y guía desde cero

La [portada interactiva](site/index.html) compara vibe coding, el ciclo de desarrollo, el trabajo guiado por especificaciones y Oracle Factory con un mismo ejemplo. El recorrido pixel art muestra las decisiones humanas y una vuelta de revisión, corrección y nuevas pruebas. Es una demostración visual; no ejecuta agentes ni registra aprobaciones reales.

La [guía desde cero](site/desde-cero.html) instala Oracle 0.38.1 y Trackertast 0.1.0 desde PyPI con uv y recorre el [ejemplo de notas](examples/notas) hasta el cierre local. Factory todavía se ejecuta desde este checkout; su distribución instalable y la selección de otro proyecto se siguen en la tarea `20261002-234439-dist-uv`.

Para ver ambas páginas:

```bash
python3 -m http.server 8765 --directory site
```

Abrir <http://localhost:8765>. También funcionan abriendo `site/index.html` sin conexión. El sitio no tiene dependencias externas en tiempo de ejecución. GitHub Actions publica `site/` en GitHub Pages desde `main`.

Para comprobar la web en Chromium, instalar la dependencia de desarrollo Playwright y ejecutar:

```bash
npm install --no-save --package-lock=false playwright@1.62.1
node tests/test_site.cjs
```

La prueba usa `/usr/bin/chromium` por defecto; se puede indicar otro ejecutable con la variable `CHROMIUM`. Comprueba los controles, las decisiones, el teclado, movimiento reducido, adaptación móvil, enlaces y funcionamiento sin red. La suite de Python incluye el ejemplo de la guía con Oracle, Trackertast y Git reales, aislado en una carpeta temporal. Requiere los comandos `oracle` y `tasks` disponibles; sin ellos esa integración se omite.
