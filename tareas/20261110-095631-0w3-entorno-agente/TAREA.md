# Autopilot: el agente lanzado recibe un entorno filtrado y una guía de permisos sin Python abierto

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-10 09:56:31 UTC)

OpenSpec: openspec/changes/20261110-095631-0w3-entorno-agente. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-10 09:58:39 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261110-095631-0w3-entorno-agente/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-10 09:58:50 UTC)

Requisitos importados: flujo_c93a1d23e9668d672.el_agente_lanzado_recibe_un_entorno_minimo (funcional), flujo_c93a1d23e9668d672.entorno_explicito_por_corrida (funcional), flujo_c93a1d23e9668d672.la_guia_de_permisos_no_abre_python (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-10 10:01:48 UTC)

Medidas de flujo_c93a1d23e9668d672.el_agente_lanzado_recibe_un_entorno_minimo: factory_entorno_agente.el_agente_lanzado_recibe_un_entorno_minimo, factory_entorno_agente.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 10:01:50 UTC)

Medidas de flujo_c93a1d23e9668d672.entorno_explicito_por_corrida: factory_entorno_agente.entorno_explicito_por_corrida, factory_entorno_agente.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 10:01:52 UTC)

Medidas de flujo_c93a1d23e9668d672.la_guia_de_permisos_no_abre_python: factory_entorno_agente.la_guia_de_permisos_no_abre_python, factory_entorno_agente.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 10:02:28 UTC)

Medidas de flujo_c93a1d23e9668d672.el_agente_lanzado_recibe_un_entorno_minimo: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 10:02:28 UTC)

Medidas de flujo_c93a1d23e9668d672.entorno_explicito_por_corrida: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 10:02:28 UTC)

Medidas de flujo_c93a1d23e9668d672.la_guia_de_permisos_no_abre_python: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 13:50:44 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Arreglo de seguridad del conductor, construido por mí (no por un agente lanzado: no corresponde que un agente construya su propia jaula). Candidato 34e2d97 (camino COMPLETO: 166+ líneas de producto y toca cli.py; yo había dicho «ligero» y me corregí): evidencia verde (1384 pruebas, 10 casos de contrato). QUÉ CAMBIA: el agente lanzado por autopilot --ejecutar --lanzar recibe un entorno MÍNIMO por lista de permitidos (PATH, HOME, USER, LOGNAME, SHELL, LANG, LANGUAGE, TERM, TZ, TMPDIR, BASH_DEFAULT_TIMEOUT_MS, BASH_MAX_TIMEOUT_MS, prefijos LC_ y XDG_) más FACTORY_AGENTE (que gana siempre) y lo que la persona entregue con --entorno NOMBRE (repetible, sólo con --ejecutar --lanzar, por corrida, no se guarda; se rechaza antes de correr o escribir nada); los comandos mecánicos de Factory no cambian; docs/modos.md explica el filtro y la guía de permisos con Python acotado a -m unittest y tools/verificar_cambio.py, advirtiendo del patrón abierto. PRUEBA EXISTENTE EDITADA (declarada): tests/datos/ayuda-cli.json regenerado por la opción nueva --entorno (datos de la ayuda del CLI); ninguna otra prueba existente se editó. REVISIÓN: sólo codex (2 rondas): un hallazgo medio, EA-1 (--entorno se ignoraba en la consulta de sólo lectura sin --ejecutar): corregido, con prueba; ronda 2 sin hallazgos. MUTACIONES propias: 27 sobre el cambio más 6 sobre la corrección de EA-1, todas las reales detectadas; una de mis corridas de mutaciones se cortó por un error de mi script y por un momento afirmé que estaban detectadas sin haberlas corrido: lo corregí y las corrí de verdad. UNA FALLA PROPIA: la evidencia dio éxito: False en la primera vuelta porque una prueba existente de la web (test_w3) leyó las opciones de claude dentro del texto de --lanzar como opciones de autopilot; ajusté el ejemplo de la guía (variable de fish) y la repetí; yo sólo había corrido las pruebas cercanas. DECIDE BRIAN: (1) camino completo con un solo proveedor revisor (agy sin cuota hasta cerca del 2026-11-15). (2) LÍMITES DECLARADOS: HOME llega al agente y puede apuntar a credenciales; el proceso no se aísla (corre como tu usuario; para aislarlo hace falta un contenedor); Factory no hace cumplir los permisos de --allowedTools, que define el comando de --lanzar. (3) Las tres corridas anteriores del agente (origen de este cambio) recibieron TODO el entorno, incluidas OPENROUTER_API_KEY y CLAUDE_CODE_MESSAGING_TOKEN (sólo vi los nombres); no hicieron nada fuera de lugar que yo haya visto, pero no puedo garantizarlo: si preferís rotar esas claves, es decisión tuya. No edité otra prueba existente.); 0 abiertos derivados; commit fa9ef0ed750111391b898f2e164e1bffe9085d5a; informe tareas/20261110-095631-0w3-entorno-agente/revisiones/registro-33zcxc3p/informe.json; decisiones tareas/20261110-095631-0w3-entorno-agente/revisiones/registro-33zcxc3p/decisiones.json.

### Nota (2026-11-10 13:52:32 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261110-095631-0w3-entorno-agente/oracle-veredicto.txt.

### Nota (2026-11-10 13:54:25 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
