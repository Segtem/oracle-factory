"""Pedir revisiones a revisores independientes, preparar el paquete y decidir la revisión (sacado de cli.py).

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo (`cli.NOMBRE`), no lo copia: así un valor
cambiado en `cli` (la raíz del proyecto en las pruebas, por ejemplo) vale también acá."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import contextlib
import fcntl
import io
import json
import os
import re
import subprocess
import sys
import tempfile

from . import cli
from . import estructura
from . import preparacion
from . import revision as documentos_revision
from . import revisores as revisores_mod


def bytes_json(valor: dict) -> bytes:
    return (json.dumps(valor, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def leer_regular(ruta: Path, nombre: str) -> bytes:
    if not ruta.is_file():
        raise cli.FactoryError(f'{nombre}: se requiere un archivo regular: {ruta}')
    return ruta.read_bytes()


def guardar_par_revision(identificador: str, prefijo: str, informe: bytes, decisiones: bytes) -> tuple[Path, Path]:
    raiz = cli.ruta_segura(cli.ROOT / 'tareas' / identificador / 'revisiones')
    destino = None
    try:
        if not cli.ruta_segura(raiz.parent / 'TAREA.md').is_file():
            raise cli.FactoryError(f'no encuentro la tarea: {raiz.parent / "TAREA.md"}')
        raiz.mkdir(parents=True, exist_ok=True)
        destino = Path(tempfile.mkdtemp(prefix=prefijo + '-', dir=raiz))
        for nombre, datos in (('informe.json', informe), ('decisiones.json', decisiones)):
            archivo = cli.ruta_segura(destino / nombre)
            with archivo.open('xb') as salida:
                salida.write(datos)
        return destino / 'informe.json', destino / 'decisiones.json'
    except (OSError, cli.FactoryError) as e:
        raise cli.FactoryError(f'no se completaron los documentos de revisión: {e}. '
                           f'Revisá posibles archivos residuales en {destino or raiz}; no se sobrescribieron antecedentes ni se publicó un gate nuevo.') from e


def pedido_de_revision(identificador: str) -> str:
    """El comando completo para pedir una revisión con el primer revisor configurado; sin revisores, qué falta y dónde declararlo."""
    revisores = sorted(cli.config_proyecto()["revisores"])
    if revisores:
        return f"oracle-factory pedir-revision {identificador} --a {revisores[0]}"
    return ("falta un revisor independiente: declaralo en .factory/config.json, por ejemplo " + revisores_mod.EJEMPLO
            + f"; después: oracle-factory pedir-revision {identificador} --a codex (o el nombre que hayas declarado)")


def base_vacia() -> str:
    """Un commit sin archivos, siempre el mismo, para revisar todo el producto de un candidato sin commit anterior.

    Es un objeto de Git sin rama que lo apunte: no toca ramas, historia ni configuración (la identidad va sólo en este comando).
    """
    arbol = subprocess.run(
        ["git", "hash-object", "-t", "tree", "-w", "--stdin"], cwd=cli.ROOT, input="", capture_output=True, text=True)
    fijo = {**os.environ, "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000", "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000"}
    for rol in ("AUTHOR", "COMMITTER"):  # la identidad del entorno ganaría sobre la fija y cambiaría el SHA
        fijo[f"GIT_{rol}_NAME"], fijo[f"GIT_{rol}_EMAIL"] = "Oracle Factory", "factory@invalid"
    p = subprocess.run(["git", "commit-tree", arbol.stdout.strip(), "-m", "base vacía para revisar el producto entero"],
                       cwd=cli.ROOT, env=fijo, capture_output=True, text=True)
    if arbol.returncode or p.returncode:
        raise cli.FactoryError(f"no pude crear la base vacía: {(arbol.stderr or p.stderr).strip()}")
    return p.stdout.strip()


def preparar_revision(identificador: str) -> tuple[Path, Path]:
    carpeta, estado = cli.abierto(identificador)
    registro = (cli.ruta_registro(carpeta)).read_bytes()
    if json.loads(registro) != estado:
        raise cli.FactoryError('registro cambió durante la lectura; volvé a preparar')
    cli.exigir_spec(carpeta, estado)
    contexto, docs = cli.contexto_producto(), cli.documentos(carpeta, estado)
    informe, decisiones = documentos_revision.plantillas(identificador, contexto, docs)
    sha = cli.candidato_vigente(identificador)
    if not sha:
        print("Aviso: no hay candidato vigente (un commit con su carpeta de candidato y sin cambios de producto después), así "
              "que el informe queda sin informes de revisores ni evidencia. Pedí una revisión: "
              f"{cli.pedido_de_revision(identificador)}", file=sys.stderr)
    if sha:
        todos, evidencia, archivos, avisos = cli.material_del_candidato(identificador, sha)
        revisores = [r for r in todos if not r.get("reemplazado_por")]
        informe, decisiones = preparacion.completar(informe, decisiones, revisores, evidencia, archivos)
        vueltas = []
        for anterior in cli.candidatos_anteriores(identificador, sha):
            # Las vueltas anteriores pasan por la misma validación que las del candidato vigente.
            anteriores, _, _, avisos_anteriores = cli.material_del_candidato(identificador, anterior)
            vueltas += [{"candidato": anterior, **r} for r in anteriores]
            avisos += avisos_anteriores
        vueltas += [{"candidato": sha, **r} for r in todos if r.get("reemplazado_por")]  # vueltas anteriores en el mismo candidato
        informe["comprobaciones"] = (informe["comprobaciones"] or []) + preparacion.vueltas_anteriores(vueltas) or None
        for aviso in avisos:
            print(f'Aviso: {aviso}', file=sys.stderr)
        print(f'Candidato {sha}: {len(revisores)} informe(s) de revisores, '
              f'{len(informe["hallazgos"])} hallazgo(s), evidencia {"sí" if evidencia else "no"}.')
    rutas = cli.guardar_par_revision(identificador, 'preparacion', cli.bytes_json(informe), cli.bytes_json(decisiones))
    try:
        cli.exigir_spec(carpeta, estado)
        if (not cli.mismo_producto(contexto, cli.contexto_producto()) or cli.documentos(carpeta, estado) != docs
                or (cli.ruta_registro(carpeta)).read_bytes() != registro):
            raise cli.FactoryError('cambió el producto o el registro durante la preparación')
    except (cli.FactoryError, OSError) as e:
        raise cli.FactoryError(f'{e}; no uses la preparación en {rutas[0].parent}; prepará una nueva. No se cambiaron gates.') from e
    print(f'Informe pendiente: {rutas[0]}\nDecisiones pendientes: {rutas[1]}')
    print(f"Cambio: {identificador}; HEAD: {contexto['head']}; huella de archivos: {contexto['archivos_sha256']}")
    print('La huella incluye cambios locales; confirmá el producto antes de revisar. Preparar no analiza ni aprueba.')
    print('Completá el informe y luego su SHA-256 en decisiones; resolvé los hallazgos con criterio humano.')
    print(f'Próximo paso: oracle-factory revision {identificador} --formato guiado --informe RUTA_INFORME '
          '--decisiones RUTA_DECISIONES --revisor NOMBRE --decision DECISION')
    print('DECISION debe ser aprobar o cambios, elegida por la persona después de revisar.')
    return rutas


def material_del_candidato(identificador: str, sha: str) -> tuple[list[dict], dict | None, list[str], list[str]]:
    """(informes de revisores usables, evidencia, archivos del paquete, avisos) de la carpeta del candidato."""
    raiz = estructura.ruta_canonica(cli.ROOT, identificador, "evidencia", sha).parent
    avisos: list[str] = []

    def cargar(ruta: Path):
        try:
            datos = json.loads(cli.ruta_segura(ruta).read_text(encoding="utf-8"))
        except (OSError, ValueError, cli.FactoryError) as e:
            avisos.append(f"{ruta.relative_to(cli.ROOT)} no se pudo leer ({type(e).__name__}); no lo uso")
            return None
        if not isinstance(datos, dict):
            avisos.append(f"{ruta.relative_to(cli.ROOT)} no es un objeto JSON; no lo uso")
            return None
        return datos

    paquetes = [p for p in (cargar(r) for r in sorted((raiz / "clue").glob("*.json"))) if p] if (raiz / "clue").is_dir() else []
    archivos = sorted({f["file"] for p in paquetes for f in p.get("files") or [] if isinstance(f, dict) and f.get("file")})
    revisores = []
    for ruta in sorted((raiz / "revision").glob("*.json")) if (raiz / "revision").is_dir() else []:
        datos, rel = cargar(ruta), ruta.relative_to(cli.ROOT).as_posix()
        if datos is None:
            continue
        if datos.get("schema_version") != preparacion.ESQUEMA_CLUE:
            avisos.append(f"{rel} no es un informe de Oracle Clue; no lo uso")
            continue
        if not str(datos.get("head") or "").startswith(sha):
            avisos.append(f"{rel} es de otro candidato ({str(datos.get('head'))[:7]}); no lo uso")
            continue
        paquete = next((p for p in paquetes if p.get("diff_sha256") == datos.get("diff_sha256")
                        and p.get("context_sha256") == datos.get("context_sha256")), None)
        if paquete is None or not Path(str(paquete.get("repo"))).is_dir():
            # Un informe que no se puede validar no se usa (falta su paquete o su checkout).
            falta = "su paquete en clue/" if paquete is None else f"el checkout del paquete ({paquete.get('repo')})"
            avisos.append(f"{rel} no se puede validar: falta {falta}; recrealo con oracle-factory ruta {identificador} "
                          "checkout y no lo uso")
            continue
        if cli.producto_excluido(paquete):  # Clue confía en las exclusiones del paquete; Factory las comprueba
            avisos.append(f"{rel} viene de un paquete que deja afuera archivos del producto "
                          f"({', '.join(map(str, cli.producto_excluido(paquete)))}); no lo uso")
            continue
        ruta_paquete = next(r for r in sorted((raiz / "clue").glob("*.json")) if cargar(r) == paquete)
        p = cli.ejecutar(["oracle-clue", "validar", str(ruta), "--paquete", str(ruta_paquete), "--repo", str(paquete["repo"])])
        if p.returncode:
            avisos.append(f"{rel} no pasa la validación de Clue: {(p.stderr or p.stdout).strip()[:300]}; no lo uso")
            continue
        revisores.append({"ruta": rel, "datos": datos, "validacion": "validado con oracle-clue"})
    # El informe más nuevo de cada revisor (<revisor>-<n>.json) reemplaza a los anteriores del mismo revisor, aunque no
    # se pueda usar: entonces ese revisor no aporta nada, en vez de volver a su vuelta anterior.
    ultimo: dict[str, tuple[int, str]] = {}
    for archivo in sorted((raiz / "revision").glob("*.json")) if (raiz / "revision").is_dir() else []:
        m = re.fullmatch(r"(.+)-(\d+)\.json", archivo.name)
        if m and int(m[2]) > ultimo.get(m[1], (0, ""))[0]:
            ultimo[m[1]] = (int(m[2]), archivo.relative_to(cli.ROOT).as_posix())
    for r in revisores:
        m = re.fullmatch(r"(.+)-(\d+)\.json", Path(r["ruta"]).name)
        if m and ultimo[m[1]][1] != r["ruta"]:
            r["reemplazado_por"] = ultimo[m[1]][1]
    resultado = raiz / "evidencia" / "resultado.json"
    evidencia = None
    if resultado.is_file():
        datos = cargar(resultado)
        if datos is not None:
            evidencia = {"ruta": resultado.relative_to(cli.ROOT).as_posix(), "resultado": datos}
    return revisores, evidencia, archivos, avisos


def exclusiones_del_paquete(base: str, head: str) -> list[str]:
    """Lo que el paquete de Clue deja fuera: .factory/ y tareas/, más cada otro archivo del diff que no es producto."""
    cambiados = [n for n in cli.ejecutar(["git", "diff", "--name-only", "-z", "--no-renames", base, head]).stdout.split("\0") if n]
    carpetas = ("tareas", estructura.DIR)
    return sorted({*carpetas, *(n for n in cambiados if n and not cli.es_producto(n) and Path(n).parts[0] not in carpetas)})


def producto_excluido(paquete: dict) -> list[str]:
    """Archivos del producto que un paquete de Clue deja afuera: con alguno, el paquete no sirve para revisar."""
    return sorted(str(n) for n in paquete.get("excluded_files") or [] if not isinstance(n, str) or cli.es_producto(n))


def corte_del_candidato(identificador: str, sha: str, estado: dict) -> tuple[list[dict], list[dict]] | None:
    """(medios o más, bajos) sin aceptar en los informes vigentes del candidato; None si no tiene ninguno usable."""
    material = cli.material_del_candidato(identificador, sha)
    for aviso in material[3]:  # por qué un informe del candidato no cuenta (por ejemplo, un paquete que excluye producto)
        print(f"Aviso: {aviso}", file=sys.stderr)
    revisores = [r for r in material[0] if not r.get("reemplazado_por")]
    return preparacion.corte(revisores, estado.get("aceptados") or []) if revisores else None


@contextmanager
def turno_de_pedidos(identificador: str):
    """Turno entre pedidos de revisión del mismo cambio. Espera en vez de fallar, y el sistema lo suelta cuando el proceso
    termina de cualquier forma: un pedido cortado no deja un bloqueo que haya que retirar."""
    ruta = cli.ruta_segura(cli.ROOT / estructura.DIR / "local" / "locks" / f"{identificador}.pedir.lock")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "a") as archivo:
        fcntl.flock(archivo, fcntl.LOCK_EX)
        yield


def pedir_revision(identificador: str, nombre: str, extra: str | None = None, base: str | None = None) -> Path:
    """Pide una revisión del candidato actual al revisor configurado y guarda su informe si Clue lo valida."""
    carpeta, estado = cli.abierto(identificador)
    revisor = cli.config_proyecto()["revisores"].get(nombre)
    if revisor is None:
        raise cli.FactoryError(f"no hay un revisor «{nombre}» en .factory/config.json; por ejemplo: {revisores_mod.EJEMPLO}")
    if cli.cambios_locales_de_producto():
        raise cli.FactoryError("hay cambios del producto sin commit: confirmalos antes de pedir una revisión ("
                           + ", ".join(cli.cambios_locales_de_producto()[:5]) + ")")
    # Un commit que sólo guarda informes o evidencia no cambia el producto: el candidato sigue siendo el vigente.
    head = cli.ejecutar(["git", "rev-parse", cli.candidato_vigente(identificador) or "HEAD"]).stdout.strip()
    sha = head[:7]
    if base == "vacio":
        base = cli.base_vacia()
    elif base is None:
        p = cli.ejecutar(["git", "merge-base", "HEAD", "main"])
        if p.returncode:
            raise cli.FactoryError("no encuentro la rama main para la base del paquete; indicá --base REF")
        base = p.stdout.strip()
    else:  # el clon del revisor no tiene las ramas del repositorio: la base va como SHA
        p = cli.ejecutar(["git", "rev-parse", "--verify", "--quiet", base + "^{commit}"])
        if p.returncode:
            raise cli.FactoryError(f"--base {base} no es un commit de este repositorio")
        base = p.stdout.strip()
    clue_dir = estructura.ruta_canonica(cli.ROOT, identificador, "clue", sha)
    revision_dir = estructura.ruta_canonica(cli.ROOT, identificador, "revision", sha)
    revisiones = estructura.ruta_canonica(cli.ROOT, identificador, "checkout", sha).parent
    for d in (revisiones, clue_dir):  # revision/ se crea sólo con un informe válido
        cli.ruta_segura(d).mkdir(parents=True, exist_ok=True)
    excluir = cli.exclusiones_del_paquete(base, head)
    with cli.turno_de_pedidos(identificador):  # otro pedido simultáneo no crea el mismo checkout ni toma el mismo número
        # El siguiente número de este revisor (exacto: «codex» no cuenta los de «codex-rapido»), mirando sus informes y
        # pedidos (versionados: en un clon nuevo no están los paquetes ni los checkouts, que son locales), sus paquetes y
        # sus clones, que pueden haber quedado de un pedido que falló antes de su paquete.
        nombre_ = re.escape(nombre)
        usados = [int(m[1]) for x in [*revision_dir.glob(f"{nombre}-*"), *clue_dir.glob("paquete-*.json"), *revisiones.glob(f"{sha}-*")]
                  for m in [re.fullmatch(rf"(?:{nombre_}-|paquete-{nombre_}-|{sha}-{nombre_}-)(\d+)(?:\.json|\.pedido\.md)?", x.name)] if m]
        n = max(usados, default=0) + 1
        paquete = clue_dir / f"paquete-{nombre}-{n}.json"
        # Un clon aparte por pedido, no un worktree: un worktree comparte la configuración y las ramas del repositorio, y
        # lo que un revisor hiciera con git ahí le caería encima; y dos revisores no comparten checkout. --local enlaza los
        # objetos en el mismo disco (no copia nada) y el clon no depende de ellos: un gc del repositorio no lo deja sin el
        # candidato. Un checkout viejo (un worktree de antes) ya no se usa.
        checkout = revisiones / f"{sha}-{nombre}-{n}"
        if checkout.exists():
            raise cli.FactoryError(f"el checkout {checkout.relative_to(cli.ROOT)} ya existe; borralo o pedí la revisión otra vez")
        p = cli.ejecutar(["git", "clone", "--quiet", "--local", "--no-checkout", str(cli.ROOT), str(checkout)])
        if not p.returncode:
            p = cli.ejecutar(["git", "-C", str(checkout), "checkout", "--quiet", "--detach", head])
        for remoto in cli.ejecutar(["git", "-C", str(checkout), "remote"]).stdout.split() if not p.returncode else []:
            p = cli.ejecutar(["git", "-C", str(checkout), "remote", "remove", remoto])  # sin remoto: un push no llega al repositorio
        if p.returncode:
            raise cli.FactoryError(f"no pude crear el checkout de revisión: {p.stderr.strip()}")
        p = cli.ejecutar(["oracle-clue", "preparar", "--repo", str(checkout), "--base", base, "--contexto", estado["spec"],
                      *(a for ruta in excluir for a in ("--excluir", ruta)), "--salida", str(paquete)])
    if p.returncode and any(m in (p.stderr or p.stdout) for m in ("vacío fuera de las exclusiones", "el diff está vacío")):
        raise cli.FactoryError(f"el candidato {sha} no cambia el producto respecto de la base: no trae cambios o sólo trae registros, "
                           "y un paquete de registros no se revisa. Para revisar código que ya existe (por ejemplo, al cerrar con "
                           f"evidencia un cambio viejo), pedí la revisión con --base en un commit anterior a ese código, o con --base vacio para revisar todo el producto del candidato")
    if p.returncode:
        raise cli.FactoryError(f"oracle-clue no pudo preparar el paquete: {(p.stderr or p.stdout).strip()[:500]}")
    datos_paquete = json.loads(paquete.read_text(encoding="utf-8"))
    if cli.producto_excluido(datos_paquete):
        raise cli.FactoryError("el paquete de Clue deja afuera archivos del producto: "
                           + ", ".join(map(str, cli.producto_excluido(datos_paquete))) + "; no lancé al revisor")
    trabajo = cli.ROOT / estructura.DIR / "local" / "revisores" / f"{sha}-{nombre}-{n}"
    cli.ruta_segura(trabajo).mkdir(parents=True, exist_ok=True)
    informe, registro, pedido_archivo = trabajo / "informe.json", trabajo / "salida.log", trabajo / "pedido.md"
    anteriores = [r.relative_to(cli.ROOT).as_posix() for c in cli.candidatos_anteriores(identificador, sha)
                  for r in sorted(estructura.ruta_canonica(cli.ROOT, identificador, "revision", c).glob("*.json"))]
    vueltas = ("Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):\n"
               + "\n".join(f"- {r}" for r in anteriores) + "\n") if anteriores else ""
    if estado.get("aceptados"):
        vueltas += ("Riesgos ya aceptados por una persona en este cambio (no los reportes otra vez salvo que el defecto haya "
                    "cambiado o empeorado):\n" + "\n".join(f"- {a['archivo']}: {a['titulo']} (aceptado por {a['actor']}: "
                                                            f"{a['motivo']})" for a in estado["aceptados"]) + "\n")
    if datos_paquete.get("excluded_files"):
        vueltas += (f"Fuera del paquete, porque no son producto ({', '.join(datos_paquete.get('exclusions') or [])}): "
                    f"{len(datos_paquete['excluded_files'])} archivos de registros y evidencia de Factory; no los revises.\n")
    valores = {"id": identificador, "titulo": estado.get("titulo", ""), "propuesta": str(carpeta / "proposal.md"),
               "spec": str(cli.ROOT / estado["spec"]), "candidato": sha, "checkout": str(checkout), "paquete": str(paquete),
               "informe": str(informe), "proveedor": revisor["proveedor"], "modelo": revisor["modelo"], "vueltas": vueltas}
    texto = revisores_mod.pedido(revisores_mod.plantilla(cli.ROOT), valores, extra)
    pedido_archivo.write_text(texto, encoding="utf-8")
    argv = revisores_mod.argumentos(revisor["comando"], {"pedido": texto, "pedido_archivo": pedido_archivo, "carpeta": trabajo,
                                                         "informe": informe, "registro": registro, "paquete": paquete,
                                                         "checkout": checkout})
    print(f"Revisor {nombre} ({revisor['proveedor']}, {revisor['modelo']}) sobre el candidato {sha}; tope {revisor['tope_minutos']} min.")
    print("Comando: " + " ".join(a if len(a) < 80 else a[:77] + "..." for a in argv))
    with cli.turno_de_pedidos(identificador):  # el lanzamiento queda antes: un pedido cortado a mitad no desaparece
        _, estado = cli.leer(identificador)
        lanzamiento = os.urandom(6).hex()  # el resultado dice qué lanzamiento cierra
        cli.evento(estado, "revision_lanzada", forma="registro", revisor=nombre, candidato=sha, lanzamiento=lanzamiento)
        cli.guardar(carpeta, estado)
    hallazgos, motivo, severidades = 0, None, ""
    try:  # Ctrl-C en el revisor o en la validación: queda «interrumpido», no un lanzamiento sin resultado
        resultado = revisores_mod.ejecutar_revisor(argv, trabajo, registro, revisor["tope_minutos"])
        if resultado == "tope":
            motivo = f"el revisor no terminó dentro del tope de {revisor['tope_minutos']} minutos"
        elif resultado == "no_inicia":
            motivo = f"no se pudo iniciar el revisor ({argv[0]})"
        elif not informe.is_file():
            resultado, motivo = "sin_informe", f"el revisor no dejó el informe en {informe}"
        else:
            # Si el revisor movió el HEAD de su checkout (una rama, un commit), se valida contra el candidato.
            cli.ejecutar(["git", "-C", str(checkout), "checkout", "--quiet", "--force", "--detach", head])
            p = cli.ejecutar(["oracle-clue", "validar", str(informe), "--paquete", str(paquete), "--repo", str(checkout)])
            if p.returncode:
                resultado, motivo = "rechazado", f"Clue rechazó el informe: {(p.stderr or p.stdout).strip()[:500]}"
            else:
                datos = json.loads(informe.read_text(encoding="utf-8"))
                hallazgos = len(datos.get("findings") or [])
                severidades = preparacion.contar_severidades(datos.get("findings") or [])
    except KeyboardInterrupt:
        with cli.turno_de_pedidos(identificador):
            _, estado = cli.leer(identificador)
            cli.evento(estado, "revision_pedida", forma="registro", revisor=nombre, proveedor=revisor["proveedor"],
                   modelo=revisor["modelo"], candidato=sha, resultado="interrumpido", hallazgos=0, lanzamiento=lanzamiento)
            cli.guardar(carpeta, estado)
        raise
    with cli.turno_de_pedidos(identificador):  # leer y guardar en el mismo turno: el evento de otro pedido no se pierde
        _, estado = cli.leer(identificador)
        cli.evento(estado, "revision_pedida", forma="registro", revisor=nombre, proveedor=revisor["proveedor"],
               modelo=revisor["modelo"], candidato=sha, resultado=resultado, hallazgos=hallazgos, lanzamiento=lanzamiento)
        cli.guardar(carpeta, estado)
    if motivo:
        raise cli.FactoryError(f"{motivo}. La salida del revisor quedó en {registro.relative_to(cli.ROOT)}; revision/ no cambió.")
    cli.ruta_segura(revision_dir).mkdir(parents=True, exist_ok=True)
    destino = revision_dir / f"{nombre}-{n}.json"
    cli.escribir_atomico(destino, informe.read_bytes())
    cli.escribir_atomico(revision_dir / f"{nombre}-{n}.pedido.md", pedido_archivo.read_bytes())
    print(f"Informe de {nombre}: {destino.relative_to(cli.ROOT)} ({hallazgos} hallazgo{'s' if hallazgos != 1 else ''}"
          f"{': ' + severidades if severidades else ''}), validado con oracle-clue.")
    corte = cli.corte_del_candidato(identificador, sha, cli.leer(identificador)[1])
    if corte is None:
        print(f"No pude usar los informes del candidato {sha} para decidir si hace falta otra vuelta; "
              f"mirá los avisos con oracle-factory revision-preparar {identificador}")
        return destino
    graves, bajos = corte
    if graves:
        print(f"Quedan {len(graves)} hallazgo{'s' if len(graves) != 1 else ''} medio{'s' if len(graves) != 1 else ''} o más "
              f"sin aceptar en el candidato {sha} ({', '.join(str(h.get('id')) for h in graves)}).")
        print(f"Próximo paso: corregirlos, commitear y pedir otra vuelta con oracle-factory pedir-revision {identificador}")
        print(f"También: aceptarlos como riesgo o descartarlos, con motivo, en oracle-factory revisar {identificador}")
    else:
        print(f"No quedan hallazgos medios ni altos sin aceptar en el candidato {sha}: no hace falta otra vuelta.")
        print(f"Próximo paso: oracle-factory revisar {identificador}"
              + (f" — los {len(bajos)} bajos los decide una persona (aceptar, descartar o dejar abierto)" if bajos else ""))
    return destino


def revisar_guiado(identificador: str, informe: Path, decisiones: Path, revisor: str, decision: str,
                   confirmado: tuple[str, str] | None = None) -> None:
    carpeta, estado = cli.abierto(identificador)
    registro_ruta = cli.ruta_segura(cli.ruta_registro(carpeta))
    registro = registro_ruta.read_bytes()
    if json.loads(registro) != estado:
        raise cli.FactoryError('registro cambió durante la lectura; volvé a revisar')
    cli.exigir_spec(carpeta, estado)
    contenido, resoluciones = cli.leer_regular(informe, 'informe'), cli.leer_regular(decisiones, 'decisiones')
    contexto, docs = cli.contexto_producto(), cli.documentos(carpeta, estado)
    try:
        analisis, triage, pendientes_ids = documentos_revision.validar(
            contenido, resoluciones, identificador=identificador, contexto=contexto, documentos=docs, revisor=revisor)
    except documentos_revision.RevisionInvalida as e:
        raise cli.FactoryError(str(e)) from e
    abiertos = len(pendientes_ids)
    print('Formato: guiado; consistencia estructural, sin verificar calidad del análisis ni identidad de actores.')
    print(f"Revisor: {revisor}; decisión solicitada: {decision}; commit: {contexto['head']}; huella: {contexto['archivos_sha256']}")
    print(f"Revisión declarada completa: {analisis['completa']}; archivos: {', '.join(analisis['archivos_revisados'])}")
    print('Límites: ' + ('; '.join(analisis['limites']) or 'sin límites adicionales declarados; no implica cobertura universal'))
    for comprobacion in analisis['comprobaciones']:
        print(f"Comprobación {comprobacion['resultado']}: {comprobacion['descripcion']} · {comprobacion['evidencia']}")
    for hallazgo in analisis['hallazgos']:
        print(f"Hallazgo {hallazgo['id']}: {hallazgo['descripcion']} · {hallazgo['ubicacion']} · {hallazgo['evidencia']}")
    if not analisis['hallazgos']:
        print('Ausencia de hallazgos declarada: ' + analisis['sin_hallazgos_motivo'])
    for resolucion in triage['decisiones']:
        print(f"Resolución {resolucion['hallazgo_id']}: {resolucion['estado']} · {resolucion['actor']} · {resolucion['fecha']} · {resolucion['motivo']}")
    print(f"Actor de decisión: {triage['actor']}; motivo: {triage['motivo']}")
    print(f"Abiertos derivados: {abiertos}; IDs: {', '.join(pendientes_ids) or 'ninguno'}")
    if decision == 'aprobar':
        causas = ([f"comprobación en {c['resultado']}: {c['descripcion']}" for c in analisis['comprobaciones'] if c['resultado'] != 'cumple']
                  + [f"hallazgo abierto: {h}" for h in pendientes_ids] + ([] if analisis['completa'] else ['la revisión está declarada incompleta']))
        if causas:
            raise cli.FactoryError('no se puede aprobar:\n  - ' + '\n  - '.join(causas)
                               + '\nRegistrá la decisión «cambios» o, si corresponde, resolvé lo que falta y prepará la revisión de nuevo.')

    def revalidar():
        cli.exigir_spec(carpeta, estado)
        if (cli.leer_regular(informe, 'informe') != contenido or cli.leer_regular(decisiones, 'decisiones') != resoluciones):
            raise cli.FactoryError('informe o decisiones cambiaron durante la operación; volvé a revisarlos')
        if (not cli.mismo_producto(contexto, cli.contexto_producto()) or cli.documentos(carpeta, estado) != docs
                or registro_ruta.read_bytes() != registro):
            raise cli.FactoryError('producto, spec o registro cambió durante la operación; volvé a revisar')

    firma = cli.firma_revision('guiado', cli.sha256(contenido), cli.sha256(resoluciones), revisor, decision, contexto)

    def publicar_propuesta(e):
        revalidar()
        cli.escribir_atomico(registro_ruta, cli.bytes_json(e), esperado=registro)

    forma = cli.decidir(estado, 'revision', cli.tipos_cambio(estado), firma, cli.menu_revision(identificador, decision),
                    'registro de revisión cancelado', publicar_propuesta, confirmado)
    if forma is None:
        return
    revalidar()
    destino, destino_decisiones = cli.guardar_par_revision(identificador, 'registro', contenido, resoluciones)
    preparado = analisis['contexto'].get('head')  # lo declara el informe: sólo se guarda si es un commit
    preparado = preparado if isinstance(preparado, str) and re.fullmatch(r'[0-9a-f]{40}', preparado) else None
    try:
        revalidar()
        if cli.leer_regular(destino, 'informe archivado') != contenido or cli.leer_regular(destino_decisiones, 'decisiones archivadas') != resoluciones:
            raise cli.FactoryError('las copias archivadas cambiaron antes de registrar')
        estado['revision'] = {
            'formato': 'guiado', 'revisor': revisor, 'decision': decision, 'hallazgos_abiertos': abiertos,
            'informe': str(destino.relative_to(cli.ROOT)), 'sha256': cli.sha256(contenido),
            'decisiones': str(destino_decisiones.relative_to(cli.ROOT)), 'decisiones_sha256': cli.sha256(resoluciones),
            **cli.registro_decision(estado, forma), 'contexto': contexto,
            **({'head_preparacion': preparado} if preparado and preparado != contexto['head'] else {}),
        }
        estado.update(oracle=None, fase='revision_aprobada' if decision == 'aprobar' else 'cambios_pedidos')
        cli.evento(estado, 'revision_registrada', forma=forma, formato='guiado', revisor=revisor, decision=decision,
               abiertos=abiertos, sha256=cli.sha256(contenido), decisiones_sha256=cli.sha256(resoluciones))
        cli.escribir_atomico(registro_ruta, cli.bytes_json(estado), esperado=registro)
    except (cli.FactoryError, OSError) as e:
        raise cli.FactoryError(f'no se publicó la nueva revisión: {e}. Copias residuales en {destino.parent}; '
                           'se conservó el registro anterior o la edición concurrente.') from e
    try:
        cli.nota_tarea(identificador, f'Revisión guiada {revisor}: {decision}; registrada por {cli.quien(estado["revision"])}; {abiertos} abiertos derivados; '
                   f"commit {contexto['head']}; informe {destino.relative_to(cli.ROOT)}; decisiones {destino_decisiones.relative_to(cli.ROOT)}.")
    except (cli.FactoryError, OSError) as e:
        raise cli.FactoryError(f'La revisión quedó registrada en {registro_ruta}; nota del tracker pendiente: {e}. '
                           'Consultá estado y recuperá sólo la nota; no se revirtió el registro.') from e
    print(f'Informe registrado: {destino}\nDecisiones registradas: {destino_decisiones}')
    cli.siguiente(identificador, estado['fase'])


def motivo_armado(informe: dict, sha: str, decision: str, resoluciones: list[dict]) -> str:
    hallazgos = informe.get("hallazgos") or []
    partes = [f"{'Apruebo' if decision == 'aprobar' else 'Pido cambios en'} el candidato {sha}"]
    partes.append(f"{len(hallazgos)} hallazgo{'s' if len(hallazgos) != 1 else ''} de los revisores"
                  + (": " + ", ".join(f"{r['hallazgo_id']} {r['estado'].replace('_', ' ')}" for r in resoluciones)
                     if resoluciones else ""))
    evidencia = next((c["descripcion"] for c in informe.get("comprobaciones") or []
                      if c["descripcion"].startswith("Evidencia del candidato")), None)
    if evidencia:
        partes.append(evidencia[0].lower() + evidencia[1:])
    vueltas = sum(c["descripcion"].startswith("Vuelta anterior") for c in informe.get("comprobaciones") or [])
    if vueltas:
        partes.append(f"{vueltas} vuelta{'s' if vueltas != 1 else ''} anterior{'es' if vueltas != 1 else ''} registrada{'s' if vueltas != 1 else ''}")
    return "; ".join(partes) + "."


def proponer_revision(identificador: str, decision: str, motivo: str) -> None:
    """El agente deja la decisión y el motivo que propone; la persona los ve como opción en revisar."""
    carpeta, estado = cli.abierto(identificador)
    sha = cli.candidato_vigente(identificador)
    if sha is None:
        raise cli.FactoryError("no hay candidato vigente para proponer una revisión")
    # Fuera de «propuestas»: ésas son las decisiones canónicas de modos.DECISIONES, con firma.
    estado.setdefault("motivos_propuestos", {})["revision"] = {"decision": decision, "motivo": motivo, "candidato": sha,
                                                      **cli.actor(), "cuando": cli.ahora()}
    cli.evento(estado, "revision_propuesta", forma="propuso", decision=decision, candidato=sha)
    cli.guardar(carpeta, estado)
    print(f"Propuesta de {cli.AGENTE} para el candidato {sha}: {decision}; motivo «{motivo}». "
          f"La persona la ve como opción con oracle-factory revisar {identificador}.")


def revisar_paso_a_paso(identificador: str) -> None:
    """La revisión del candidato vigente, guiada: prepara, muestra, pregunta y registra sin editar JSON.

    Un corte después de mostrar la revisión queda en el registro (revision_cancelada) y estado lo avisa.
    """
    intento: dict = {}
    try:
        cli._revisar_paso_a_paso(identificador, intento)
    except (cli.FactoryError, EOFError, KeyboardInterrupt) as e:
        if intento:
            causa = {EOFError: "se cerró la entrada antes de registrar la revisión",
                     KeyboardInterrupt: "se interrumpió antes de registrar la revisión"}.get(type(e), str(e))
            try:  # el error que se ve sigue siendo el de la revisión; el de anotarlo se dice aparte
                cli.anotar_intento(identificador, intento, causa)
            except (cli.FactoryError, OSError, ValueError) as error:
                print(f"Aviso: no pude anotar el intento de revisión en el registro ({error}).", file=sys.stderr)
        raise


def anotar_intento(identificador: str, intento: dict, causa: str) -> None:
    """revision_cancelada, salvo que la revisión se haya registrado igual (un fallo posterior, como la nota del tracker)."""
    carpeta, _ = cli.leer(identificador)
    destino = cli.ruta_registro(carpeta)
    leido = destino.read_bytes()
    estado = json.loads(leido)
    if any(e.get("accion") == "revision_registrada" for e in (estado.get("eventos") or [])[intento["eventos"]:]):
        return
    cli.evento(estado, "revision_cancelada", forma="intento", causa=causa, candidato=intento["candidato"])
    cli.guardar(carpeta, estado, esperado=leido)  # si otro lo escribió entretanto, no se pisa


def lanzamientos_abiertos(estado: dict) -> list[dict]:
    """Los revisores lanzados que todavía no dejaron resultado, con las mismas reglas que aviso_lanzamientos. Un pedido
    «interrumpido» (Ctrl-C) ya terminó: no sigue en curso ni se avisa como cortado."""
    abiertos: list[dict] = []
    for e in estado.get("eventos") or []:
        r, c = e.get("revisor"), e.get("candidato")
        if e.get("accion") == "revision_lanzada":
            abiertos.append(e)
        elif e.get("accion") == "revision_pedida":
            propio = [a for a in abiertos if a.get("lanzamiento") and a.get("lanzamiento") == e.get("lanzamiento")]
            abiertos = [a for a in abiertos if a not in propio] if propio else \
                [a for a in abiertos if (a.get("revisor"), a.get("candidato")) != (r, c)]
    return abiertos


def aviso_lanzamientos(estado: dict) -> list[str]:
    """Revisores lanzados que no dejaron resultado (el pedido se cortó a mitad): uno por lanzamiento, mientras el
    cambio siga abierto.

    Un resultado cierra sólo su lanzamiento (o, en registros sin lanzamiento con nombre, todos los de su revisor y
    candidato). Un lanzamiento sin resultado sigue a la vista; si después el mismo revisor terminó sobre ese candidato
    o se lanzó sobre otro, el aviso lo dice y no pide repetirlo (eso revisaría el candidato nuevo, no ése)."""
    if estado.get("fase") in ("cerrada", "abandonada"):
        return []
    ultimo: dict = {}  # el último candidato sobre el que se lanzó cada revisor
    terminados: set = set()  # (revisor, candidato) con un resultado
    for e in estado.get("eventos") or []:
        if e.get("accion") == "revision_lanzada":
            ultimo[e.get("revisor")] = e.get("candidato")
        elif e.get("accion") == "revision_pedida" and e.get("resultado") != "interrumpido":
            terminados.add((e.get("revisor"), e.get("candidato")))
    avisos = []
    for e in cli.lanzamientos_abiertos(estado):
        r, c = e.get("revisor"), e.get("candidato")
        texto = f"el revisor {r} se lanzó ({str(e.get('cuando', ''))[:16].replace('T', ' ')}) sobre el candidato {c} y no dejó resultado"
        if ultimo.get(r) != c:
            texto += f"; después se lanzó sobre el candidato {ultimo.get(r)}, así que no hace falta repetirlo"
        elif (r, c) in terminados:
            texto += "; otro pedido del mismo revisor sobre ese candidato sí terminó, así que no hace falta repetirlo"
        else:
            texto += f"; volvé a pedirlo con oracle-factory pedir-revision {estado['id']} --a {r}"
        avisos.append(texto)
    return avisos


def sin_medir_con_medidas(estado: dict) -> list[str]:
    """Requisitos con medidas decididas cuyo .requisito todavía tiene sin_medir: juzgar no pasaría la cobertura."""
    salida = []
    for rid in estado.get("requisitos") or []:
        ruta = cli.requisitos_dir() / f"{rid}.requisito"
        if (estado.get("medidas") or {}).get(rid) and ruta.is_file() and re.search(r"(?m)^\s+sin_medir ", ruta.read_text(encoding="utf-8")):
            salida.append(rid)
    return salida


def aviso_sin_medir(identificador: str, estado: dict) -> list[str]:
    return [f"{rid} tiene sus medidas decididas pero todavía dice «sin medir», y juzgar no va a pasar la cobertura: "
            f"decidí las mismas medidas otra vez quitando la marca: oracle-factory medir {identificador} --requisito {rid} "
            f"--medida … --quitar-sin-medir (si lo propone un agente, con --agente NOMBRE, una persona lo confirma con "
            f"oracle-factory medir {identificador} --confirmar)" for rid in cli.sin_medir_con_medidas(estado)]


def aviso_sin_autor(estado: dict) -> list[str]:
    """Acciones que quedaron sin autor: corridas sin --agente y sin una terminal de una persona."""
    sin = [e.get("accion") for e in estado.get("eventos") or [] if e.get("tipo_actor") == "sin_identificar"]
    if not sin:
        return []
    cuales = ", ".join(dict.fromkeys(sin))
    return [f"{len(sin)} {'acción quedó' if len(sin) == 1 else 'acciones quedaron'} sin autor ({cuales}): un agente las "
            "hace con --agente NOMBRE, y una persona desde su terminal"]


def aviso_revision(estado: dict) -> list[str]:
    """Si el último intento de revisión se cortó sin registrarse, el aviso con su causa y qué hacer."""
    ultimo = next((e for e in reversed(estado.get("eventos") or [])
                   if e.get("accion") in ("revision_registrada", "revision_cancelada")), None)
    if not ultimo or ultimo["accion"] != "revision_cancelada":
        return []
    try:  # «sigue valiendo» con las mismas reglas de vigencia que estado y el próximo paso
        rev = estado.get("revision") or {}
        vigente = bool(rev) and cli.mismo_producto(rev.get("contexto"), cli.contexto_producto()) and not cli.problemas_de_revision(estado)
    except (cli.FactoryError, OSError):
        vigente = False
    que = "sigue valiendo la revisión anterior" if vigente else f"volvé a correr oracle-factory revisar {estado['id']}"
    return [f"el último intento de revisión ({str(ultimo.get('cuando', ''))[:16].replace('T', ' ')}, {ultimo.get('actor')}) "
            f"no se registró: {ultimo.get('causa')}; {que}"]


def _revisar_paso_a_paso(identificador: str, intento: dict) -> None:
    cli.abierto(identificador)
    cli.exigir_terminal("registrar la revisión")
    sha = cli.candidato_vigente(identificador)
    if sha is None:
        raise cli.FactoryError("no hay candidato vigente: hace falta un commit con su carpeta de candidato (evidencia o informes "
                           f"de revisores) y sin cambios de producto después. Para seguir: {cli.pedido_de_revision(identificador)}")
    with contextlib.redirect_stdout(io.StringIO()):
        ruta_informe, ruta_decisiones = cli.preparar_revision(identificador)
    informe = json.loads(ruta_informe.read_text(encoding="utf-8"))
    decisiones = json.loads(ruta_decisiones.read_text(encoding="utf-8"))
    if not informe.get("archivos_revisados") or not informe.get("comprobaciones"):
        if informe.get("comprobaciones"):  # la evidencia está; lo que falta es el paquete de un revisor, que trae los archivos
            falta = "tiene evidencia, pero ningún informe de un revisor independiente (revisar necesita los archivos que él revisó)"
        else:
            falta = "no tiene informes de revisores ni evidencia"
        raise cli.FactoryError(f"el candidato {sha} {falta}. Para seguir: {cli.pedido_de_revision(identificador)}")
    print(f"Revisión de {identificador} · candidato {sha}")
    for c in informe["comprobaciones"]:
        print(f"  {'✓' if c['resultado'] == 'cumple' else '✗'} {c['descripcion']}\n      Evidencia: {c['evidencia']}")
    for limite in informe.get("limites") or []:
        print(f"  Límite: {limite}")
    # Desde acá, un corte es un intento que no se registró; los eventos de antes no cuentan para saber si se registró.
    intento.update(candidato=sha, eventos=len(cli.leer(identificador)[1].get("eventos") or []))
    persona = cli.actor()["actor"]
    resoluciones = []
    aceptados = {a["firma"]: a for a in cli.leer(identificador)[1].get("aceptados") or [] if a.get("firma")}
    nuevos, revocados = [], []  # se guardan sólo si la revisión se registra
    decididos: dict[str, dict | None] = {}  # firma → resolución (None: quedó abierto) de su primera aparición
    for h in informe.get("hallazgos") or []:
        print(f"\nHallazgo {h['id']} en {h['ubicacion']}:\n  {h['descripcion']}\n  Evidencia: {h['evidencia']}")
        firma = preparacion.firma_de_ubicacion(h["ubicacion"], h["descripcion"])
        if firma in decididos:  # otro revisor reportó lo mismo: una sola decisión por hallazgo, sin contradicciones
            igual = decididos[firma]
            print(f"  Es el mismo hallazgo que {igual['hallazgo_id'] if igual else 'uno anterior'}: "
                  f"{'misma decisión (' + igual['estado'] + ')' if igual else 'queda abierto también'}.")
            if igual:
                resoluciones.append({**igual, "hallazgo_id": h["id"]})
            continue
        previo = aceptados.get(firma) if firma else None
        if previo:
            print(f"  YA ACEPTADO por {previo['actor']} el {previo['fecha'][:10]} (candidato {previo['candidato']}), "
                  f"como «{previo['titulo']}»: «{previo['motivo']}»")
            j = cli.elegir(f"¿Mantenés aceptado {h['id']}?", [
                ("Mantener aceptado", "se registra como riesgo aceptado con el mismo motivo"),
                ("Revocar", "deja de estar aceptado y lo decidís como un hallazgo nuevo")])
            if j is None:
                raise cli.FactoryError("revisión cancelada; no registré nada")
            if j == 0:
                resoluciones.append({"hallazgo_id": h["id"], "estado": "riesgo_aceptado", "motivo": previo["motivo"],
                                     "origen_motivo": "persona", "actor": persona, "fecha": cli.ahora()})
                decididos[firma] = resoluciones[-1]
                continue
            revocados.append(firma)
        i = cli.elegir(f"¿Qué hacés con {h['id']}?", [("Aceptar el riesgo", "queda registrado como riesgo aceptado"),
                                                  ("Descartar", "no aplica o no es un defecto"),
                                                  ("Dejar abierto", "sólo se podrá pedir cambios")])
        if i is None:
            raise cli.FactoryError("revisión cancelada; no registré nada")
        if i == 2:
            if firma:
                decididos[firma] = None
            continue
        estado_h = ("riesgo_aceptado", "descartado")[i]
        motivo_h, origen_h = cli.elegir_motivo(f"{'Acepto el riesgo' if i == 0 else 'Descarto el hallazgo'}: {h['descripcion']}")
        resoluciones.append({"hallazgo_id": h["id"], "estado": estado_h, "motivo": motivo_h, "origen_motivo": origen_h,
                             "actor": persona, "fecha": cli.ahora()})
        if firma:
            decididos[firma] = resoluciones[-1]
        if estado_h == "riesgo_aceptado":  # sin firma (título de puros signos) se guarda igual, pero no coincide con nada
            nuevos.append({"archivo": preparacion.archivo_de_ubicacion(h["ubicacion"]), "titulo": h["descripcion"],
                           "firma": firma, "motivo": motivo_h, "actor": persona, "fecha": cli.ahora(), "candidato": sha})
    abiertos = len(informe.get("hallazgos") or []) - len(resoluciones)
    # «Completa» lo declara la persona: Factory no lo supone.
    alcance = cli.elegir("¿Revisaste todo lo que abarca el informe?", [
        ("Sí, la revisión está completa", "se registra como completa"),
        ("No, quedó incompleta", "se registra incompleta, con sus límites; sólo se podrá pedir cambios")])
    if alcance is None:
        raise cli.FactoryError("revisión cancelada; no registré nada")
    completa = alcance == 0
    if not completa and not informe.get("limites"):
        limite = input("¿Qué quedó sin revisar? ").strip()
        if not limite:
            raise cli.FactoryError("una revisión incompleta necesita su límite; no registré nada")
        informe["limites"] = [limite]
    # Los números no se corren: «Aprobar» es siempre la 1, y cuando no se puede dice por qué.
    causas = ([f"{abiertos} hallazgo(s) abiertos"] if abiertos else []) + ([] if completa else ["la revisión está incompleta"]) + [
        f"{c['descripcion']} ({c['resultado']})" for c in informe["comprobaciones"] if c["resultado"] != "cumple"]
    aprobar = ("NO DISPONIBLE: " + "; ".join(causas)) if causas else "la revisión queda aprobada; después corre juzgar y se puede cerrar"
    i = cli.elegir(f"Decisión sobre el candidato {sha}:", [("Aprobar", aprobar),
                                                         ("Pedir cambios", "la revisión queda registrada pidiendo cambios"),
                                                         ("Cancelar", "no registra nada")])
    if i is None or i == 2:
        raise cli.FactoryError("revisión cancelada; no registré nada")
    if i == 0 and causas:
        raise cli.FactoryError("no se puede aprobar: " + "; ".join(causas) + ". No registré nada.")
    decision = ("aprobar", "cambios")[i]
    _, estado = cli.leer(identificador)
    propuesta = (estado.get("motivos_propuestos") or {}).get("revision") or {}
    propuesto = propuesta.get("motivo") if propuesta.get("decision") == decision and propuesta.get("candidato") == sha else None
    motivo = cli.elegir_motivo(cli.motivo_armado(informe, sha, decision, resoluciones), propuesto)
    informe.update(revisor=persona, completa=completa)
    contenido = cli.bytes_json(informe)
    cli.escribir_atomico(ruta_informe, contenido)
    decisiones.update(informe_sha256=cli.sha256(contenido), actor=persona, motivo=motivo[0], decisiones=resoluciones)
    cli.escribir_atomico(ruta_decisiones, cli.bytes_json(decisiones))
    cli.revisar_guiado(identificador, ruta_informe, ruta_decisiones, persona, decision, motivo)
    carpeta, estado = cli.leer(identificador)
    cambio = (estado.get("motivos_propuestos") or {}).pop("revision", None) is not None  # la propuesta ya se decidió
    if nuevos or revocados:  # valen para las vueltas siguientes, aunque esta revisión pida cambios
        quitar = set(revocados) | {n["firma"] for n in nuevos if n["firma"]}
        estado["aceptados"] = [a for a in estado.get("aceptados") or [] if not a.get("firma") or a["firma"] not in quitar] + nuevos
        cambio = True
    if cambio:
        cli.guardar(carpeta, estado)


def revisar(identificador: str, informe: Path, revisor: str, decision: str, abiertos: int | None = None,
            *, formato: str = 'libre', decisiones: Path | None = None) -> None:
    if decision not in {'aprobar', 'cambios'} or not revisor.strip():
        raise cli.FactoryError('indicá revisor y una decisión válida')
    if formato == 'guiado':
        if abiertos is not None or decisiones is None:
            raise cli.FactoryError('modo guiado requiere --decisiones y calcula abiertos; no admite --hallazgos-abiertos')
        return cli.revisar_guiado(identificador, informe, decisiones, revisor, decision)
    if formato != 'libre' or decisiones is not None:
        raise cli.FactoryError('usá --formato guiado con decisiones, o libre sin decisiones; no hay conversión automática')
    if type(abiertos) is not int or abiertos < 0:
        raise cli.FactoryError('modo libre requiere --hallazgos-abiertos N explícito, entero no negativo')
    carpeta, estado = cli.abierto(identificador)
    registro = (cli.ruta_registro(carpeta)).read_bytes()
    if json.loads(registro) != estado:
        raise cli.FactoryError('registro cambió durante la lectura; volvé a revisar')
    cli.exigir_spec(carpeta, estado)
    if not informe.is_file():
        raise cli.FactoryError(f"no encuentro el informe: {informe}")
    if decision not in {"aprobar", "cambios"} or not revisor.strip():
        raise cli.FactoryError("indicá revisor y una decisión válida")
    if abiertos < 0 or (decision == "aprobar" and abiertos):
        raise cli.FactoryError("una revisión aprobada exige cero hallazgos abiertos")
    contenido = informe.read_bytes()
    if not contenido.strip():
        raise cli.FactoryError("el informe de revisión está vacío")
    contexto = cli.contexto_producto()
    huella = cli.sha256(contenido)
    destino = cli.dir_estado(carpeta) / 'review.md'
    print('Formato: libre; declaración humana sin validación estructural del contenido, alcance ni límites.')
    print(f"Revisor: {revisor}; decisión: {decision}; abiertos: {abiertos}; commit: {contexto['head']}")
    firma = {**cli.firma_revision("libre", huella, None, revisor, decision, contexto), "abiertos": abiertos}

    def publicar_propuesta(e):
        if (cli.ruta_registro(carpeta)).read_bytes() != registro:
            raise cli.FactoryError("registro cambió durante la operación; repetí la revisión")
        cli.guardar(carpeta, e)

    forma = cli.decidir(estado, "revision", cli.tipos_cambio(estado), firma, cli.menu_revision(identificador, decision),
                    "registro de revisión cancelado", publicar_propuesta)
    if forma is None:
        return
    cli.exigir_spec(carpeta, estado)
    if not cli.mismo_producto(contexto, cli.contexto_producto()):
        raise cli.FactoryError("el producto cambió durante la confirmación; repetí la revisión")
    if cli.leer_regular(informe, 'informe') != contenido or (cli.ruta_registro(carpeta)).read_bytes() != registro:
        raise cli.FactoryError('informe o registro cambió durante la confirmación; repetí la revisión')
    destino.write_bytes(contenido)
    estado["revision"] = {
        "formato": "libre",
        "revisor": revisor, "decision": decision, "hallazgos_abiertos": abiertos,
        "informe": str(destino.relative_to(cli.ROOT)), "sha256": huella,
        **cli.registro_decision(estado, forma), "contexto": contexto,
    }
    estado["oracle"] = None
    estado["fase"] = "revision_aprobada" if decision == "aprobar" else "cambios_pedidos"
    cli.evento(estado, "revision_registrada", forma=forma, revisor=revisor, decision=decision, abiertos=abiertos, sha256=huella)
    cli.guardar(carpeta, estado)
    cli.nota_tarea(identificador, f"Revisión {revisor}: {decision}; registrada por {cli.quien(estado['revision'])}; {abiertos} abiertos; commit {contexto['head']}; informe {destino.relative_to(cli.ROOT)}.")
    print(f"Informe registrado: {destino}")
    cli.siguiente(identificador, estado["fase"])
