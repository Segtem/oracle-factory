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

Las claves son los ids de los requisitos de Oracle (los de `estado ID --json`), y los casos, ids de `unittest` que se puedan cargar desde donde corre el sensor. `trazar` usa sólo la biblioteca estándar (`sys.settrace`, Python 3.11 o más), traza también los hilos que arranque cada caso y cuenta los archivos dentro de `RAIZ`, fuera de `.venv`. Un caso que falla queda registrado con `"resultado": "falla"`, aunque también tenga subpruebas omitidas. Si ya había una traza puesta (otro sensor, un depurador), se encadena: sigue recibiendo sus eventos y la recupera al terminar. `tools/verify_trazabilidad.py` es un ejemplo completo.

## Cómo se lee

```bash
oracle-factory trazabilidad ID          # texto
oracle-factory trazabilidad ID --json   # oracle-factory.trazabilidad/1
oracle-factory trazabilidad ID --base REF
```

Toma el candidato vigente y lo compara con su base: el merge-base del candidato con `main`, como `pedir-revision`, u otra con `--base`. Los renombres se detectan (un archivo movido cuenta sólo lo que cambió) y los nombres llegan exactos, aunque tengan espacios. Muestra:

- **por requisito**, sus casos con su resultado y las líneas cambiadas que ejecutan;
- **sin respaldo**: líneas cambiadas ejecutables que no ejecuta ningún caso del contrato;
- **corren al importar**: líneas cambiadas de módulo o de cuerpos de clase del módulo (constantes, imports, atributos); corren antes que los casos, así que se listan aparte, sin decir si tienen respaldo. Una clase definida dentro de una función corre cuando la función se llama, así que cuenta como el resto de la función. El cuerpo de `if __name__ == "__main__":` no corre al importar: cuenta como ejecutable, y figura sin respaldo si ningún caso lo corre. En una función decorada, la línea del `def` cuenta como ejecutada cuando lo está su primer decorador, que es la línea que ve la traza;
- **no rastreables**: archivos cambiados que la traza no ve (no son Python o no compilan);
- **borrados**: archivos del producto que el candidato quitó o movió fuera del producto (por ejemplo, a `tareas/`).

Los registros de Factory (`.factory/`, `tareas/`) no cuentan: no son producto.

## Avisos de pruebas en `estado`

`oracle-factory estado ID` (y `estado ID --json`, en la clave `pruebas`) usa esta misma trazabilidad para avisar, sin bloquear nada, de los
requisitos del cambio que no tienen ningún caso de prueba en el candidato vigente, o de que el candidato no tiene `trazabilidad.json`.
El aviso no cambia los pendientes ni el próximo paso: es una práctica de desarrollo (escribir primero las pruebas de cada escenario de la
spec), no un paso que reemplace a Oracle ni a las mutaciones.

Si un requisito no se puede probar, se declara en su spec, antes del primer escenario:

```markdown
### Requirement: el_texto_de_ayuda_es_claro
Tipo: no funcional
Pruebas: no aplica — es un texto de ayuda, lo revisa una persona
```

La línea va en la cabecera del requisito (antes del primer escenario y fuera de los bloques de código), una sola vez, y necesita un motivo
que no sea sólo guiones; sin él, `aprobar-spec` e `importar` se niegan. Una línea mala no descarta las buenas de los otros requisitos.
Un requisito con más de una línea `Pruebas:` queda sin excepción. Las excepciones sólo cuentan si la spec tiene una aprobación vigente
(la misma comprobación que usa `importar`): si se editó después o se invalidó, `estado` lo avisa y no las toma. La ruta de la spec tiene que
estar dentro del proyecto, sin `..` ni enlaces simbólicos. Como la spec la aprueba una persona, aprobarla es aprobar el
motivo, y `estado` lo muestra («Pruebas: ID no aplica — motivo»). Un requisito exceptuado deja de avisar.

## Límites

- Ejecutar una línea no prueba que sea correcta: sólo que algún caso del contrato pasó por ella.
- El código que corre en otro proceso (por ejemplo, `oracle` o `tasks` llamados por la CLI) no se traza.
- Lo que corre al importar un módulo (constantes, imports, cuerpos de clase) pasa antes que cualquier caso: se lista aparte, sin decir si tiene respaldo. Las líneas de comentario y en blanco no figuran en ningún lado.
- Un hilo que un caso deja corriendo después de terminar sigue con la traza de ese caso.
- Sin respaldo no bloquea nada: es información para quien revisa.
