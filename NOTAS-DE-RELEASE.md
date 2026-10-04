# Oracle Factory 0.1.0a3

- Inicio guiado: `nuevo --con-ejemplo notas` prepara ejemplo, propuesta, spec y reglas; rechaza destinos existentes antes de crear una tarea.
- `listar` recupera IDs completos y fases de cambios Factory.
- `medir ID --listar` consulta requisitos y medidas; `--requisito` y `--medida` hacen asociaciones explícitas validadas por el Oracle publicado.
- Se conserva `sin_medir` por defecto; `--sin-medir` declara un límite y `--quitar-sin-medir` lo retira explícitamente. Cambiar asociaciones invalida revisión y juicio anteriores.
- Conserva archivos ante sintaxis/medidas inválidas, usa reemplazo atómico y detecta cambios de entradas antes del guardado. El bloqueo coordina operaciones medir de Factory; no bloquea editores externos.
- `init` conserva configuración/ignores propios y explica el siguiente paso de Factory. Guía sin copias ni edición de indentación, con IDs de cambio/requisito recuperados de la CLI.
- Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11.

## Distribución y publicación

El release de GitHub adjunta wheel, sdist y SHA256SUMS. La subida de 0.1.0a3 a PyPI queda a cargo del mantenedor. El sitio usa el wheel del release para que el recorrido nuevo funcione mientras esa subida está pendiente.

```bash
uv publish dist/oracle_factory-0.1.0a3-py3-none-any.whl dist/oracle_factory-0.1.0a3.tar.gz
```

La evidencia exacta de pruebas, wheel instalado y guía se guarda en las tareas `20261004-005956-inicio-guiado` y `20261004-005956-elegir-medidas`. Confirmaciones de pruebas son fixtures en proyectos temporales; no aprueban el cierre de estos cambios reales. Verificación en Linux, sin piloto humano ni ejecución de Windows/macOS.

# Oracle Factory 0.1.0a2

- Migra la dependencia a `oracle-task==0.2.0` y resuelve el comando `tasks` desde esa distribución.
- Conserva IDs, carpetas de tareas y decisiones humanas. Actualiza la portada y la guía desde cero.
- Oracle continúa fijado en 0.38.1; no hace falta esperar otro paquete para instalar este corte.
- Publicado en PyPI; hashes wheel/sdist verificados contra el release y ejemplo completo probado desde una instalación nueva. Factory 0.1.0a1 depende del paquete antiguo. Trackertast se archivó, sin borrar sus versiones; para instalaciones nuevas usar Oracle Task y Factory 0.1.0a2 o posterior.

```bash
uv publish dist/oracle_factory-0.1.0a2-py3-none-any.whl dist/oracle_factory-0.1.0a2.tar.gz
```

La tarea `20261003-185925-migrar-task` registra la validación del corte.

# Oracle Factory 0.1.0a1

Primer corte alpha instalable, preparado para publicación manual en PyPI.

- Comando `oracle-factory`, Python >=3.11; Oracle 0.38.1 y Trackertast 0.1.0 como dependencias del mismo entorno.
- `--proyecto` selecciona la carpeta de trabajo; por defecto usa el directorio actual.
- `init` inicializa sin reemplazar configuración; `ejemplo notas` copia los recursos incluidos sin sobrescribir.
- Conserva aprobación de alcance, importación, revisión humana, evidencia vigente y cierre humano.
- Web pixel art y guía desde cero, con capacidades disponibles y futuras diferenciadas.

## Validación

Suite Python y ejemplo completo mediante el wheel instalado, fuera del checkout y sin ejecutables globales Oracle/Trackertast. Validación de wheel/sdist, metadata y recursos. Los resultados exactos del corte se registran en la tarea `20261002-234439-dist-uv`.

## Límites

Alpha: no genera productos ni coordina agentes automáticamente. Clue es independiente y todavía no está integrado. Las confirmaciones registran al operador; no autentican por sí solas su identidad. La prueba de instalación se realiza en Linux. Las decisiones humanas reales no se simulan para cerrar las tareas de este proyecto.

## Publicación manual en PyPI

El release adjunta wheel, sdist y SHA256SUMS. Descargar esos artefactos y comprobar sus hashes antes de publicar. Desde este checkout, los mismos archivos probados quedan en `dist/`:

```bash
uv publish dist/oracle_factory-0.1.0a1-py3-none-any.whl dist/oracle_factory-0.1.0a1.tar.gz
```

El comando usa las credenciales que configure el mantenedor. Este release no implica que la versión ya esté disponible en PyPI. Tras subirla, comprobar `uvx --from oracle-factory==0.1.0a1 oracle-factory --version` en un entorno limpio.
