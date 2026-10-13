# Trazabilidad por candidato

Para revisar el código de un cambio por promesa y no por archivo: qué líneas cambiadas del candidato ejecutan los casos de cada requisito, y cuáles no ejecuta ninguno.

## Cómo se produce

El sensor del proyecto, el mismo que deja `hechos.json` en la evidencia del candidato, corre otra vez los casos del contrato con una traza de líneas y deja `trazabilidad.json` al lado:

```python
from oracle_factory import trazabilidad

datos = trazabilidad.trazar(RAIZ, {
    'capacidad_c1234.requisito_uno': ['test_algo.Clase.test_caso_a', 'test_algo.Clase.test_caso_b'],
    'capacidad_c1234.requisito_dos': ['test_algo.Clase.test_caso_c'],
})
(evidencia / 'trazabilidad.json').write_text(json.dumps(datos, ensure_ascii=False, indent=2))
```

Las claves son los ids de los requisitos de Oracle (los de `estado ID --json`), y los casos, ids de `unittest` que se puedan cargar desde donde corre el sensor. `trazar` usa sólo la biblioteca estándar (`sys.settrace`, Python 3.11 o más) y cuenta los archivos dentro de `RAIZ`, fuera de `.venv`. Un caso que falla queda registrado con `"resultado": "falla"`. `tools/verify_trazabilidad.py` es un ejemplo completo.

## Cómo se lee

```bash
oracle-factory trazabilidad ID          # texto
oracle-factory trazabilidad ID --json   # oracle-factory.trazabilidad/1
```

Toma el candidato vigente y lo compara con su base (el merge-base con `main`, como `pedir-revision`). Muestra:

- **por requisito**, sus casos con su resultado y las líneas cambiadas que ejecutan;
- **sin respaldo**: líneas cambiadas ejecutables que no ejecuta ningún caso del contrato;
- **no rastreables**: archivos cambiados que la traza no ve (no son Python o no compilan).

Los registros de Factory (`.factory/`, `tareas/`) no cuentan: no son producto.

## Límites

- Ejecutar una línea no prueba que sea correcta: sólo que algún caso del contrato pasó por ella.
- El código que corre en otro proceso (por ejemplo, `oracle` o `tasks` llamados por la CLI) no se traza.
- Lo que corre al importar un módulo (constantes, imports, cuerpos de clase) pasa antes que cualquier caso: no cuenta como ejecutable, así que no figura ni como respaldado ni como sin respaldo. Las líneas de comentario y en blanco tampoco.
- Sin respaldo no bloquea nada: es información para quien revisa.
