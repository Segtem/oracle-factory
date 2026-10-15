# Design

- La tabla lleva una fila por decisión (`spec`, `medidas` de un requisito funcional, `medidas` de uno no funcional, `revision`, `cierre`) y una columna por modo. Cada celda dice una de tres cosas, que corresponden a lo que devuelve `modos.via_agente`: «decide el agente» (`decide`), «el agente propone y una persona confirma» (`propone`), «sólo una persona» (`rechaza`).
- En la página, cada fila lleva `data-decision` y `data-tipo`, y cada celda `data-modo`; en el documento, la tabla Markdown tiene las mismas filas y columnas. La prueba lee las dos.
- Las páginas siguen las reglas del sitio que ya se prueban: idioma `es`, un solo `h1`, contenido en el HTML (no en un script), enlaces internos que resuelven y comandos nombrados que existen.
