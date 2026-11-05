# Diseño

- `tools/capturas_vscode.py` crea el proyecto de ejemplo (un repositorio git con una persona y un agente ficticios, con `oracle-factory init` y dos cambios en estados distintos), instala la extensión desde `editores/vscode/*.vsix` en un directorio de extensiones temporal, abre `code` bajo Xvfb forzando X11 y toma las capturas con `import`; recorta y optimiza a PNG. Deja también `tests/datos/ejemplos-demo.json` con la salida de cada comando mostrado.
- Las imágenes van a `site/img/vscode-*.png` con `width` y `height` explícitos (sin saltos de layout), `loading="lazy"` y texto alternativo que describe lo que se ve.
- Las páginas muestran las salidas dentro de bloques `<pre data-ejemplo="ID">`; una prueba compara cada bloque con `ejemplos-demo.json`, de modo que el texto de la web no se desvía de lo que la CLI contestó.
- Una prueba rechaza en el script, en el JSON y en las páginas cualquier ruta del home real, correo o cuenta de GitHub que no sea del ejemplo.
- El script necesita `xvfb-run`, `import` (ImageMagick) y `xdotool`; no corre en la suite, que sólo comprueba sus resultados.
