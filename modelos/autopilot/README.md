# El conductor autopilot, como leyes probadas

`oracle_factory.autopilot.decidir` (qué hace el conductor con el próximo paso de un cambio) escrito en
[Bend 2](https://bend-lang.com/) como un modelo con leyes que se prueban para todos los próximos pasos y todas las banderas. Es la
regla, no el código de Factory, que es Python. Mismo enfoque que `modelos/quien-decide/`.

- `autopilot.bend`: el modelo. Recibe el próximo paso ya clasificado (cada subcomando que reconoce el parser de Factory, prosa o
  algo ilegible) y cinco banderas: si hay frenos, si el cambio está cerrado, si falta un segundo revisor, si hay candidato y si el
  agente ya dejó su propuesta de revisión.
- `LAWS.bend`: 22 leyes. La central: si el conductor actúa, corre sólo un comando mecánico, y si frena, delega o termina, no trae
  comando. Las demás: con frenos siempre frena; confirmar las medidas y cada decisión de una persona se le piden a una persona;
  ninguna decisión de una persona es mecánica; antes de revisar se prepara la propuesta y se pide el segundo revisor que falta; sin
  candidato primero se construye; la prosa se delega; lo que no conoce lo frena; sin próximo paso sólo termina lo cerrado. Las
  revisa una persona.
- `PROOF.bend`: sus pruebas, por análisis de casos, generadas por `generar.py` (no se editan a mano: `python3 generar.py`).
- `autopilot.mjs`: el modelo compilado a JavaScript, versionado. Si cambiás el modelo: `bend autopilot.bend -o autopilot.mjs`.

`tests/test_leyes_autopilot.py` lo vigila: con `bend`, las pruebas valen, `PROOF.bend` y `autopilot.mjs` están al día y trece
mutantes del modelo hacen fallar alguna prueba; con `bend`, `lean` y `leanc`, `--verdict` las acepta; con `node`, el modelo y
`autopilot.decidir` dicen lo mismo en las 832 combinaciones. Sin una herramienta, esa prueba se omite y dice cuál falta.

Límites: el modelo no cubre `argumentos_mecanicos` ni el conductor que ejecuta (`conductor.py`), ni cómo `estado` arma el próximo
paso; un próximo paso con otras opciones del mismo subcomando se clasifica igual. La comparación arma un comando por subcomando.
