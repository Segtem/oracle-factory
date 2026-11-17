"""Los comandos del proyecto: init (y el ejemplo), migrar, procedencia, autonomía, desplegar y autopilot (sacado de cli.py).

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo (`cli.NOMBRE`), no lo copia: así un valor
cambiado en `cli` (la raíz del proyecto en las pruebas, por ejemplo) vale también acá."""
from __future__ import annotations

from importlib import resources
from pathlib import Path
import json
import shlex
import sys

from . import autopilot
from . import conductor
from . import despliegue as despliegue_mod
from . import estructura
from . import migracion
from . import modos
from . import osv as osv_mod
from . import procedencia as procedencia_mod


def declarar_sensor_del_ejemplo() -> bool:
    """`nuevo --con-ejemplo notas` declara el sensor del ejemplo si el proyecto no declara ninguno; True si lo declaró. Declararlo no lo
    aprueba: eso lo hace una persona con `aprobar-sensor`. Con registros aparte el ejemplo queda en el almacén y no en el producto que
    corre el sensor, y con la configuración anterior en la raíz (`factory.json`) crear `.factory/config.json` la dejaría sin efecto: en
    los dos casos no declara nada."""
    config = cli.ruta_segura(cli.ROOT / estructura.DIR / 'config.json')
    if cli.PRODUCTO or not config.is_file() or cli.config_proyecto()["sensor"]:
        return False
    crudo = config.read_bytes()
    sensor = {"comando": ["{python}", "examples/notas/sensor.py", "--salida", "{salida}/hechos.json"], "tope_minutos": 5, "hechos": "avisar"}
    datos = {**json.loads(crudo), "sensor": sensor}
    cli.escribir_atomico(config, (json.dumps(datos, indent=2, ensure_ascii=False) + "\n").encode(), esperado=crudo)
    return True


def plan_ejemplo() -> dict[Path, bytes]:
    destino = cli.ruta_segura(cli.ROOT / 'examples' / 'notas')
    if destino.exists():
        raise cli.FactoryError(f"el destino del ejemplo ya existe: {destino}; usá nuevo --capacidad notas para otro cambio")
    oracle = cli.proyecto_oracle()
    if not (oracle / 'catalogos').is_dir() or not (oracle / 'oracle.json').is_file():
        raise cli.FactoryError('primero inicializá el proyecto con oracle-factory init')
    origen = resources.files('oracle_factory').joinpath('data/notas')
    plan = {}
    def recorrer(carpeta, relativa):
        for item in sorted(carpeta.iterdir(), key=lambda x: x.name):
            nombre = relativa / item.name
            if item.is_dir():
                recorrer(item, nombre)
            else:
                plan[destino / nombre] = item.read_bytes()
                if relativa == Path('catalogos'):
                    plan[oracle / 'catalogos' / item.name] = item.read_bytes()
    recorrer(origen, Path())
    for ruta in plan:
        cli.ruta_segura(ruta)
        if ruta.exists():
            raise cli.FactoryError(f"destino existente; no se creó ninguna tarea ni se sobrescribió: {ruta}")
        for padre in ruta.parents:
            if padre == cli.ROOT:
                break
            if padre.exists() and not padre.is_dir():
                raise cli.FactoryError(f"el directorio destino es un archivo: {padre}")
    return plan


