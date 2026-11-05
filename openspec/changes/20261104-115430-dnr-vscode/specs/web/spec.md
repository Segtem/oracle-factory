# Capability: web

## ADDED Requirements

### Requirement: las_guias_muestran_vscode_real
Tipo: funcional
El sistema DEBE mostrar en las guías, al menos, cuatro capturas reales de VS Code con la extensión de Factory sobre un proyecto de ejemplo (la vista «Factory», el tablero, el próximo paso de un cambio y la consulta «por qué»), cada una como imagen que existe en `site/img/`, con texto alternativo no vacío, dimensiones declaradas y un peso de hasta 300 KB, y el conjunto de hasta 1,5 MB.

#### Scenario: una persona lee la guía y quiere ver la herramienta
- DADA la guía desde cero o la de colaboración
- CUANDO se recorren sus imágenes
- ENTONCES hay al menos cuatro capturas de VS Code distintas, cada archivo existe, tiene texto alternativo, ancho y alto, y ninguna pasa de 300 KB ni el conjunto de 1,5 MB

#### Scenario: una captura que falta
- DADA una página que enlaza una imagen de `site/img/` inexistente
- CUANDO se corren las comprobaciones del sitio
- ENTONCES fallan nombrando la página y la imagen

### Requirement: los_ejemplos_son_salida_real
Tipo: funcional
El sistema DEBE mostrar en las guías ejemplos de salida de los comandos que coinciden palabra por palabra con lo que la CLI contestó sobre el proyecto de ejemplo, registrado en `tests/datos/ejemplos-demo.json`, y DEBE existir una forma reproducible de regenerar capturas y ejemplos (`tools/capturas_vscode.py`).

#### Scenario: un ejemplo escrito a mano
- DADO un bloque de ejemplo de una guía cuyo texto no coincide con el registrado
- CUANDO se corren las comprobaciones del sitio
- ENTONCES fallan nombrando la página y el ejemplo

### Requirement: los_ejemplos_no_filtran_datos_personales
Tipo: no funcional
El sistema NO DEBE incluir en las guías, en el registro de ejemplos ni en el script de capturas rutas del directorio personal real, correos ni cuentas que no sean del proyecto de ejemplo, que usa personas ficticias.

#### Scenario: una ruta personal en un ejemplo
- DADO un ejemplo que contiene una ruta de home real o un correo ajeno al ejemplo
- CUANDO se corren las comprobaciones del sitio
- ENTONCES fallan nombrando el archivo
