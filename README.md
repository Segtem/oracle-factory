# Oracle Factory — 0.1.0a3 (alpha)

La visión de Oracle Factory es coordinar agentes y herramientas para producir software completo: desde una necesidad aceptada hasta código, pruebas, revisión y entrega. La persona decide el alcance, resuelve hallazgos y acepta la entrega.

Hoy existe una POC de CLI: genera documentos con formato **OpenSpec**, usa **oracle-task** para tareas e importa requisitos y evalúa evidencia con **Oracle**. La implementación del producto y las pruebas se ejecutan por fuera de la CLI. Recibe informes manuales de revisión; **Oracle Clue** prepara contexto y valida informes externos en su primer alpha; el análisis con IA sigue pendiente y CodeRabbit es una alternativa externa.

Es una CLI local y un flujo visible en Git. No hace commits ni publica ramas por cuenta propia. La aprobación de alcance, la resolución de hallazgos y el cierre son acciones humanas.

Para trabajar entre dos personas con sus agentes, consultá la [guía de colaboración](docs/colaboracion.md): reparto, checkouts separados, relevos, revisión con Clue e integración con evidencia vigente. Incluye plantillas y una demostración local; las asignaciones son acuerdos humanos y el piloto con personas se registra por separado.

En el checkout de desarrollo, la [revisión guiada](docs/revision-guiada.md) prepara informes pendientes, separa decisiones y calcula hallazgos abiertos. Todavía no está incluida en el release 0.1.0a3 enlazado abajo. El formato libre sigue disponible; este checkout exige `--hallazgos-abiertos` explícito al registrarlo.


## Instalación del corte alpha

El corte alpha 0.1.0a3 incorpora inicio guiado (`nuevo --con-ejemplo`), comando de medición explícita (`medir`) y listado de cambios de Factory (`listar`).

El wheel de esta versión se encuentra disponible en el [release de GitHub v0.1.0a3](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a3). La subida a PyPI está pendiente. En PyPI se encuentra actualmente la versión `0.1.0a2`, pero **no incluye** `nuevo --con-ejemplo`, `medir` ni `listar`. No se recomienda instalar 0.1.0a2 si se desea utilizar los comandos de este corte.

Para instalar el wheel desde el release oficial con `uv`:

```bash
uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task https://github.com/Segtem/oracle-factory/releases/download/v0.1.0a3/oracle_factory-0.1.0a3-py3-none-any.whl
uv tool update-shell
oracle-factory --version
oracle-factory --proyecto ./mi-proyecto init
oracle-factory --proyecto ./mi-proyecto nuevo --con-ejemplo notas "Comprobar el título de una nota"
```

Si uv advierte sobre conflicto porque los ejecutables `oracle` o `tasks` ya están instalados en tu sistema, podés instalar el mismo wheel sin `--with-executables-from`:

```bash
uv tool install --python 3.13 https://github.com/Segtem/oracle-factory/releases/download/v0.1.0a3/oracle_factory-0.1.0a3-py3-none-any.whl
```

Factory utiliza sus dependencias internas (`oracle-metalenguaje 0.38.1` y `oracle-task 0.2.0`) desde su entorno aislado y no requiere exponer sus binarios en el PATH global para operar.

`--proyecto` se coloca antes del subcomando; sin esa opción se usa la carpeta actual. `init` crea la estructura de Oracle, Oracle Task y OpenSpec, añade ignores para `.factory-demo/`, `__pycache__/` y `*.py[cod]` sin sobrescribir configuración existente y no crea commits ni aprobaciones. Git debe estar instalado. Python 3.11 o posterior.

Los archivos indicados con `--informe` y `--con` se interpretan desde el proyecto seleccionado; también aceptan rutas absolutas.

