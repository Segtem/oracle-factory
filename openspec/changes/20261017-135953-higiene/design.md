# Design

- `pedir_revision`: evento `revision_lanzada` (turno_de_pedidos, como `revision_pedida`) antes de `ejecutar_revisor`; un `KeyboardInterrupt` durante el revisor registra `revision_pedida` con `resultado="interrumpido"` y se relanza. `aviso_lanzamientos(estado)`: por cada `revision_lanzada` sin una `revision_pedida` posterior del mismo revisor y candidato, un aviso. Lo suman `estado` y `datos_estado`.
- `aviso_sin_autor(estado)`: los eventos con `tipo_actor == "sin_identificar"`, agrupados por acción.
- `inicializar`: anota qué de `corpus`, `relaciones`, `diferencial` existía antes de `oracle init`, y después quita las que creó y quedaron vacías.
- `bloqueo_medidas`: `.factory/local/locks/<ID>.medir.lock`; el `.gitignore` que arma `init` ya no lleva `.factory-demo/`.
