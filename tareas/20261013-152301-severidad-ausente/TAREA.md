# Spec de revisores: un informe sin severidad no se guarda

- ESTADO: CERRADA
- PRIORIDAD: 15
- ETIQUETAS: 

### Nota (2026-10-13 15:23:01 UTC)

Hallazgo F-03 (agy, vuelta 1) de 20261013-115616-vueltas-severidad: el requisito el_corte_de_vueltas_sigue_la_severidad promete que, al terminar pedir-revision, un hallazgo sin severidad cuenta como medio, pero Clue exige la severidad y rechaza ese informe antes de guardarlo, así que el escenario no se alcanza (se prueba sólo sobre preparacion.corte). Reescribir con un MODIFIED: un informe sin severidad no se guarda; si uno guardado la pierde, cuenta como media.

### Nota (2026-10-14 14:48:08 UTC)

Hecho en el cambio 20261014-140627-severidad-ausente (merge b853e6c): MODIFIED de el_corte_de_vueltas_sigue_la_severidad; un informe sin severidad (ausente, nula o desconocida) no se guarda, y uno guardado que la pierde no se usa y estado avisa. Pruebas de punta a punta en tests/test_severidad_ausente.py.
