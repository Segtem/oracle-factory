# Diseño

- La lógica va en un módulo nuevo, `oracle_factory/osv.py`, para no agrandar `procedencia.py`; el comando sólo la llama.
- Se agrega `--consultar-osv` a `procedencia`, que exige `--red`. Sin `--red` falla antes de importar nada de red.
- La consulta usa la API de OSV.dev: `POST /v1/querybatch` con `{package: {name, ecosystem: "PyPI"}, version}` por cada
  par distinto de los inventarios guardados, y `GET /v1/vulns/ID` por cada aviso devuelto (el lote sólo trae identificadores). Se
  usa `urllib` de la biblioteca estándar, sin dependencias nuevas.
- `--osv-url` cambia la base de la API; las pruebas la apuntan a un servidor local, así que ninguna prueba toca la red.
- El resultado se valida con `procedencia.avisos` (el mismo validador del archivo local) antes de guardarse; se guarda con una
  escritura atómica en `--salida` (por omisión `.factory/local/avisos-osv.json`) y se audita con `informe_auditar`.
- Cualquier error (conexión, tiempo, estado HTTP, JSON o aviso inválido) levanta un error con el motivo y no deja archivo parcial.
