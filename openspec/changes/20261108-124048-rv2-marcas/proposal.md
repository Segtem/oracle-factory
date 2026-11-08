# El comprobador del sitio detecta bloques marcados duplicados

## Por qué

WPG-007 (hallazgo bajo de codex en el cambio `paginas`, aceptado entonces como riesgo): `tools/sitio_paginas.py` valida los bloques generados del sitio (`menu`, `pie`, `leer`, `ruta`) comparando sólo la primera pareja de marcadores `<!-- bloque -->…<!-- /bloque -->` de cada página. Si una página trae una segunda pareja con el mismo nombre y contenido alterado, `problemas()` devuelve `[]` y el sitio publica un menú o un pie que no sale de la tabla. Quien mantiene la web pierde la garantía de que lo generado es lo único que hay.

## Qué cambia

- `problemas()` marca como problema, nombrando la página y el bloque, que una pareja de marcadores aparezca más de una vez (la apertura o el cierre repetidos).
- Se cubre la clase entera: los cuatro bloques, tanto los que la página debe tener como los que no debe tener (`leer` en la portada, `ruta` en las demás).
- Una pareja única y bien formada sigue pasando; el repositorio actual sigue dando `[]`.

## Fuera de alcance

- Cambiar cómo se escriben los bloques (`--escribir` ya reemplaza sólo la primera pareja; con el comprobador, un duplicado deja de pasar inadvertido).
- Detectar HTML duplicado sin marcadores.

## Decisiones humanas

Ninguna abierta: aprobar la spec es la decisión de la persona.
