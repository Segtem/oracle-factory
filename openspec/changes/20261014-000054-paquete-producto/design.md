# Design

- Las exclusiones salen del diff del candidato contra la base (`git diff --name-only`): `.factory` y `tareas` siempre, más cada archivo que `es_producto` no cuenta y no está debajo de esas dos. Así un registro nuevo fuera de esas carpetas (una spec consolidada que gestiona Factory, el estado de un cambio anterior a `.factory/`) también queda afuera, sin listas aparte.
- La comprobación es una función: un paquete es aceptable si ninguno de sus `excluded_files` cuenta como producto. La usan `pedir-revision` (después de `preparar`, antes de lanzar al revisor) y `material_del_candidato` (al leer cada informe guardado), así no divergen.
- Un paquete sin `exclusions` (los de 0.1.0a1) pasa la comprobación sin cambios; Clue 0.1.0a2 lo valida igual que antes.
- El pedido suma una línea en el bloque de vueltas (`$vueltas`), como los riesgos aceptados: una plantilla propia no necesita cambiar.
