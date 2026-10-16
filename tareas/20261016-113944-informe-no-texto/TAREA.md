# estado y resumen se caen con un informe que no es texto en factory.json

- ESTADO: CERRADA
- PRIORIDAD: 30
- ETIQUETAS: bug

### Nota (2026-10-16 11:39:51 UTC)

Visto el 2026-10-16 al probar la extensión de VS Code: con revision.informe u oracle.informe = 5 en factory.json, estado y resumen terminan en TypeError (problemas_de_revision hace ROOT / ruta, oracle_factory/cli.py:1488). donde ya lo marca no_valido (estructura._entrada). Que estado y resumen lo traten igual: un pendiente que nombre el valor, no un traceback. La extensión hoy muestra el error de la CLI.

### Nota (2026-10-16 12:59:45 UTC)

Hecho en el cambio 20261016-114832-informe-no-texto (merge c00aa72): ruta_del_registro y no_es_ruta con el criterio de donde en los cinco lugares; un campo presente que no es texto (también 0, False, "", [] o {}) es un pendiente «<campo> no válido en el registro» y el paso rehace la revisión o el juicio. El campo spec del registro quedó fuera de alcance.