def inicializar(oracle: str | None = None) -> None:
    """Prepara Factory en ROOT. Con `oracle`, adopta el proyecto Oracle que ya está en esa carpeta en vez de crear uno en la raíz."""
    marca = cli.ROOT / estructura.DIR
    if marca.is_symlink() or (marca.exists() and not marca.is_dir()):
        raise cli.FactoryError(f"{marca} existe y no es una carpeta de Factory: renombrala o quitala antes de ejecutar init; no creé nada")
    if oracle is None and (marca / "config.json").is_file():  # ya inicializado: se respeta la carpeta de Oracle configurada
        configurada = cli.config_proyecto()["oracle"]
        oracle = None if configurada in (".", "") else configurada
    afuera = estructura.raiz_del_proyecto(cli.ROOT.parent) if cli.ROOT.parent != cli.ROOT else None
    if afuera is not None:
        print(f"Aviso: esta carpeta está dentro del proyecto Factory {afuera}; init crea un proyecto anidado y los comandos "
              "usarán el más cercano.", file=sys.stderr)
    if oracle is not None:
        relativa = cli.carpeta_relativa(oracle)
        if (oracle in ("", ".") or relativa is None
                or (cli.ROOT / relativa).resolve() != cli.ROOT / relativa or not (cli.ROOT / relativa / "oracle.json").is_file()):
            raise cli.FactoryError(f"--oracle es la carpeta de un proyecto Oracle que ya existe dentro de este proyecto "
                               f"(con oracle.json); «{oracle}» no lo es. No creé nada")
    cli.ROOT.mkdir(parents=True, exist_ok=True)
    propios = ("tareas", ".gitignore", "openspec/changes", estructura.DIR)
    oracle_raiz = ("catalogos", "corpus", "diferencial", "relaciones", "requisitos", "macros", "oracle.json")
    for nombre in propios + (() if oracle else oracle_raiz):
        cli.ruta_segura(cli.ROOT / nombre)
    de_antes = {nombre for nombre in cli.SIN_USO_DE_ORACLE if (cli.ROOT / nombre).exists()}
    for comando in (["tasks", "init", str(cli.ROOT), "--sin-readme"], *([] if oracle else [["oracle", "init", str(cli.ROOT)]])):
        resultado = cli.ejecutar(comando)
        if resultado.returncode:
            raise cli.FactoryError(resultado.stderr or resultado.stdout)
    for nombre in cli.SIN_USO_DE_ORACLE:  # las crea `oracle init` y Factory no las usa: vacías, sólo confunden
        carpeta = cli.ROOT / nombre
        if nombre not in de_antes and carpeta.is_dir() and not carpeta.is_symlink() and not any(carpeta.iterdir()):
            carpeta.rmdir()
    cli.ruta_segura(cli.CHANGES).mkdir(parents=True, exist_ok=True)
    for sub in ('cambios', 'local'):
        cli.ruta_segura(cli.ROOT / estructura.DIR / sub).mkdir(parents=True, exist_ok=True)
    config = cli.ruta_segura(cli.ROOT / estructura.DIR / 'config.json')
    if not config.exists() and not (cli.ROOT / 'factory.json').exists():  # con la configuración anterior en la raíz, la pasa `migrar`
        datos = {"modo_por_defecto": modos.POR_DEFECTO, "tipos_obligatorios": False}
        config.write_text(json.dumps({**datos, **({"oracle": oracle} if oracle else {})}, indent=2) + "\n", encoding='utf-8')
    elif oracle and config.exists():  # ya inicializado: sólo se anota dónde está el proyecto Oracle
        datos = json.loads(config.read_text(encoding='utf-8'))
        if datos.get("oracle") != oracle:
            cli.escribir_atomico(config, (json.dumps({**datos, "oracle": oracle}, indent=2, ensure_ascii=False) + "\n").encode())
    leeme = cli.ruta_segura(cli.ROOT / estructura.DIR / 'LEEME.md')
    if not leeme.exists():
        leeme.write_text(cli.LEEME_FACTORY, encoding='utf-8')
    ignore = cli.ruta_segura(cli.ROOT / '.gitignore')
    contenido = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    pendientes = [line for line in (estructura.IGNORAR_LOCAL, estructura.IGNORAR_CLUE, '__pycache__/', '*.py[cod]')
                  if line not in contenido.splitlines()]
    if pendientes:
        with ignore.open('a', encoding='utf-8') as archivo:
            archivo.write(('\n' if contenido and not contenido.endswith('\n') else '') + '\n'.join(pendientes) + '\n')
    versionados = cli.ejecutar(["git", "ls-files", "--", ":(glob)" + estructura.IGNORAR_CLUE + "**"]).stdout.split()
    if versionados:  # el .gitignore no saca del índice lo que ya estaba versionado; init no toca el índice
        print("Aviso: hay paquetes de Clue versionados de antes; ahora son locales. Para dejar de versionarlos sin borrarlos: "
              "git rm -r --cached " + " ".join(sorted({str(Path(p).parent) for p in versionados})), file=sys.stderr)
    # Git no versiona carpetas vacías: sin esto, quien clona el proyecto no tiene tareas/ ni catalogos/ y no puede
    # crear un cambio. .factory/local/ no: es local y Git la ignora.
    raiz_oracle = cli.ROOT / (oracle or "")
    for carpeta_vacia in (cli.ROOT / "tareas", cli.CHANGES, cli.ROOT / estructura.DIR / "cambios", raiz_oracle / "catalogos",
                          raiz_oracle / "requisitos", raiz_oracle / "macros"):
        if carpeta_vacia.is_dir() and not any(carpeta_vacia.iterdir()):
            (cli.ruta_segura(carpeta_vacia) / ".gitkeep").write_text("", encoding="utf-8")
        regla = cli.ejecutar(["git", "check-ignore", "-v", "--", str(carpeta_vacia / ".gitkeep")])
        if not regla.returncode:  # un .gitignore del proyecto la excluye: Factory no pisa esa regla, pero avisa
            print(f"Aviso: Git ignora {carpeta_vacia.relative_to(cli.ROOT)}/ ({regla.stdout.split(chr(9))[0].strip()}): quien "
                  "clone el proyecto no la va a tener. Si es de Factory, sacá esa regla del .gitignore.", file=sys.stderr)
    print(f'Factory inicializada en {cli.ROOT}. No se crearon commits ni aprobaciones.')
    print(f'Acuerdos: {cli.CHANGES}; tareas: {cli.ROOT / "tareas"}; proyecto Oracle: {cli.ROOT / (oracle or "")}.')
    print(f'Carpeta propia de Factory: {cli.ROOT / estructura.DIR} (versionada, salvo local/, que Git ignora).')
    print('Conservé la configuración existente. .gitignore excluye salidas temporales y bytecode de Python.')
    print('Si el proyecto todavía no usa Git, ejecutá git init desde esta carpeta; Factory no crea commits.')
    print(cli.instalar_hook())
    if cli.PRODUCTO:  # preparando un almacén: la guía va al producto con `agentes`, no al almacén (conectar no toca el producto)
        print("La guía para agentes va en el producto, sin versionar: corré oracle-factory agentes (y skill --instalar) desde el producto.")
    else:
        cli.comando_agentes(False)
    if cli.PRODUCTO:  # los drivers de merge van en la configuración de Git del clon, y en un almacén Factory no la escribe
        print("Almacén de registros: Factory no escribe su configuración de Git, así que no instala la unión de registros al integrar.")
    elif not cli.ejecutar(["git", "rev-parse", "--git-dir"]).returncode:
        print(cli.instalar_union())
    print('Próximo paso: oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"')
    print('Para recuperar cambios existentes: oracle-factory listar')


