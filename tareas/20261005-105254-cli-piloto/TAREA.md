# Pulir la CLI de Factory con lo observado en el piloto

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: colaboracion, piloto, cli


## Objetivo

Corregir la fricción 7 del [piloto con agentes](../20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md):
- `estado`: el próximo paso sigue en `medir --listar` después de medir, y en `estado` después de juzgar.
- `medir`: avisar que reemplaza las medidas y señalar las huérfanas. `--listar` debe separar las medidas del proyecto de las meta.
- `importar`: la `fuente` del requisito tiene que ser relativa al proyecto, no la ruta absoluta del checkout.
- `revision` sin commits: explicar el paso que falta.
- Plantillas: la spec debe traer `## ADDED Requirements` y la proposal no debe decir «Brian».
- Ejemplo `notas`: las medidas deben cumplir `meta.ningun_umbral_de_igualdad` y `meta.toda_medida_filtra_o_agrupa` (fricción 11).

### Nota (2026-10-05 11:44:21 UTC)

Fricción observada al registrar la revisión de colaboración (2026-10-05): commitear factory.json/review.md cambia HEAD y deja la revisión 'desactualizada respecto del producto' aunque archivos_sha256 sea idéntico. contexto_producto() exige HEAD igual; los registros del flujo ya se excluyen de los archivos. Evaluar vincular la revisión a archivos_sha256 + commit del producto, no al HEAD que incluye registros.
