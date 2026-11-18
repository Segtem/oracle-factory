# El conductor autopilot, como leyes probadas

`oracle_factory.autopilot.decidir` (qué hace el conductor con el próximo paso de un cambio) escrito en
[Bend 2](https://bend-lang.com/) como un modelo con leyes que se prueban para todos los próximos pasos y todas las banderas. Es la
regla, no el código de Factory, que es Python. Mismo enfoque que `modelos/quien-decide/`.

- `autopilot.bend`: el modelo. Recibe el próximo paso ya clasificado (cada subcomando que reconoce el parser de Factory, prosa o
  algo ilegible) y cinco banderas: si hay frenos, si el cambio está terminado (cerrado o abandonado), si falta un segundo revisor, si hay candidato y si el
  agente ya dejó su propuesta de revisión.
- `LAWS.bend`: 24 leyes. La central: si el conductor actúa, corre sólo un comando mecánico, y si frena, delega o termina, no trae
  comando. Las demás: con frenos siempre frena; confirmar las medidas y cada decisión de una persona se le piden a una persona;
  ninguna decisión de una persona es mecánica; antes de revisar se prepara la propuesta y se pide el segundo revisor que falta; sin
  candidato primero se construye; la prosa se delega; lo que no conoce lo frena; sin próximo paso sólo termina lo cerrado o abandonado. Las
  revisa una persona.
- `PROOF.bend`: sus pruebas, por análisis de casos, generadas por `generar.py` (no se editan a mano: `python3 generar.py`).
- `autopilot.mjs`: el modelo compilado a JavaScript, versionado. Si cambiás el modelo: `bend autopilot.bend -o autopilot.mjs`.

`tests/test_leyes_autopilot.py` lo vigila: con `bend`, las pruebas valen, `PROOF.bend` y `autopilot.mjs` están al día y quince
mutantes del modelo hacen fallar alguna prueba; con `bend`, `lean` y `leanc`, `--verdict` las acepta; con `node`, el modelo y
`autopilot.decidir` dicen lo mismo en las 1392 combinaciones (las tres fases: en curso, cerrada y abandonada; y, además de cada subcomando, los pasos que dicen «faltan archivos» o traen una ruta por completar). Sin una herramienta, esa prueba se omite y dice cuál falta.

Límites: el modelo no cubre `argumentos_mecanicos` ni el conductor que ejecuta (`conductor.py`), ni cómo `estado` arma el próximo
paso. La clasificación del texto del paso (lo que `decidir` lee antes del subcomando: «faltan archivos», una ruta `RUTA_…` por completar,
prosa, algo que el parser no acepta) está representada por clases; la comparación las prueba con representantes, no con todo
texto posible.