def comando_migrar(verificar: bool) -> None:
    """Pasa el estado de cada cambio y la configuración a .factory/ (fase 2 de la estructura)."""
    movimientos, problemas, avisos = migracion.planear(cli.ROOT)
    for texto in problemas + avisos:
        print(f"Aviso: {texto}", file=sys.stderr)
    if verificar:
        for m in movimientos:
            print(f"{m['cambio']}: {m['origen'].relative_to(cli.ROOT)} -> {m['destino'].relative_to(cli.ROOT)}"
                  + ("" if m["estado"] == "escribir" else " (ya está en el lugar nuevo; sólo falta borrar el viejo)"))
        print(f"Por migrar: {len(movimientos)} archivos.")
        if any(m["origen"].name == "factory.json" and m["origen"].parent == cli.ROOT for m in movimientos):
            print("Aviso: factory.json de la raíz es parte del producto: moverlo cambia la huella y vence las revisiones vigentes.")
        if movimientos or problemas:
            raise SystemExit(1)
        return
    if any(m["origen"].name == "factory.json" and m["origen"].parent == cli.ROOT for m in movimientos):
        print("Aviso: factory.json de la raíz es parte del producto: moverlo cambia la huella y vence las revisiones vigentes; "
              "hay que volver a preparar y registrar la revisión de los cambios abiertos.")
    hechos = migracion.aplicar(movimientos)
    cambios = sorted({m["cambio"] for m in movimientos})
    print(f"Migrados {hechos} archivos de {len(cambios)} cambios y configuración. No hice commits: revisá con git status y confirmalos.")
    if problemas:
        raise SystemExit(1)


