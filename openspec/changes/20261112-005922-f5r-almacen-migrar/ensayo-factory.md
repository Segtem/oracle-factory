# Ensayo: migrar Factory mismo a un almacén (2026-11-12)

`python tools/ensayar_migracion.py ~/Dev/factory-almacen-migrar --pruebas`, sobre un clon temporal del commit `a6ac7aa3`
(etapa 6 recién implementada), con un almacén y una configuración de usuario temporales. Tardó 938 s (la suite dos veces).
No tocó el repo de Factory ni la configuración del usuario.

## Qué pasó

- `migrar --almacen` copió **6607 archivos versionados** al almacén en un commit y dejó las 6607 bajas preparadas en el
  índice de la copia, sin commitear. No movió nada sin versionar (el clon no trae `.factory/local/`; en `~/Dev/factory` hay
  162 MB ahí, que la migración real movería).
- `listar` muestra **los mismos 130 renglones** antes y después (sin la línea «Acuerdos:», que nombra dónde están los registros).
- Pruebas de la copia: 1455, con 15 omitidas en las dos corridas (el clon no trae `node_modules/`: las de la web con
  Playwright). Antes de migrar falló 1; después, 17 más.

## Las fallas y qué se hizo

| Prueba | Por qué falla | Qué se hizo |
| --- | --- | --- |
| `test_almacen_migrar` mg1 (URL), ya antes de migrar | la prueba no aislaba `XDG_DATA_HOME`: con la variable puesta, el clon iba a otra carpeta | arreglada la prueba |
| `test_terminal_lista` (15) | con el producto conectado, la extensión crea un `RelativePattern`; el `vscode` falso de `tests/terminal_en_node.cjs` no lo tenía y la extensión se caía al activarse | la extensión ya no se cae si no puede vigilar el almacén (lo anota y la vista sigue; prueba nueva en `test_almacen_vscode`); el `vscode` falso suma `RelativePattern`, como VS Code |
| `test_portabilidad` p6 (requisitos de este repositorio) | lee `requisitos/` del repo de Factory | sin arreglar: depende de los registros en el repo |
| `test_verificador_generico` vg3 (forma de los catálogos) | compara con los `catalogos/` del repo de Factory | sin arreglar: depende de los registros en el repo |

## Lo que habría que arreglar antes de migrar `~/Dev/factory` de verdad

- Las dos pruebas de arriba (p6 y vg3) tienen que buscar los registros en el almacén cuando el producto está conectado, o
  saltearse diciendo por qué.
- Las herramientas que la suite no ejercita: 73 de `tools/*.py` nombran `ROOT/SOURCE / ".factory"`, `openspec`,
  `requisitos`, `catalogos`, `tareas` o `kb` (los `verify_*.py` de cambios cerrados, y `verificar_cambio.py`, que escribe los
  catálogos en `RAIZ/catalogos`). Las de cambios cerrados no se vuelven a correr; `verificar_cambio.py` sí, y tendría que
  escribir en el almacén (`--raiz` ya existe; falta que lo deduzca de la conexión).
- Lo que `migrar` deja fuera de alcance: las líneas de Factory en `.gitignore` y `.gitattributes`, y el bloque generado del
  `AGENTS.md` versionado.
- La puerta local de salida (`hooks`) mira `kb` y `resumen` del repo; con el almacén aparte no se instala ningún hook en el
  producto (etapa 3), así que hay que decidir qué pasa con la que ya está instalada en Factory.
- Empujar la baja borra 6607 archivos en origin y respaldo: es una decisión de Brian, aparte de este cambio.
