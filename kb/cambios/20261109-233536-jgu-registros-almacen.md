---
generado: oracle-factory kb
id: "20261109-233536-jgu-registros-almacen"
fase: "oracle_verde"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 2: el almacén y conectar

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: oracle_verde
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md](../../openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen]] — cumple
- [[requisitos/flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto]] — cumple
- [[requisitos/flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar]] — cumple
- [[requisitos/flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega]] — cumple

## Decisiones

- 2026-11-09 23:35 · Cambio creado · claude-code (agente)
- 2026-11-09 23:36 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-09 23:36 · Requisitos importados · claude-code (agente)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 01:10 · Revisión registrada · Brian Hollweg (persona) — aprobar: Propuesta del agente claude-code. Etapa 2 de 6 de «registros fuera del repo del producto»: el almacén y conectar. Candidato 7786b00 (camino completo: toca cli.py, 301+ líneas de producto): evidencia verde (1374 pruebas, 20 casos de contrato). QUIÉN LO HIZO: lo construyó un agente lanzado por el conductor (autopilot --ejecutar --lanzar con claude -p y permisos acotados: leer/editar/escribir, oracle-factory, .venv/bin/python, git status/diff/log/show/add/commit; sin push, checkout, reset, config ni red) en dos pasos: 1) 20 pruebas, catálogos y propuesta de medidas (se frenó en medir --confirmar); 2) implementación (oracle\_factory/almacenes.py nuevo, 123 líneas, más cableado en cli.py, parser, autopilot) y evidencia (se frenó por el freno de pruebas editadas). Yo escribí la spec, hice las 69+ mutaciones, pedí la revisión y arreglé el hallazgo. QUÉ HACE: conectar RUTA guarda en la configuración personal (XDG\_CONFIG\_HOME/oracle-factory/almacenes.json o \~/.config/...) {directorio común de Git del producto: almacén}; con el producto conectado todo comando sin --registros usa el almacén (desde subcarpetas y worktrees); conectar sin argumentos dice el estado; desconectar quita la conexión; sólo de una persona (autopilot.PERSONA); un producto con .factory/ propio y conectado se niega. PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/datos/ayuda-cli.json regenerado por los subcomandos nuevos conectar y desconectar (datos de la ayuda del CLI); ninguna prueba existente se quitó ni aflojó. REVISIÓN: sólo codex (2 rondas): un hallazgo medio, dos conectar a la vez podían perder una conexión (leer-modificar-guardar sin bloqueo, temporal fijo): corregido con un flock exclusivo sobre almacenes.json.lock, relectura bajo el bloqueo y temporal propio; la prueba lanza 6 procesos a la vez; la ronda 2 no trajo hallazgos. DECIDE BRIAN: (1) INTERPRETACIÓN DEL AGENTE MÁS ESPECÍFICA QUE LA SPEC: conectar y desconectar SIGUEN FUNCIONANDO cuando el producto tiene .factory/ propio y además está conectado (la spec dice que se niega «un comando»); me parece correcto porque es la salida del conflicto (el mensaje propone desconectar); si preferís que se nieguen también, hay que cambiar la spec. (2) camino completo con un solo proveedor revisor (agy y agy2 sin cuota hasta cerca del 2026-11-15). (3) Sin fcntl (Windows) no hay bloqueo: dos conectar a la vez podrían pisarse; está dicho en un comentario y no hay prueba porque este entorno es Linux. MUTACIONES: 69 sobre el código del agente: las reales detectadas con casos nuevos dentro de métodos existentes; equivalentes declaradas con motivo: claves de JSON siempre texto, git devuelve los errores por stderr, leer() ya devuelve {} sin archivo, git ya devuelve rutas reales, os.chdir al almacén es redundante (ejecutar() corre git con cwd=ROOT), el parser rechaza el comando vacío, el nombre del temporal, unlink sin suprimir. LÍMITES: la configuración personal vale por usuario y máquina; clonar desde una URL, subir/bajar el almacén y commitear tras cada decisión son la etapa 4; el candidato y la huella con dos fuentes la etapa 3. No edité otra prueba existente.
- 2026-11-10 01:10 · Juicio de Oracle · claude-code (agente)

## Riesgos aceptados

- Ninguno.

## Commits

- `081f98f` registros-almacen: propuesta y spec (etapa 2 de 6) (trailer)
- `12a44ad` registros-almacen: spec aprobada por Brian (trailer)
- `5ee2f59` registros-almacen: pruebas, catálogos y propuesta de medidas (trailer)
- `6b2ddb6` registros-almacen: medidas confirmadas por Brian (trailer)
- `e5486d5` registros-almacen: conectar y desconectar, el almacén por usuario (etapa 2 de 6) (trailer)
- `19ed52d` registros-almacen: evidencia del candidato e5486d5 (trailer)
- `6a24a61` registros-almacen: intento de revisión con agy (cuota agotada) (trailer)
- `fb6769c` registros-almacen: casos de las mutaciones propias (XDG/HOME, ruta relativa, raíces restauradas, producto desde subcarpeta) (trailer)
- `43dab88` registros-almacen: evidencia del candidato tras las mutaciones propias (trailer)
- `7786b00` registros-almacen: bloqueo y temporal propio al guardar las conexiones (hallazgo de codex sobre conectar a la vez) (trailer)
- `807da81` registros-almacen: evidencia del candidato tras el hallazgo de la concurrencia (trailer)
- `d4bb2b8` registros-almacen: informe de codex (ronda 2, sin hallazgos) (trailer)
- `dbb57b4` registros-almacen: propuesta de revisión (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261109-233536-jgu-registros-almacen`.

## Mensajes

- 2026-11-09 23:37 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-09 23:39 · claude-code: autopilot se detuvo: confirmar las medidas es sólo de una persona. Comando para una persona: oracle-factory medir 20261109-233536-jgu-registros-almacen --confirmar
- 2026-11-09 23:49 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261109-233536-jgu-registros-almacen --a agy
- 2026-11-10 00:11 · claude-code: autopilot se detuvo: hay frenos: prueba\_existente\_editada
