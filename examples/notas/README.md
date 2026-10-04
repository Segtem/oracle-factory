# Un primer cambio de notas

Este ejemplo acompaña a `site/desde-cero.html`. Es una regla mínima de validación, sin interfaz ni base de datos. La implementación viene escrita para poder concentrarse en el flujo de la POC.

Al crear el cambio con `oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"`:
- Se infiere automáticamente la capacidad `notas`.
- Se copia este ejemplo completo en `examples/notas`.
- Se copian `proposal.md` y `spec.md` al paquete del cambio (`openspec/changes/<id>/`).
- Se copian las reglas a `catalogos/` (`notas.casos_ejecutados.oracle` y `notas.resultados.oracle`).
- Rechaza destinos existentes antes de crear la tarea; no sobrescribe archivos y evita pasos manuales de copia.

Archivos del ejemplo:
- `proposal.md` y `spec.md`: propuesta y especificación con tres escenarios (título vacío, espacios y texto).
- `notas.py`: implementación de la regla de validación.
- `test_notas.py`: tres casos de prueba unitaria ejecutables.
- `sensor.py`: ejecuta la función, observa los resultados y escribe los hechos para Oracle.
- `catalogos/`: reglas de Oracle que evalúan casos ejecutados y resultados fallidos.

Para medir tras `oracle-factory importar <id>`:
- `oracle-factory medir <id> --listar`: muestra los requisitos importados del cambio y las medidas efectivas disponibles, con sus límites y fuentes.
- `oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir`: asocia las medidas al requisito de forma explícita y valida su existencia en el catálogo. Por defecto, `medir` conserva `sin_medir`; para quitarlo se exige `--quitar-sin-medir` explícito (o `--sin-medir "alcance pendiente"` para registrar cobertura parcial).
- Ya no es necesario editar la indentación a mano en el archivo `.requisito`, aunque sigue siendo texto plano editable si se necesita inspeccionar en el editor.
- Una asociación inválida no modifica los archivos; modificar la asociación invalida la revisión y el veredicto de Oracle previos. La especificación debe estar vigente.

Ejecución de pruebas y sensor:

```sh
uv run --no-project --python 3.13 python -m unittest discover -s examples/notas -p "test_*.py" -v
uv run --no-project --python 3.13 python examples/notas/sensor.py --salida .factory-demo/hechos.json
```

El sensor observa exactamente los tres casos declarados. Enlazar medidas no prueba por sí mismo su pertinencia ni el cumplimiento del requisito; el código del sensor, la elección de casos y los límites de las reglas requieren criterio y revisión humanos.
