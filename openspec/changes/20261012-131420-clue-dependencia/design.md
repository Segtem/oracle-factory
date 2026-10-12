# Design

- **`pyproject.toml`.** Se agrega `oracle-clue==0.1.0a1` a `dependencies`, la versión publicada hoy.
- **`ejecutar`.** Ya corre `oracle` y `tasks` con el punto de entrada del mismo intérprete cuando la distribución está instalada. Se le agrega `"oracle-clue": "oracle-clue"`. Las dos llamadas que hoy usan `shutil.which("oracle-clue")` pasan a `ejecutar(["oracle-clue", …])`.
- **Sin rama «sin validar».** `material_del_candidato` deja de tener el caso sin Clue. Si Clue falta igual (por ejemplo, en un checkout sin instalar), el error lo dice, como pasa con Oracle.
- **Pruebas.** Las de autoproducción que simulaban «sin Clue» con `shutil.which → None` pasan a armar informes validables, o a comprobar que un informe sin paquete no se usa.