La [guía desde cero](https://segtem.github.io/oracle-factory/desde-cero.html) recorre el ejemplo de notas en un proyecto vacío sin clonar Factory. Para desarrollo desde el checkout, `python3 fabrica.py` conserva la misma interfaz y selección de proyecto.

El [release de GitHub](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a3) conserva los artefactos y sus hashes. El paquete sigue siendo experimental: no coordina agentes automáticamente ni integra todavía Clue.


## Flujo de la POC

1. `oracle-factory init`: inicializa Oracle, tareas y acuerdos; añade entradas necesarias a `.gitignore` sin sobrescribir la configuración del usuario. Los mensajes siguientes provienen de Factory.
2. `oracle-factory nuevo --con-ejemplo notas "<pedido>"`: crea la tarea y el paquete OpenSpec copiando el ejemplo entero a `examples/notas`, la propuesta y spec al cambio y las reglas a `catalogos/`. Verifica destinos antes de crear la tarea y rechaza destinos existentes sin sobrescribir archivos. (También está disponible `oracle-factory nuevo --capacidad <slug> "<pedido>"` para plantillas en blanco sin ejemplo).
3. `oracle-factory listar`: recupera únicamente los cambios de Factory del proyecto con su ID completo y fase actual.
4. `oracle-factory aprobar-spec <id>`: muestra la propuesta y la spec y exige escribir interactivamente `APROBAR ESPECIFICACION <id>`. El agente espera; no puede aceptar por la persona.
5. `oracle-factory importar <id>`: invoca al importador de Oracle. Los requisitos nuevos nacen **sin medir** y aislados por dominio para evitar herencias indebidas.
6. `oracle-factory medir <id> --listar`: muestra los requisitos importados del cambio y las medidas disponibles en el catálogo con sus límites y fuentes.
   `oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir`: asocia medidas explícitamente sin edición manual de indentación. Conserva `sin_medir` por defecto; para retirarlo exige `--quitar-sin-medir` explícito (o `--sin-medir "alcance pendiente"` para cobertura parcial). Una asociación inválida no modifica archivos; modificar la asociación invalida la revisión y el juicio previos. Enlazar medidas no prueba pertinencia ni cumplimiento por sí mismo.
7. Implementar y probar: los tests y el sensor se ejecutan por fuera de Factory.
8. `oracle-factory revision <id> --informe <ruta> --revisor "<nombre>" --decision aprobar --hallazgos-abiertos 0`: registra la revisión humana y su decisión, vinculadas al commit de Git actual.
9. `oracle-factory juzgar <id> --con <hechos.json>`: exige cobertura completa de los requisitos importados y corre Oracle sobre la evidencia aportada por el sensor. Un exit code 0 con «sin juicio» o fallas en sombra no habilita el cierre.
10. `oracle-factory cerrar <id>`: exige que todos los gates (spec, importación, revisión sin hallazgos abiertos y juicio verde) estén completos y vigentes. La persona confirma escribiendo `CERRAR <id>`.

En todo momento se puede consultar el estado con `oracle-factory estado <id>`.


## Ejemplo mínimo

En tu proyecto inicializado, creá un cambio con el ejemplo y aprobá la spec tras revisarla:

```bash
oracle-factory init
oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"
# Recuperar el ID impreso o con: oracle-factory listar
oracle-factory aprobar-spec <id>
oracle-factory importar <id>
oracle-factory medir <id> --listar
oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir
```

Si necesitás los comandos independientes `oracle` y `tasks`, usá la instalación con `--with-executables-from oracle-metalenguaje,oracle-task`. Luego podés consultar `oracle cobertura --proyecto .`: hasta mapear todos los requisitos, Factory no acepta evidencia ni permite cerrar.


## Alcance y límites de esta POC

- Usa los comandos instalados de Oracle y oracle-task; no implementa copias de sus reglas.
- No instala ni invoca CodeRabbit. Recibe su informe exportado o pegado y hace explícita la decisión humana. El análisis con IA sigue pendiente y Clue en su primer alpha prepara contexto y valida informes externos.
- Oracle evalúa los hechos aportados; Factory no ejecuta el sensor ni certifica que ese JSON provenga de la versión actual. No lee el código para demostrar cualquier afirmación. La cobertura completa de una spec requiere criterio humano y medidas defendibles.
- No archiva automáticamente el cambio OpenSpec ni modifica código del producto. No realiza git push ni publicación de ramas.
- El flujo se verificó en Linux; los comandos para Windows y macOS fueron revisados pero no cuentan con ejecución automatizada completa en esos sistemas. Las guías no sustituyen la dirección de una persona competente.


## Preparación y vigencia de la evidencia

Usar Python 3, Git y las herramientas instaladas. La integración se probó con Oracle 0.38.1 y Oracle Task 0.2.0. No se requiere la CLI de OpenSpec para importar estas specs a Oracle; esta POC no valida el ciclo completo del CLI OpenSpec.

Antes de registrar la revisión, terminar los cambios y crear el commit del producto. La CLI guarda HEAD y una huella de archivos versionados y nuevos no ignorados. Si cambia el commit, código, spec, medidas o evidencia, repetir la revisión/juicio. Los registros de tareas y los informes generados en el paquete no se incluyen en la huella del producto, pero los informes se verifican por hash propio. Los archivos ignorados y dependencias externas quedan fuera de esa huella; los submódulos no están soportados.

Renovar la aprobación de propuesta/spec invalida la importación, la revisión y el veredicto anteriores. Una asociación de medidas diferente invalida la revisión y el juicio. Las confirmaciones interactivas son un protocolo del operador: registran el usuario del sistema, sin autenticar de forma independiente a una persona.


## Pruebas

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

La suite incluye regresiones con Git real y una integración temporal de creación de tarea, importación Oracle, rechazo de evidencia insuficiente, juicio y cierre. Las aprobaciones de esa prueba son fixtures; no aprueban ningún cambio real.


## Web y guía desde cero

**[Abrir la web](https://segtem.github.io/oracle-factory/) · [Guía desde cero](https://segtem.github.io/oracle-factory/desde-cero.html)**

La [portada interactiva](site/index.html) compara vibe coding, el ciclo de desarrollo, el trabajo guiado por especificaciones y Oracle Factory con un mismo ejemplo. El recorrido pixel art muestra las decisiones humanas y una vuelta de revisión, corrección y nuevas pruebas. Es una demostración visual; no ejecuta agentes ni registra aprobaciones reales.

La [guía desde cero](site/desde-cero.html) recorre el [ejemplo de notas](examples/notas) hasta el cierre local con inicio guiado y comando `medir`.

Para ver ambas páginas localmente:

```bash
python3 -m http.server 8765 --directory site
```

Abrir <http://localhost:8765>. También funcionan abriendo `site/index.html` sin conexión. El sitio no tiene dependencias externas en tiempo de ejecución. GitHub Actions publica `site/` en GitHub Pages desde `main`.

Para comprobar la web en Chromium, instalar la dependencia de desarrollo Playwright y ejecutar:

```bash
npm install --no-save --package-lock=false playwright@1.62.1
node tests/test_site.cjs
```

La prueba usa `/usr/bin/chromium` por defecto; se puede indicar otro ejecutable con la variable `CHROMIUM`. Comprueba los controles, las decisiones, el teclado, movimiento reducido, adaptación móvil, enlaces y funcionamiento sin red.
