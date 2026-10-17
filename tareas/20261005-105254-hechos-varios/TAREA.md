# Juzgar un candidato integrado con hechos de varios sensores

- ESTADO: CERRADA
- PRIORIDAD: 30
- ETIQUETAS: colaboracion, piloto, oracle


## Objetivo

Fricción 1 del [piloto con agentes](../20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md): `juzgar --con` acepta un solo JSON y nada detecta que dos sensores emitan la misma relación, que pone rojo el requisito de otro frente sin conflicto en Git. En el piloto se resolvió con `combinar_hechos.py`.

Depende de que Oracle acepte `--con` repetible y rechace las relaciones repetidas (tarea `hechos-varios-sensores` en ~/Dev/oracle). Después, Factory: `juzgar --con` repetible y documentación.

### Nota (2026-10-17 11:33:55 UTC)

Hecho en el cambio 20261017-023151-hechos-varios (merge 8cbf0df): juzgar --con repetible con Oracle 0.39.0; el registro guarda cada archivo con su huella (hechos_mas); dos sensores con la misma relación no dejan veredicto. Ya no hace falta combinar_hechos.py.
