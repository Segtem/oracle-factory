# Diseño

- La lista vive en `oracle_factory/lista_previa.py`: una tupla de `(clave, pregunta)` más una función `texto()` que la arma para mostrarla. Las claves salen de la medición de los hallazgos.
- `flujo_revision.pedir_revision` la imprime justo antes de la línea «Revisor … sobre el candidato …». No toca el pedido (`revisores_mod.pedido`) ni el flujo.
- `docs/lista-previa.md` repite cada pregunta tal cual; una prueba compara cada pregunta del código con el documento y falla nombrando la que falta.
- La guía se arma en `oracle_factory/agentes.py`; se agrega una línea que nombra el documento. `agentes --verificar` ya detecta una guía vieja.
- Nada bloquea: es un recordatorio, como el paso de escribir primero las pruebas.
