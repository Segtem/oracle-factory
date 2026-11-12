# Registros fuera del repo del producto, etapa 6: migrar los registros de un proyecto a un almacén

## Por qué

Las etapas 1 a 5 dejan que un producto nuevo guarde los registros de Factory en un almacén aparte, pero un proyecto que ya trabaja con Factory los tiene adentro de su repo (`.factory/`, `openspec/`, `requisitos/`, `catalogos/`, `tareas/`, `kb/`, `oracle.json`) y hoy, si se lo conecta, Factory se niega a trabajar («migrar los registros al almacén, etapa 6, todavía no existe»). Un equipo que ya usa Factory y quiere dejar de contaminar su repo necesita pasar esos registros al almacén sin perder nada. Factory mismo es el primer caso: tiene unos 6600 archivos de registros versionados.

## Qué cambia

- `oracle-factory migrar --almacen ALMACÉN` (sólo una persona), con ALMACÉN una carpeta de un repo Git o una URL de Git (se clona como en `conectar`):
  - copia byte a byte al almacén los archivos versionados de los registros del producto, tal como están en su HEAD;
  - mueve al almacén, en la misma ruta, lo no versionado de esas carpetas (`.factory/local/`, los paquetes de Clue ignorados): nada se borra sin haberse llevado antes;
  - deja un solo commit en el almacén que nombra el producto y el commit de origen;
  - conecta el producto al almacén;
  - borra los registros del producto y deja la baja preparada en su índice (`git rm`) **sin commitear**: la persona la mira y la commitea. Factory no commitea en el producto.
- `migrar --almacen ALMACÉN --verificar` dice qué copiaría y qué movería, sin escribir nada.
- Se niega sin cambiar nada si lo corre un agente, si el producto ya está conectado, si tiene cambios sin commitear en los registros, si todavía tiene el formato anterior a la fase 2, o si el almacén ya tiene registros de Factory o está dentro del producto (o al revés).
- `tools/ensayar_migracion.py`: ensaya la migración sobre una copia de un proyecto (un clon local en una carpeta temporal y un almacén temporal) y escribe un informe: los cambios que lista Factory antes y después (tienen que ser los mismos) y, con `--pruebas`, qué pruebas de la copia fallan con los registros afuera. El ensayo sobre Factory se corre una vez y su informe queda en este cambio.

## Fuera de alcance

- Migrar `~/Dev/factory` de verdad: es una decisión aparte de Brian, porque empujarla borra miles de archivos en origin. Este cambio deja el comando y el informe del ensayo con lo que habría que arreglar antes.
- Arreglar las herramientas de Factory (`tools/verify_*.py`, pruebas) que dan por hecho los registros en el repo: el informe del ensayo las lista.
- Traer la historia de los registros al almacén (queda en la historia del producto, sin reescribir nada).
- Limpiar del producto las líneas de Factory en `.gitignore` y `.gitattributes`, o el bloque generado de un `AGENTS.md` versionado.
- Volver atrás una migración (desconectar y volver a commitear los registros en el producto se hace a mano).

## Decisiones humanas

Tomadas por Brian el 2026-11-12: comando más ensayo sobre una copia (la migración real de Factory queda aparte); en el producto, los registros se borran y la baja queda sin commitear; el almacén recibe una copia en un solo commit, sin la historia.
