# donde --json etiqueta no_valido: falta prueba

- ESTADO: CERRADA
- PRIORIDAD: 5
- ETIQUETAS: 

### Nota (2026-10-14 19:59:23 UTC)

Riesgo aceptado por Brian en 20261014-145018-donde-ausente (hallazgo DONDE-TEST-001 de codex, vuelta 3): cj2 de tests/test_cli_json.py no arma una entrada inválida del registro, así que una mutación que convirtiera no_valido en ausente en datos_donde pasaría; y la aserción de históricos usa all() sin exigir que haya alguno. test_e6_valores_no_validos_en_el_registro (test_estructura) prueba el texto de donde («no válido»), no la etiqueta del JSON. Arreglo: en cj2, invalidar un campo del registro (como e6) y exigir situacion no_valido, y exigir al menos un histórico.

### Nota (2026-10-15 00:13:23 UTC)

Hecho en el cambio 20261014-204205-donde-no-valido (merge 222acb4): MODIFIED de donde_y_resumen_se_leen_como_json con historico y no_valido definidos y el escenario de una entrada inválida; cj2 exige al menos un histórico y que, con una entrada inválida, se siga listando todo lo de antes. Los sensores de cli-json y donde-ausente cuentan sólo sus casos.
