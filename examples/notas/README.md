# Un primer cambio de notas

Este ejemplo acompaña `site/desde-cero.html`. Es una regla mínima de validación, sin interfaz ni base de datos. La implementación viene escrita para poder concentrarse en el flujo de la POC.

- `proposal.md` y `spec.md`: copiar su contenido al cambio creado con `fabrica.py nuevo --capacidad notas` y revisarlo antes de aprobar.
- `notas.py`: implementación de la regla.
- `test_notas.py`: tres casos ejecutables.
- `sensor.py`: observa los resultados y escribe hechos para Oracle.
- `catalogos/`: reglas completas para copiar a `catalogos/` del proyecto. En el requisito importado, reemplazar `sin_medir` por `medido_por notas.casos_ejecutados, notas.resultados`, conservando los cuatro espacios iniciales.

Desde la raíz de Factory:

```sh
uv run --no-project --python 3.13 python -m unittest discover -s examples/notas -p "test_*.py" -v
uv run --no-project --python 3.13 python examples/notas/sensor.py --salida .factory-demo/hechos.json
```

El sensor observa exactamente los tres casos declarados. Las medidas no prueban propiedades fuera de ellos ni verifican por sí mismas que un sensor sea correcto; su código y la elección de casos también requieren revisión.
