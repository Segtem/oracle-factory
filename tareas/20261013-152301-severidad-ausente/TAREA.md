# Spec de revisores: un informe sin severidad no se guarda

- ESTADO: ABIERTA
- PRIORIDAD: 15
- ETIQUETAS: 

### Nota (2026-10-13 15:23:01 UTC)

Hallazgo F-03 (agy, vuelta 1) de 20261013-115616-vueltas-severidad: el requisito el_corte_de_vueltas_sigue_la_severidad promete que, al terminar pedir-revision, un hallazgo sin severidad cuenta como medio, pero Clue exige la severidad y rechaza ese informe antes de guardarlo, así que el escenario no se alcanza (se prueba sólo sobre preparacion.corte). Reescribir con un MODIFIED: un informe sin severidad no se guarda; si uno guardado la pierde, cuenta como media.
