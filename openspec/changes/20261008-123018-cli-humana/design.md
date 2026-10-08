# Design

- **Compuerta.** El mensaje de `revisar_guiado` que dice «no se puede aprobar» pasa a armar la lista de causas con los datos que ya tiene: el análisis, los pendientes y la decisión.
- **Sin candidato.** Antes de completar el informe, `preparar_revision` escribe el aviso en stderr.
- **Falta Oracle.** `main` captura `ModuleNotFoundError` de `oracle_metalenguaje` y lo convierte en `FactoryError` con el intérprete usado y dos salidas: `source .venv/bin/activate.fish` o `uv tool install oracle-factory`.
- **Re-ejecución.** `fabrica.py` usa `importlib.util.find_spec("oracle_metalenguaje")`, compara `sys.executable` con `.venv/bin/python` y llama a `os.execv`. No hay bucle posible: si `.venv` tampoco tiene la dependencia, se re-ejecuta una sola vez y falla con el mensaje anterior.
- **glow.** `shutil.which("glow")` más `sys.stdout.isatty()`, y `subprocess.run(["glow", "-p", ruta])`. Sin las dos cosas, se imprime el archivo.
- **Próximo paso.** `siguiente` se reescribe a partir del estado:
  - `medidas_pendientes` → `medir --confirmar`;
  - requisitos sin medidas → `medir --listar`;
  - sin candidato vigente → `pedir-revision --a <primer revisor>`;
  - con candidato y sin revisión → `revisar`;
  - revisión aprobada → `juzgar` (sin `--con` si están los hechos del candidato);
  - Oracle en verde → `cerrar`.

  El menú vive sólo en el despacho del comando `estado`, no en `mostrar()`, que las pruebas llaman directo. Ejecuta con `main(["--proyecto", ROOT, *argv])`.
