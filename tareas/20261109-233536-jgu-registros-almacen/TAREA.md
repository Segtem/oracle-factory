# Registros fuera del repo del producto, etapa 2: el almacén y conectar

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-09 23:35:36 UTC)

OpenSpec: openspec/changes/20261109-233536-jgu-registros-almacen. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-09 23:36:42 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 23:36:50 UTC)

Requisitos importados: flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen (funcional), flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto (funcional), flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar (funcional), flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-09 23:38:45 UTC)

Medidas de flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen: factory_registros_almacen.con_el_producto_conectado_los_comandos_usan_el_almacen, factory_registros_almacen.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 23:38:48 UTC)

Medidas de flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto: factory_registros_almacen.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto, factory_registros_almacen.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 23:38:50 UTC)

Medidas de flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar: factory_registros_almacen.conectar_sin_argumentos_y_desconectar, factory_registros_almacen.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 23:38:52 UTC)

Medidas de flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega: factory_registros_almacen.un_producto_con_su_propio_factory_conectado_se_niega, factory_registros_almacen.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 23:41:43 UTC)

Medidas de flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 23:41:43 UTC)

Medidas de flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 23:41:43 UTC)

Medidas de flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 23:41:43 UTC)

Medidas de flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 01:10:22 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 2 de 6 de «registros fuera del repo del producto»: el almacén y conectar. Candidato 7786b00 (camino completo: toca cli.py, 301+ líneas de producto): evidencia verde (1374 pruebas, 20 casos de contrato). QUIÉN LO HIZO: lo construyó un agente lanzado por el conductor (autopilot --ejecutar --lanzar con claude -p y permisos acotados: leer/editar/escribir, oracle-factory, .venv/bin/python, git status/diff/log/show/add/commit; sin push, checkout, reset, config ni red) en dos pasos: 1) 20 pruebas, catálogos y propuesta de medidas (se frenó en medir --confirmar); 2) implementación (oracle_factory/almacenes.py nuevo, 123 líneas, más cableado en cli.py, parser, autopilot) y evidencia (se frenó por el freno de pruebas editadas). Yo escribí la spec, hice las 69+ mutaciones, pedí la revisión y arreglé el hallazgo. QUÉ HACE: conectar RUTA guarda en la configuración personal (XDG_CONFIG_HOME/oracle-factory/almacenes.json o ~/.config/...) {directorio común de Git del producto: almacén}; con el producto conectado todo comando sin --registros usa el almacén (desde subcarpetas y worktrees); conectar sin argumentos dice el estado; desconectar quita la conexión; sólo de una persona (autopilot.PERSONA); un producto con .factory/ propio y conectado se niega. PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/datos/ayuda-cli.json regenerado por los subcomandos nuevos conectar y desconectar (datos de la ayuda del CLI); ninguna prueba existente se quitó ni aflojó. REVISIÓN: sólo codex (2 rondas): un hallazgo medio, dos conectar a la vez podían perder una conexión (leer-modificar-guardar sin bloqueo, temporal fijo): corregido con un flock exclusivo sobre almacenes.json.lock, relectura bajo el bloqueo y temporal propio; la prueba lanza 6 procesos a la vez; la ronda 2 no trajo hallazgos. DECIDE BRIAN: (1) INTERPRETACIÓN DEL AGENTE MÁS ESPECÍFICA QUE LA SPEC: conectar y desconectar SIGUEN FUNCIONANDO cuando el producto tiene .factory/ propio y además está conectado (la spec dice que se niega «un comando»); me parece correcto porque es la salida del conflicto (el mensaje propone desconectar); si preferís que se nieguen también, hay que cambiar la spec. (2) camino completo con un solo proveedor revisor (agy y agy2 sin cuota hasta cerca del 2026-11-15). (3) Sin fcntl (Windows) no hay bloqueo: dos conectar a la vez podrían pisarse; está dicho en un comentario y no hay prueba porque este entorno es Linux. MUTACIONES: 69 sobre el código del agente: las reales detectadas con casos nuevos dentro de métodos existentes; equivalentes declaradas con motivo: claves de JSON siempre texto, git devuelve los errores por stderr, leer() ya devuelve {} sin archivo, git ya devuelve rutas reales, os.chdir al almacén es redundante (ejecutar() corre git con cwd=ROOT), el parser rechaza el comando vacío, el nombre del temporal, unlink sin suprimir. LÍMITES: la configuración personal vale por usuario y máquina; clonar desde una URL, subir/bajar el almacén y commitear tras cada decisión son la etapa 4; el candidato y la huella con dos fuentes la etapa 3. No edité otra prueba existente.); 0 abiertos derivados; commit dbb57b45af5f3a0fcfda6ffd61515caf8b80e409; informe tareas/20261109-233536-jgu-registros-almacen/revisiones/registro-e5rd1coj/informe.json; decisiones tareas/20261109-233536-jgu-registros-almacen/revisiones/registro-e5rd1coj/decisiones.json.

### Nota (2026-11-10 01:10:30 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-233536-jgu-registros-almacen/oracle-veredicto.txt.