def comando_procedencia(args) -> None:
    """El inventario de las dependencias, quién usó una y la auditoría contra avisos OSV. Local, salvo --consultar-osv --red."""
    if args.consultar_osv:
        if not args.red:
            raise cli.FactoryError("--consultar-osv se conecta a OSV.dev: autorizalo con --red (sale sólo nombre, versión y ecosistema de cada dependencia)")
        if args.buscar or args.auditar or args.id or args.avisos:
            raise cli.FactoryError("--consultar-osv mira todos los inventarios guardados y no se combina con --buscar, --auditar, --avisos ni un cambio")
        try:
            print(osv_mod.informe(cli.ROOT, args.osv_url, args.salida, args.json), end="")
        except procedencia_mod.ProcedenciaError as e:
            raise cli.FactoryError(str(e)) from e
        return
    if args.red or args.salida:
        raise cli.FactoryError("--red y --salida son para --consultar-osv")
    if args.buscar and args.auditar:
        raise cli.FactoryError("--buscar y --auditar no se combinan; usá uno")
    if (args.buscar or args.auditar) and args.id:
        raise cli.FactoryError("--buscar y --auditar miran todos los inventarios guardados: no llevan un cambio")
    if args.auditar and not args.avisos:
        raise cli.FactoryError("--auditar necesita --avisos ARCHIVO con avisos en formato OSV")
    if args.avisos and not args.auditar:
        raise cli.FactoryError("--avisos es para --auditar")
    try:
        if args.buscar or args.auditar:
            print(procedencia_mod.informe_buscar(cli.ROOT, args.buscar, args.json) if args.buscar
                  else procedencia_mod.informe_auditar(cli.ROOT, args.avisos, args.json), end="")
            return
        python = procedencia_mod.python_del_proyecto(cli.PRODUCTO or cli.ROOT, args.python)
        bom, diferencias, confiable = procedencia_mod.inventario(cli.PRODUCTO or cli.ROOT, python)
    except procedencia_mod.ProcedenciaError as e:
        raise cli.FactoryError(str(e)) from e
    cuerpo = procedencia_mod.texto(bom)
    guardado = None
    if args.id:
        carpeta, estado = cli.abierto(args.id)
        head = cli.git_producto(["git", "rev-parse", "HEAD"])
        if head.returncode:
            raise cli.FactoryError("procedencia necesita un repositorio Git con al menos un commit")
        sha = cli.candidato_vigente(args.id) or head.stdout.strip()[:7]
        destino = cli.ROOT / estructura.DIR / "cambios" / args.id / "candidatos" / sha / "procedencia" / "cyclonedx.json"
        cli.ruta_segura(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        cli.escribir_atomico(destino, cuerpo.encode("utf-8"))
        huella = cli.sha256(cuerpo.encode("utf-8"))
        cli.evento(estado, "procedencia_registrada", candidato=sha, archivo=destino.relative_to(cli.ROOT).as_posix(), huella=huella,
               componentes=len(bom["components"]), confiable=confiable, diferencias=len(diferencias))
        cli.guardar(carpeta, estado)
        guardado = (destino.relative_to(cli.ROOT).as_posix(), huella)
    if args.json:
        print(cuerpo, end="")
        return
    fuente = "uv.lock" if any(procedencia_mod.propiedad(c, "factory:fuente") == "uv.lock" for c in bom["components"]) else "el entorno instalado"
    print(f"Inventario de dependencias de Python: {len(bom['components'])} componentes, según {fuente}.")
    print("Confiable: sí." if confiable else "Confiable: no.")
    for d in diferencias:
        print(f"  - {d}")
    for c in bom["components"]:
        if procedencia_mod.propiedad(c, "factory:corregida"):
            print(f"  corregido por Lightwell: {c['name']} {c['version']}")
    if guardado:
        print(f"Guardado en {guardado[0]} (sha256 {guardado[1][:16]}…) y registrado en {args.id}.")
    else:
        print("No se guardó (indicá el cambio para guardarlo en su candidato) ni se mostró el CycloneDX (--json).")


def comando_autonomia(etapa: str | None, modo: str | None, como_json: bool) -> int:
    """Muestra quién decide en cada etapa; con etapa y modo, una persona la cambia."""
    if etapa and not modo:
        raise cli.FactoryError(f"indicá el modo de la etapa {etapa}: {' o '.join(modos.MODOS_ETAPA)}")
    if etapa:
        if cli.AGENTE:
            raise cli.FactoryError(f"cambiar la autonomía de una etapa lo decide una persona, sin --agente: {cli.AGENTE} no puede dársela a un agente")
        if cli.config_proyecto()["autonomia"][etapa] == modo:
            print(f"La etapa {etapa} ya está en {modo}.")
            return 0
        cli.confirmar_persona((f"Poner la etapa {etapa} en {modo}", f"Poner {etapa} en {modo}",
                           "un agente " + ("podrá decidir en esa etapa" if modo == "autonomo" else "ya no podrá decidir en esa etapa")),
                          "cambio de autonomía cancelado; la configuración sigue igual")
        ruta = cli.ruta_segura(cli.ROOT / estructura.DIR / "config.json")
        if not ruta.is_file():
            raise cli.FactoryError(f"no hay {estructura.DIR}/config.json: iniciá el proyecto con oracle-factory init")
        crudo = ruta.read_bytes()
        datos = json.loads(crudo)
        datos["autonomia"] = {**(datos.get("autonomia") or {}), etapa: modo}
        cli.escribir_atomico(ruta, (json.dumps(datos, indent=2, ensure_ascii=False) + "\n").encode(), esperado=crudo)
        print(f"La etapa {etapa} quedó en {modo}. El cambio está en {estructura.DIR}/config.json: commitealo para que valga en el equipo.")
        return 0
    filas = cli.filas_autonomia()
    if como_json:
        print(json.dumps(filas, ensure_ascii=False, indent=2))
        return 0
    print("Autonomía por etapa (quién decide por la vía de agente; una persona decide siempre):")
    for f in filas:
        print(f"  {f['etapa']:13} {f['modo']:13} decide: {f['decide']:30} " + (f"lo aplica: {f['comando']}" if f["aplica_hoy"] else "sin comando de Factory todavía"))
    return 0


def comando_desplegar(simular: bool, autorizar: bool, commit: str | None, destinos: list[str], cambios: bool = False) -> int:
    """El plan de despliegue; sólo una persona desde su terminal lo ejecuta."""
    quien = cli.actor()
    autonoma = modos.via_agente_etapa(cli.config_proyecto()["autonomia"]["produccion"]) == "decide"  # la etapa producción en `autonomo`
    if autorizar and quien["tipo_actor"] != "persona" and not (autonoma and quien["tipo_actor"] == "agente"):
        raise cli.FactoryError("autorizar un despliegue lo hace una persona desde su terminal: un agente puede armar y simular el plan "
                           "(oracle-factory desplegar --simular), no ejecutarlo")
    try:
        decl = despliegue_mod.cargar(cli.ROOT)
        codigo_puerta, texto_puerta = cli.verificar_en_proceso(["puerta"])
        plan = despliegue_mod.armar_plan(cli.ROOT, decl, commit, destinos or None, puerta=lambda: (codigo_puerta == 0, texto_puerta), cambios=cambios)
    except (despliegue_mod.DeclaracionInvalida, despliegue_mod.DespliegueNegado) as e:
        raise cli.FactoryError(str(e)) from e
    previa = despliegue_mod.sin_terminar(cli.ROOT)
    if previa:  # avisa y no bloquea: quien autoriza mira esos destinos
        print(f"Aviso: la corrida anterior ({previa['id']}) no terminó: quedó «{previa['resultado']}»; pudo haber tocado "
              + (", ".join(previa["tocados"]) or "ningún destino") + f". Mirá su registro (.factory/despliegues/{previa['id']}/registro.json) antes de autorizar.")
    print(despliegue_mod.texto_plan(decl, plan))
    if cambios and not plan["orden"]:
        return 0
    faltan = despliegue_mod.faltan_secretos(decl, plan)
    if faltan:
        print("Faltan en el entorno estos secretos (sólo los nombres): " + ", ".join(faltan))
    if not autorizar or simular:
        print("No se ejecutó nada. Para ejecutarlo, una persona: oracle-factory desplegar --autorizar" + (f" --commit {commit}" if commit else ""))
        return 0
    try:
        registro = despliegue_mod.ejecutar(cli.ROOT, decl, plan, autorizo=quien["actor"], planeo=quien["actor"])
    except despliegue_mod.DespliegueNegado as e:
        raise cli.FactoryError(str(e)) from e
    for n in registro["orden"]:
        r = registro["destinos"][n]
        print(f"  {n}: {r['estado']}" + (f" — {r['motivo']}" if r["motivo"] else ""))
    print(f"Conjunto: {registro['conjunto']['resultado']}")
    if registro["aviso"]:
        print("Aviso: " + registro["aviso"])
    print(f"Resultado: {registro['motivo']} (registro: .factory/despliegues/{registro['id']}/registro.json)")
    return 0 if registro["resultado"] == "todo_funciona" else 1


def comando_autopilot(ident: str, como_json: bool, ejecutar: bool = False, lanzar: str | None = None, max_pasos: int = 10,
                      max_minutos: float = 120, entorno: list[str] | None = None) -> int:
    """El conductor. Sin `--ejecutar`, sólo lectura: lo que haría ahora (`autopilot.decidir` sobre los datos de `estado`). Con `--ejecutar`
    (y `--agente`), el bucle de `conductor.bucle`: corre lo mecánico, lanza al agente para lo creativo, con topes y el porqué en el registro."""
    entregar = list(entorno or [])
    if entregar and not (ejecutar and lanzar):  # antes de la salida de sólo lectura: una opción que no vale en este modo no se ignora en silencio
        raise cli.FactoryError("--entorno entrega variables al agente que lanza --lanzar: sólo vale con --ejecutar y --lanzar; no escribí nada")
    for nombre in entregar:
        if not conductor.NOMBRE_DE_VARIABLE.fullmatch(nombre):
            raise cli.FactoryError(f"--entorno {nombre!r} no es el nombre de una variable (letras, dígitos y guion bajo, sin empezar con un dígito); no escribí nada")
    if not ejecutar:
        decision = autopilot.decidir(cli.datos_estado(ident))
        if como_json:
            cli.imprimir_json(decision)
            return 0
        print(f"Autopilot {ident}: {decision['accion']}" + (f" ({decision['quien']})" if decision["quien"] else ""))
        if decision["comando"]:
            print("Comando: " + decision["comando"] + ("  (con --agente NOMBRE)" if decision["quien"] == "agente" else ""))
        if decision["instruccion"]:
            print("Instrucción: " + decision["instruccion"])
        print("Motivo: " + decision["motivo"])
        for freno in decision["frenos"]:
            print(f"  FRENO {freno.get('id')}: {freno.get('motivo')}")
        return 0
    if not cli.AGENTE:
        raise cli.FactoryError("autopilot --ejecutar actúa como agente: corré `oracle-factory --agente NOMBRE autopilot ID --ejecutar`; no escribí nada")
    if max_pasos < 1 or not max_minutos > 0:
        raise cli.FactoryError("--max-pasos y --max-minutos tienen que ser positivos; no escribí nada")
    try:
        comando_lanzar = shlex.split(lanzar) if lanzar else None
    except ValueError as e:
        raise cli.FactoryError(f"--lanzar no se puede leer como un comando: {e}; no escribí nada")
    cli.datos_estado(ident)  # un cambio que no existe falla acá, nombrándolo, antes de escribir nada
    correr, lanzador = conductor.ejecutor(cli.ROOT, cli.AGENTE, entregar)
    resultado = conductor.bucle(ident, lambda: cli.datos_estado(ident), correr, lanzador, comando_lanzar, max_pasos, max_minutos)
    if como_json:
        cli.imprimir_json(resultado)
    else:
        print(f"Autopilot {ident}: {len(resultado['pasos'])} paso(s)")
        for i, p in enumerate(resultado["pasos"], 1):
            print(f"  {i}. {p['accion']}: {p['comando'] or p['instruccion']} → código {p['codigo']}")
        print("Se detuvo: " + resultado["motivo"])
        if resultado["decision"] and resultado["decision"]["accion"] == "pedir_a_persona":
            print("Comando para una persona: " + resultado["decision"]["comando"])
        if resultado.get("aviso"):
            print("Aviso: " + resultado["aviso"])
    return 1 if resultado["fallo"] else 0


def comando_ruta(identificador: str, tipo: str) -> None:
    cli.leer(identificador)  # el cambio tiene que existir
    head = cli.git_producto(["git", "rev-parse", "HEAD"])
    if head.returncode:
        raise cli.FactoryError("ruta necesita un repositorio Git con al menos un commit")
    try:
        # El candidato vigente, como pedir-revision y juzgar: un commit que sólo guarda registros no es un candidato nuevo.
        # Si no hay, HEAD con los 7 primeros del hash completo (--short=7 lo alarga si es ambiguo y la carpeta cambiaría).
        sha = cli.candidato_vigente(identificador) or head.stdout.strip()[:7]
        print(cli.estructura.ruta_canonica(cli.ROOT, identificador, tipo, sha))
    except ValueError as e:
        raise cli.FactoryError(str(e)) from e


def comando_buscar(texto: str, maximo: int) -> None:
    if not texto.strip():
        raise cli.FactoryError("indicá el texto a buscar")
    # Un .factory enlazado no es nuestra carpeta y no se lee a través de él: entonces se busca en la raíz. Una carpeta de
    # Oracle mal configurada, en cambio, falla y dice la causa.
    oracle = "" if (cli.ROOT / cli.estructura.DIR).is_symlink() else cli.oracle_rel()
    lineas, total, omitidos = cli.estructura.buscar(cli.ROOT, texto, maximo, oracle)
    for linea in lineas:
        print(linea)
    print(f"{total} coincidencia(s)" + (f"; se muestran {len(lineas)}, usá --max para ver más" if total > len(lineas) else ""))
    if omitidos:
        print(f"Aviso: {omitidos} archivo(s) omitido(s) por superar {cli.estructura.LIMITE_ARCHIVO // 1_000_000} MB; el texto podría estar ahí.")


def comando_skill(instalar: bool, forzar: bool) -> int:
    """Muestra la skill de agente o, con --instalar, la escribe en el proyecto (nunca fuera de él)."""
    if forzar and not instalar:
        raise cli.FactoryError("--forzar sólo vale con --instalar")
    if not instalar:
        print(cli.skill_mod.texto(), end="")
        return 0
    if cli.PRODUCTO:
        return cli.almacenes.skill_en_producto(cli, forzar)
    try:
        estado, ruta = cli.skill_mod.instalar(cli.ROOT, forzar)
    except cli.skill_mod.SkillError as e:
        raise cli.FactoryError(str(e)) from e
    print({"instalada": f"Skill instalada en {ruta.relative_to(cli.ROOT)}.", "reemplazada": f"Skill reemplazada en {ruta.relative_to(cli.ROOT)}.",
           "igual": f"La skill ya estaba instalada en {ruta.relative_to(cli.ROOT)}: sin cambios."}[estado])
    return 0


def comando_agentes(verificar: bool, en_el_repo: bool = False) -> None:
    """El bloque para agentes de AGENTS.md (y la línea @AGENTS.md de CLAUDE.md), o --verificar que estén al día."""
    if en_el_repo and cli.AGENTE:
        raise cli.FactoryError(f"agentes --en-el-repo es una decisión de una persona (versionar la guía en el repo del producto); "
                           f"{cli.AGENTE} no puede. No escribí nada")
    if cli.PRODUCTO:  # con almacén aparte, en el producto: sin versionar, o en la guía que ya versiona con --en-el-repo
        return cli.almacenes.guia_en_producto(cli, verificar, en_el_repo)
    nuevo = cli.agentes_mod.bloque(cli.config_proyecto()["modo_por_defecto"])
    rutas = [cli.ruta_segura(cli.ROOT / "AGENTS.md"), cli.ruta_segura(cli.ROOT / "CLAUDE.md")]
    actuales = [r.read_text(encoding="utf-8") if r.is_file() else "" for r in rutas]
    try:
        esperados = [cli.agentes_mod.con_bloque(actuales[0], nuevo), cli.agentes_mod.con_claude(actuales[1])]
    except cli.agentes_mod.MarcasRotas as e:
        raise cli.FactoryError(str(e)) from e
    if verificar:
        viejos = [r.name for r, a, e in zip(rutas, actuales, esperados) if a != e]
        if viejos:
            raise cli.FactoryError(f"la guía para agentes no está al día en {', '.join(viejos)}; corré oracle-factory agentes")
        print("La guía para agentes está al día en AGENTS.md (y CLAUDE.md la incluye).")
        return
    for ruta, actual, esperado in zip(rutas, actuales, esperados):
        if actual != esperado:
            cli.escribir_atomico(ruta, esperado.encode("utf-8"))
    print("Guía para agentes en AGENTS.md (CLAUDE.md la incluye con @AGENTS.md): quién decide qué, los comandos de una "
          "persona y de un agente, y cómo consultar el proyecto.")


def comando_preguntar(args) -> None:
    if args.evaluar:
        if not args.salida:
            raise cli.FactoryError("--evaluar necesita --salida CARPETA (nueva)")
        c = cli.rag_mod.evaluar(cli, args.salida.resolve(), casos=args.casos)
        print(f"{c['aciertos']} de {c['preguntas']} preguntas de oro con un archivo esperado entre los {cli.rag_mod.PRIMEROS} "
              f"primeros (MRR {c['mrr']}, modo {c['modo']}, modelo {c['modelo']}). Hechos: {args.salida / 'hechos.json'}")
        hechos = json.loads((args.salida / 'hechos.json').read_text(encoding='utf-8'))
        for grupo in hechos['preguntar_grupo']:
            print(f"{grupo['grupo']}: {grupo['aciertos']}/{grupo['preguntas']}; errores: {grupo['errores']}; "
                  f"abstenciones incorrectas: {grupo['abstenciones_incorrectas']}; simulado: {bool(grupo['simulado'])}")
        return
    if args.casos:
        raise cli.FactoryError('--casos se usa junto a --evaluar')
    datos = cli.rag_mod.preguntar(cli, args.texto, args.maximo)
    print(json.dumps(datos, ensure_ascii=False, indent=2) if args.json else cli.rag_mod.texto(datos))


def listar(fase: str | None = None, abiertos: bool = False, cerrados: bool = False) -> None:
    cli.ruta_segura(cli.CHANGES)
    if not cli.CHANGES.exists():
        print('No hay cambios Factory. Empezá con oracle-factory init.')
        return
    encontrados = 0
    for carpeta in sorted(cli.CHANGES.iterdir()):
        if not cli.ID_RE.fullmatch(carpeta.name):
            continue
        cli.ruta_segura(carpeta)
        if not (cli.ruta_registro(carpeta)).exists():
            continue
        try:
            _, estado = cli.leer(carpeta.name)
        except cli.FactoryError as e:  # uno roto no deja sin lista a los demás
            print(f"{carpeta.name}  ilegible: {e}")
            encontrados += 1
            continue
        if (fase and estado['fase'] != fase) or (abiertos and estado['fase'] in ('cerrada', 'abandonada')) \
                or (cerrados and estado['fase'] != 'cerrada'):
            continue
        print(f"{carpeta.name}  {estado['fase']}{' (archivado)' if estado.get('archivo') else ''}  {estado['titulo']}")
        encontrados += 1
    if not encontrados:
        print('No hay cambios que coincidan con el filtro.' if (fase or abiertos or cerrados)
              else 'No hay cambios Factory; las tareas del tracker por sí solas no son cambios Factory.')
    print(f'Acuerdos: {cli.CHANGES}')


# Al final a propósito: `cli` importa este módulo, y así se puede importar cualquiera de los dos primero. Acá `cli` sólo
# cuando se llama a una función, no al importar.
from . import cli  # noqa: E402
