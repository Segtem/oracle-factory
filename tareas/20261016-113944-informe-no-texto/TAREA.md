# estado y resumen se caen con un informe que no es texto en factory.json

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: bug

### Nota (2026-10-16 11:39:51 UTC)

Visto el 2026-10-16 al probar la extensión de VS Code: con revision.informe u oracle.informe = 5 en factory.json, estado y resumen terminan en TypeError (problemas_de_revision hace ROOT / ruta, oracle_factory/cli.py:1488). donde ya lo marca no_valido (estructura._entrada). Que estado y resumen lo traten igual: un pendiente que nombre el valor, no un traceback. La extensión hoy muestra el error de la CLI.
