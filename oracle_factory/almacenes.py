"""Los almacenes de registros conectados (etapa 2 de 6): en la configuración personal del usuario, nunca en el repo del producto.

`$XDG_CONFIG_HOME/oracle-factory/almacenes.json` (o `~/.config/...`): {directorio común de Git del producto: ruta del almacén}.
No importa cli.py: los errores salen como ValueError y quien llama los muestra."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

from . import agentes
from . import estructura

try:
    import fcntl
except ImportError:  # sin fcntl (Windows) no hay bloqueo: dos conectar a la vez podrían pisarse
    fcntl = None


def archivo() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "oracle-factory" / "almacenes.json"


def leer() -> dict[str, str]:
    """{} si no hay archivo; ValueError si existe y no es un objeto de textos."""
    ruta = archivo()
    if not ruta.exists():
        return {}
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"no se puede leer {ruta} ({e}); arreglalo o borralo, Factory no lo sobrescribe") from e
    if not isinstance(datos, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in datos.items()):
        raise ValueError(f"{ruta} no es un objeto {{producto: almacén}}; arreglalo o borralo, Factory no lo sobrescribe")
    return datos


def guardar(datos: dict[str, str]) -> None:
    ruta = archivo()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    descriptor, nombre = tempfile.mkstemp(dir=ruta.parent, prefix=ruta.name + ".", suffix=".tmp")  # un temporal propio de cada proceso
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporal:
            temporal.write(json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        os.replace(nombre, ruta)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(nombre)
        raise


@contextlib.contextmanager
def actualizando():
    """Lee la configuración, deja modificarla y la guarda, todo bajo un bloqueo: dos conectar a la vez no se pierden entradas.

    ValueError si no se puede leer (y no guarda nada)."""
    ruta = archivo()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta.with_name(ruta.name + ".lock"), "a", encoding="utf-8") as candado:
        if fcntl:
            fcntl.flock(candado, fcntl.LOCK_EX)
        datos = leer()
        yield datos
        guardar(datos)


def _git(desde: Path, *args: str) -> str | None:
    try:
        p = subprocess.run(["git", *args], cwd=desde, capture_output=True, text=True)
    except OSError:
        return None
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None


def clave(desde: Path) -> str | None:
    """El directorio común de Git de `desde` (el mismo para todos los worktrees del repo); None si no es un repo."""
    comun = _git(desde, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return str(Path(comun).resolve()) if comun else None


def raiz_git(desde: Path) -> Path | None:
    arriba = _git(desde, "rev-parse", "--show-toplevel")
    return Path(arriba).resolve() if arriba else None


def conectado(cli) -> Path | None:
    """El almacén al que está conectado el producto de `cli.ROOT` (sin --registros), o None. Una configuración ilegible se avisa y vale «no conectado»."""
    if not archivo().exists():
        return None
    try:
        datos = leer()
    except ValueError as e:
        print(f"Aviso: {e}; se trabaja como si el producto no estuviera conectado.", file=sys.stderr)
        return None
    almacen = datos.get(clave(cli.ROOT) or "")
    if almacen is None:
        return None
    if ((raiz_git(cli.ROOT) or cli.ROOT) / cli.estructura.DIR).is_dir():
        raise cli.FactoryError(f"el producto ({cli.ROOT}) tiene su propia carpeta {cli.estructura.DIR}/ y además está conectado al almacén {almacen}: "
                               "no se adivina dónde escribir. Quitá la conexión (oracle-factory desconectar) y, si querés los registros en el "
                               "almacén, pasalos con oracle-factory migrar --almacen ALMACÉN. No se escribió nada.")
    return Path(almacen)


def registros_de(producto: Path) -> Path:
    """Dónde están los registros de `producto` (o de una carpeta suya): su almacén si está conectado; si no, el producto mismo.
    Para las herramientas y las pruebas que leen los registros sin pasar por la CLI."""
    try:
        almacen = leer().get(clave(producto) or "")
    except ValueError:
        almacen = None
    return Path(almacen) if almacen else producto


def es_url(texto: str) -> bool:
    """¿Una URL de Git (esquema://… o usuario@host:ruta) y no una carpeta que existe?"""
    return not Path(texto).expanduser().exists() and bool(re.match(r"[a-zA-Z][\w+.-]*://|[^/:\s]+@[^/:\s]+:", texto))


def carpeta_de_clones() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "oracle-factory" / "almacenes"


def _clon_de(cli, url: str) -> tuple[Path, bool]:
    """(carpeta del clon de `url`, si ya existe): se niega si el nombre no sirve o si la carpeta es otra cosa. No escribe."""
    nombre = url.rstrip("/").rsplit("/", 1)[-1].rsplit(":", 1)[-1].removesuffix(".git")
    if not nombre or nombre in (".", ".."):
        raise cli.FactoryError(f"no sé qué nombre darle al clon de {url}. No cambié nada")
    destino = carpeta_de_clones() / nombre
    if not (destino.exists() or destino.is_symlink()):
        return destino, False
    origen = _git_almacen(destino, "remote", "get-url", "origin") if destino.is_dir() else None
    if raiz_git(destino) == destino.resolve() and origen is not None and origen.returncode == 0 \
            and os.fsdecode(origen.stdout).strip() == url:
        return destino, True
    raise cli.FactoryError(f"{destino} ya existe y no es un clon de {url}: no lo toco. Movelo o conectá esa carpeta con "
                           "oracle-factory conectar RUTA. No cambié nada")


def clonar(cli, url: str) -> Path:
    """La carpeta del clon de `url` en la carpeta de datos del usuario: la reusa si ya es un clon de esa URL, se niega si es otra
    cosa y, si no existe, clona en un temporal al lado y lo renombra (un clon que falla no deja nada)."""
    destino, existe = _clon_de(cli, url)
    if existe:
        return destino
    nombre = destino.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(dir=destino.parent, prefix=f".{nombre}."))
    try:
        hecho = _git_almacen(destino.parent, "clone", "-q", url, str(temporal))
        if hecho.returncode:
            raise cli.FactoryError(f"no pude clonar {url}: {os.fsdecode(hecho.stderr).strip()}. No cambié nada")
        temporal.rename(destino)
    except BaseException:
        shutil.rmtree(temporal, ignore_errors=True)
        raise
    print(f"Cloné el almacén {url} en {destino}.")
    return destino


def comando(cli, nombre: str, almacen: str | None, como_json: bool = False) -> int:
    """conectar [ALMACÉN] / desconectar: la conexión del producto de `cli.ROOT` vive en la configuración personal del usuario.
    `conectar --json` sólo lee: es lo que pregunta la extensión de VS Code para encontrar los registros."""
    if como_json:
        if almacen is not None:
            raise cli.FactoryError("--json sólo dice la conexión: no va con un ALMACÉN. No cambié nada")
        producto, llave = raiz_git(cli.ROOT), clave(cli.ROOT)
        try:
            actual = leer().get(llave) if llave is not None else None
        except ValueError as e:
            raise cli.FactoryError(str(e)) from e
        print(json.dumps({"conectado": actual is not None, "almacen": actual, "producto": str(producto) if producto else None},
                         ensure_ascii=False))
        return 0
    if cli.AGENTE:
        raise cli.FactoryError(f"{nombre} es una decisión de una persona (dónde van los registros): corrélo sin --agente; {cli.AGENTE} no puede")
    producto, llave = raiz_git(cli.ROOT), clave(cli.ROOT)
    if producto is None or llave is None:
        raise cli.FactoryError(f"{cli.ROOT} no está dentro de un repo Git: {nombre} necesita el producto. No cambié nada")
    try:
        datos = leer()
    except ValueError as e:
        raise cli.FactoryError(str(e)) from e
    actual = datos.get(llave)
    if nombre == "desconectar":
        if actual is None:
            print("El producto no estaba conectado a ningún almacén.")
        else:
            try:
                with actualizando() as vigentes:
                    vigentes.pop(llave, None)
            except ValueError as e:
                raise cli.FactoryError(str(e)) from e
            print(f"Producto desconectado del almacén {actual} (el almacén y el producto siguen como estaban).")
        return 0
    if almacen is None:
        print(f"El producto está conectado al almacén {actual}." if actual else "El producto no está conectado a ningún almacén.")
        return 0
    destino = (clonar(cli, almacen) if es_url(almacen) else Path(almacen)).expanduser().resolve()
    if not destino.is_dir() or raiz_git(destino) != destino:
        raise cli.FactoryError(f"{destino} no es la raíz de un repo Git existente: el almacén es un repo Git propio. No cambié nada")
    if destino.is_relative_to(producto) or producto.is_relative_to(destino):
        raise cli.FactoryError(f"el almacén ({destino}) y el producto ({producto}) no pueden estar uno dentro del otro. No cambié nada")
    if actual == str(destino):
        print(f"El producto ya está conectado al almacén {destino}; no cambié nada.")
        return 0
    antes, cwd = (cli.ROOT, cli.CHANGES), os.getcwd()
    cli.ROOT, cli.CHANGES = destino, destino / "openspec" / "changes"
    try:
        os.chdir(destino)  # los hooks y la configuración de Git de init son del almacén, no del producto
        previo = foto(destino)
        cli.PRODUCTO = producto  # init ve que prepara un almacén: no escribe su configuración de Git
        cli.inicializar()
        requisitos = cli.ruta_segura(destino / "requisitos")  # init no la crea y Git no versiona carpetas vacías
        if not requisitos.exists():
            requisitos.mkdir()
            (requisitos / ".gitkeep").write_text("", encoding="utf-8")
        commitear(cli, destino, previo, nombre)
    finally:
        os.chdir(cwd)
        cli.PRODUCTO = None
        cli.ROOT, cli.CHANGES = antes
    try:
        with actualizando() as vigentes:  # se vuelve a leer: otro conectar pudo agregar algo mientras se preparaba el almacén
            vigentes[llave] = str(destino)
    except ValueError as e:
        raise cli.FactoryError(str(e)) from e
    print(f"Producto conectado al almacén {destino}: desde cualquier carpeta o worktree del producto, Factory usa sus registros.")
    return 0


def con_el_cambio(cli, identificador: str, contexto: dict) -> dict:
    """La huella del producto (`contexto`) más la de los archivos de un cambio en el almacén: su propuesta y su spec, sus
    requisitos y los catálogos de las medidas que tiene elegidas; no los registros que Factory genera. Los archivos de otro
    cambio no cuentan: editarlos no vence la revisión ni el juicio de éste."""
    carpeta, estado = cli.leer(identificador)
    rutas = [carpeta / "proposal.md", cli.ROOT / estado["spec"],
             *(cli.requisitos_dir() / f"{r}.requisito" for r in estado.get("requisitos") or []),
             *(cli.ROOT / a for m in (estado.get("medidas") or {}).values() if isinstance(m, dict)
               for a in (m.get("archivos_catalogo") or {}).values() if isinstance(a, str) and a)]
    archivos = [[n, cli.dato_de_archivo(n, cli.ROOT / n)] for n in sorted({os.path.relpath(r, cli.ROOT) for r in rutas})]
    return {**contexto, "archivos_sha256": cli.sha256(json.dumps([contexto["archivos_sha256"], archivos]).encode())}


# --- etapa 4a: Factory commitea en el almacén lo que escribió cada comando -------------------------------------------
# Variables con las que Git apuntaría a otro repo (por ejemplo, si Factory corre dentro de un hook del producto).
_GIT_DE_OTRO_REPO = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                     "GIT_COMMON_DIR", "GIT_PREFIX", "GIT_NAMESPACE")


def _git_almacen(almacen: Path, *args: str, entrada: bytes | None = None) -> subprocess.CompletedProcess:
    entorno = {k: v for k, v in os.environ.items() if k not in _GIT_DE_OTRO_REPO}
    return subprocess.run(["git", *args], cwd=almacen, input=entrada, capture_output=True,
                          env={**entorno, "GIT_LITERAL_PATHSPECS": "1"})


def foto(almacen: Path) -> dict[str, str | None] | None:
    """Lo que Git ve cambiado en el almacén: {ruta: sha256 del contenido, o None si el archivo no está}.

    None si el almacén no es la raíz de un repo Git: ahí no hay dónde commitear. Si es un repo pero Git falla, la foto trae sólo
    la clave FALLA con el motivo: el commit no se intenta y se avisa."""
    try:
        arriba = _git_almacen(almacen, "rev-parse", "--show-toplevel")
        if arriba.returncode or Path(os.fsdecode(arriba.stdout).strip()).resolve() != almacen.resolve():
            return None
        estado = _git_almacen(almacen, "status", "--porcelain", "-z", "--no-renames", "--untracked-files=all")
        ignorado = _git_almacen(almacen, "status", "--porcelain", "-z", "--ignored=traditional", "--untracked-files=all")
    except OSError as e:
        return {FALLA: str(e)}
    if estado.returncode or ignorado.returncode:
        return {FALLA: os.fsdecode(estado.stderr + ignorado.stderr).strip() or "git status falló"}
    vista: dict[str, str | None] = {}
    for entrada in estado.stdout.split(b"\0"):
        if len(entrada) > 3 and not _es_local(os.fsdecode(entrada[3:])):  # lo local de cada máquina no entra nunca, aunque esté versionado
            vista[os.fsdecode(entrada[3:])] = _huella(almacen / os.fsdecode(entrada[3:]))
    # Lo que el .gitignore del almacén deja afuera no se commitea (manda el almacén), pero si es un registro y no algo local de
    # Factory, se avisa: va en la foto con la marca IGNORADO delante.
    for entrada in ignorado.stdout.split(b"\0"):
        if entrada.startswith(b"!! "):
            nombre = os.fsdecode(entrada[3:])  # con --untracked-files=all Git nombra cada archivo, también dentro de una carpeta ignorada
            if not _es_local(nombre):
                vista[IGNORADO + nombre] = _huella(almacen / nombre)
    return vista


IGNORADO = "\0ignorado:"  # ninguna ruta de Git empieza con NUL
FALLA = "\0falla"


def _es_local(ruta: str) -> bool:
    """Lo que es de cada máquina por diseño (no se comparte): .factory/local/ y los paquetes de Clue de cada candidato."""
    partes = ruta.split("/")
    return (ruta.startswith(estructura.IGNORAR_LOCAL)
            or (len(partes) > 5 and partes[:2] == [estructura.DIR, "cambios"] and partes[3] == "candidatos" and partes[5] == "clue"))


def _huella(ruta: Path) -> str | None:
    try:
        contenido = (b"enlace:" + os.fsencode(os.readlink(ruta)) if ruta.is_symlink()
                     else (b"x:" if ruta.stat().st_mode & 0o111 else b"-:") + ruta.read_bytes() if ruta.is_file() else None)
    except OSError:
        contenido = None
    return None if contenido is None else hashlib.sha256(contenido).hexdigest()  # el bit de ejecución también es un cambio para Git


PLAZO_DEL_BLOQUEO = 30  # segundos que un comando espera el bloqueo del commit antes de avisar y dejar los registros en el disco


def archivo_del_bloqueo(almacen: Path) -> Path:
    """El archivo del bloqueo, en la carpeta COMÚN de Git del almacén: el mismo para todos sus worktrees (H-01 de codex)."""
    hecho = _git_almacen(almacen, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if hecho.returncode or not hecho.stdout.strip():
        raise OSError(os.fsdecode(hecho.stderr).strip() or "no encontré la carpeta de Git del almacén")
    return Path(os.fsdecode(hecho.stdout).strip()) / "factory-commit.lock"


@contextlib.contextmanager
def bloqueo(almacen: Path, plazo: float | None = None):
    """El bloqueo exclusivo del commit del almacén (flock sobre un archivo de su carpeta de Git): da True si se consiguió dentro
    del `plazo` (sin plazo, espera hasta conseguirlo) y False si no. Sin fcntl (Windows) da True sin bloquear."""
    with open(archivo_del_bloqueo(almacen), "a", encoding="utf-8") as candado:
        limite = None if plazo is None else time.monotonic() + plazo
        tomado = fcntl is None
        while not tomado:
            try:
                fcntl.flock(candado, fcntl.LOCK_EX | (0 if limite is None else fcntl.LOCK_NB))
                tomado = True
            except BlockingIOError:
                if time.monotonic() >= limite:
                    break
                time.sleep(0.05)
        try:
            yield tomado
        finally:
            if tomado and fcntl:
                fcntl.flock(candado, fcntl.LOCK_UN)


def _cambio_de(ruta: str) -> str | None:
    """El cambio al que pertenece una ruta del almacén (su carpeta en .factory/cambios/, tareas/ u openspec/changes/, o su nota
    kb/cambios/ID.md); None si es común."""
    p = ruta.split("/")
    if len(p) > 3 and p[:2] in ([estructura.DIR, "cambios"], ["openspec", "changes"]):
        ident = p[2]
    elif len(p) > 2 and p[0] == "tareas":
        ident = p[1]
    elif len(p) == 3 and p[:2] == ["kb", "cambios"] and p[2].endswith(".md"):
        ident = p[2][:-3]
    else:
        return None
    return ident if estructura.ID_RE.fullmatch(ident) else None


def commitear(cli, almacen: Path, antes: dict[str, str | None] | None, comando: str, ident: str | None = None) -> None:
    """Commitea en el almacén lo que cambió desde `antes` (una `foto`); lo que ya estaba cambiado y sigue igual no entra. Con un
    cambio, entra lo suyo (también lo que ya estaba cambiado: otro comando pudo dejarlo) y lo común que cambió; lo de otro cambio
    queda para el comando de ese cambio. La foto final, el add y el commit van bajo `bloqueo`, que no se toma mientras el comando
    trabaja. No escribe configuración de Git, no sube nada y no falla: si no puede, avisa y los archivos quedan en el disco.

    ponytail: un archivo que ya estaba cambiado a mano y que el comando volvió a cambiar entra entero (no se separan las dos
    ediciones); si hiciera falta, habría que commitear por trozos. Dos comandos sobre el MISMO cambio a la vez pueden compartir
    archivos en un commit (límite declarado de la etapa 4b1)."""
    if antes is None:
        return
    try:
        with bloqueo(almacen, PLAZO_DEL_BLOQUEO) as tomado:
            motivo = (_commitear(cli, almacen, antes, comando, ident) if tomado else
                      f"otro comando de Factory tiene tomado el bloqueo del commit desde hace más de {PLAZO_DEL_BLOQUEO} s")
    except OSError as e:
        motivo = str(e)
    if motivo:
        print(f"Aviso: no se pudo commitear en el almacén ({almacen}): {motivo}\nLos registros quedaron escritos en el disco; "
              "arreglá la causa y commitealos a mano en el almacén, o el próximo comando de ese cambio los commitea.", file=sys.stderr)


def _commitear(cli, almacen: Path, antes: dict[str, str | None], comando: str, ident: str | None) -> str:
    """El commit, ya con el bloqueo tomado: devuelve el motivo si Git no pudo, o ""."""
    despues = foto(almacen) if FALLA not in antes else antes
    if FALLA in (despues or {}):
        raise OSError(f"no pude ver qué cambió en el almacén: {despues[FALLA]}")
    despues = despues or {}
    cambiados = {n for n, huella in despues.items() if n not in antes or antes[n] != huella}
    if not (ident and cli.estructura.ID_RE.fullmatch(ident)):  # `nuevo` no recibe el ID: es el del cambio que creó (sin versionar todavía)
        nuevos = {_cambio_de(n) for n in cambiados if n not in antes and n.startswith(f"{cli.estructura.DIR}/cambios/")} - {None}
        if nuevos:
            versionados = _git_almacen(almacen, "ls-files", "-z", "--", *(f"{cli.estructura.DIR}/cambios/{i}/" for i in sorted(nuevos)))
            nuevos = set() if versionados.returncode else nuevos - {_cambio_de(os.fsdecode(n)) for n in versionados.stdout.split(b"\0")}
        ident = nuevos.pop() if len(nuevos) == 1 else None
    if ident:  # lo suyo entra aunque ya estuviera cambiado; lo de otro cambio, no
        cambiados = ({n for n in cambiados if _cambio_de(n.removeprefix(IGNORADO)) in (None, ident)}
                     | {n for n in despues if _cambio_de(n) == ident})  # lo ignorado ya avisado no se vuelve a avisar
    tocados = sorted(n for n in cambiados if not n.startswith(IGNORADO))
    ignorados = sorted(n[len(IGNORADO):] for n in cambiados if n.startswith(IGNORADO))
    if ignorados:
        print("Aviso: el .gitignore del almacén deja afuera registros que este comando escribió, así que no se commitearon: "
              + ", ".join(ignorados[:10]) + (" …" if len(ignorados) > 10 else "") + ". Si son registros del equipo, sacá esa regla del .gitignore.",
              file=sys.stderr)
    if not tocados:
        return ""
    quien = cli.actor()
    pie = "\n".join([*([f"Cambio: {ident}"] if ident else []), f"Comando: {comando}", f"Actor: {quien['actor']} ({quien['tipo_actor']})"])
    rutas = b"\0".join(os.fsencode(n) for n in tocados)
    paso = _git_almacen(almacen, "add", "--pathspec-from-file=-", "--pathspec-file-nul", entrada=rutas)
    if paso.returncode == 0:  # --only: lo que ya estaba en el índice se queda en el índice, sin entrar al commit
        paso = _git_almacen(almacen, "commit", "-q", "--only", "-m", f"Factory: {comando}{' ' + ident if ident else ''}", "-m", pie,
                            "--pathspec-from-file=-", "--pathspec-file-nul", entrada=rutas)
    return "" if paso.returncode == 0 else (os.fsdecode(paso.stderr + paso.stdout).strip() or f"git terminó con código {paso.returncode}")


# --- etapa 5a: la guía de agentes y la skill van al producto, sin versionar ------------------------------------------
GUIA = ("AGENTS.md", "CLAUDE.md")
SKILL = ".claude/skills/oracle-factory/SKILL.md"
MARCA_EXCLUIR = "# oracle-factory: la guía de agentes y la skill, que no se versionan (los registros viven en un almacén aparte)"


def _ya_versionados(cli, rutas) -> list[str]:
    return [r for r in rutas if cli.git_producto(["git", "ls-files", "--error-unmatch", "--", r]).returncode == 0]


def _excluir(cli, rutas) -> None:
    """Agrega `rutas` al archivo de exclusiones local de Git del producto (común a sus worktrees), salvo las que ya ignora;
    no toca .gitignore ni la configuración de Git."""
    dice = cli.git_producto(["git", "rev-parse", "--git-common-dir"]).stdout.strip()
    archivo = (cli.PRODUCTO / dice if not Path(dice).is_absolute() else Path(dice)) / "info" / "exclude"
    faltan = [f"/{r}" for r in rutas if cli.git_producto(["git", "check-ignore", "-q", "--no-index", "--", r]).returncode != 0]
    if not faltan:
        return
    actual = archivo.read_text(encoding="utf-8") if archivo.is_file() else ""
    archivo.parent.mkdir(parents=True, exist_ok=True)
    bloque = ([MARCA_EXCLUIR] if MARCA_EXCLUIR not in actual else []) + faltan
    archivo.write_text(actual + ("\n" if actual and not actual.endswith("\n") else "") + "\n".join(bloque) + "\n", encoding="utf-8")


def guia_en_producto(cli, verificar: bool, en_el_repo: bool = False) -> None:
    """`agentes` con almacén aparte: el bloque de la guía en AGENTS.md y CLAUDE.md del producto, excluidos de Git; con `en_el_repo`,
    en los que el producto ya versiona (para un producto cuya guía es parte de él, como Factory), sin excluirlos."""
    versionados = _ya_versionados(cli, GUIA)
    if versionados and not verificar and not en_el_repo:
        raise cli.FactoryError(f"el producto ya versiona {', '.join(versionados)}: no lo modifico (ensuciaría el repo del producto). "
                               "Si la guía es parte del producto, mantenela ahí con oracle-factory agentes --en-el-repo; si no, "
                               "sacala del repo. No escribí nada")
    rutas = [cli.PRODUCTO / n for n in GUIA]
    enlaces = [r.name for r in rutas if r.is_symlink()]
    if enlaces:
        raise cli.FactoryError(f"no escribo sobre enlaces simbólicos: {', '.join(enlaces)}. No escribí nada")
    actuales = [r.read_text(encoding="utf-8") if r.is_file() else "" for r in rutas]
    try:
        esperados = [agentes.con_bloque(actuales[0], agentes.bloque(cli.config_proyecto()["modo_por_defecto"], con_almacen=True)),
                     agentes.con_claude(actuales[1])]
    except agentes.MarcasRotas as e:
        raise cli.FactoryError(str(e)) from e
    if verificar:
        viejos = [r.name for r, a, e in zip(rutas, actuales, esperados) if a != e]
        if viejos:
            raise cli.FactoryError(f"la guía para agentes no está al día en {', '.join(viejos)} del producto; corré oracle-factory agentes")
        print(f"La guía para agentes está al día en AGENTS.md del producto ({cli.PRODUCTO}), y CLAUDE.md la incluye.")
        return
    for ruta, actual, esperado in zip(rutas, actuales, esperados):
        if actual != esperado:
            descriptor, nombre = tempfile.mkstemp(dir=ruta.parent, prefix=f".{ruta.name}.", suffix=".tmp")  # escritura atómica
            with os.fdopen(descriptor, "w", encoding="utf-8") as temporal:
                temporal.write(esperado)
            os.replace(nombre, ruta)
    if en_el_repo:
        print(f"Guía para agentes en AGENTS.md del producto ({cli.PRODUCTO}), con CLAUDE.md que la incluye, en el repo: commiteala "
              "con el producto.")
        return
    _excluir(cli, GUIA)
    print(f"Guía para agentes en AGENTS.md del producto ({cli.PRODUCTO}), con CLAUDE.md que la incluye; no se versionan "
          "(van en .git/info/exclude).")


def skill_en_producto(cli, forzar: bool) -> int:
    """`skill --instalar` con almacén aparte: la skill en el producto, excluida de Git."""
    if _ya_versionados(cli, [SKILL]):
        raise cli.FactoryError(f"el producto ya versiona {SKILL}: no lo modifico (ensuciaría el repo del producto). No escribí nada")
    try:
        estado, ruta = cli.skill_mod.instalar(cli.PRODUCTO, forzar)
    except cli.skill_mod.SkillError as e:
        raise cli.FactoryError(str(e)) from e
    _excluir(cli, [SKILL])
    print({"instalada": "Skill instalada", "reemplazada": "Skill reemplazada", "igual": "La skill ya estaba instalada"}[estado]
          + f" en {SKILL} del producto; no se versiona (va en .git/info/exclude).")
    return 0


# --- etapa 4b2: sincronizar el almacén con su remoto ------------------------------------------------------------------
def sincronizar(cli) -> int:
    """Trae lo del remoto del almacén y lo une con lo local con los drivers de Factory pasados con `git -c` (no se escribe
    configuración de Git), rehace lo generado y, si es una persona, sube. Todo bajo el bloqueo del almacén; si algo falla
    antes de terminar la unión, el almacén vuelve a como estaba."""
    almacen = cli.ROOT
    if cli.PRODUCTO is None:
        raise cli.FactoryError("sincronizar es del almacén de registros aparte: conectá el producto (oracle-factory conectar URL) "
                               "o indicá --registros. No cambié nada")
    rama = os.fsdecode(_git_almacen(almacen, "symbolic-ref", "-q", "--short", "HEAD").stdout).strip()
    remoto = next(iter(sorted(os.fsdecode(_git_almacen(almacen, "remote").stdout).split(), key=lambda r: r != "origin")), None)
    if not rama or remoto is None:
        raise cli.FactoryError(f"el almacén ({almacen}) " + ("no tiene remoto" if rama else "no está en una rama")
                               + ": no hay con qué sincronizar. No cambié nada")
    with bloqueo(almacen, PLAZO_DEL_BLOQUEO) as tomado:
        if not tomado:
            raise cli.FactoryError(f"otro comando de Factory tiene tomado el bloqueo del almacén desde hace más de {PLAZO_DEL_BLOQUEO} s; "
                                   "probá de nuevo cuando termine. No cambié nada")
        vista = foto(almacen) or {}
        if FALLA in vista:
            raise cli.FactoryError(f"no pude ver el estado del almacén: {vista[FALLA]}. No cambié nada")
        sucios = sorted(n for n in vista if not n.startswith(IGNORADO))
        if sucios:
            raise cli.FactoryError(f"el almacén ({almacen}) tiene cambios sin commitear: " + ", ".join(sucios[:10])
                                   + (" …" if len(sucios) > 10 else "") + ". Commitealos o descartalos antes de sincronizar. No cambié nada")
        inicio = os.fsdecode(_git_almacen(almacen, "rev-parse", "HEAD").stdout).strip()
        try:
            _unir(cli, almacen, remoto, rama)
        except BaseException:
            _git_almacen(almacen, "merge", "--abort")
            _git_almacen(almacen, "reset", "-q", "--hard", inicio)  # el árbol estaba limpio: no se pierde nada
            raise
        if cli.AGENTE:
            print(f"Traje y uní lo de {remoto}/{rama} en el almacén; no lo subí: subir el almacén es de una persona "
                  "(oracle-factory sincronizar, sin --agente).")
            return 0
        hecho = _git_almacen(almacen, "push", "-q", remoto, f"HEAD:{rama}")
    if hecho.returncode:
        raise cli.FactoryError(f"uní lo de {remoto}/{rama} pero no pude subirlo: {os.fsdecode(hecho.stderr).strip()}. "
                               "La unión quedó commiteada en el almacén; volvé a sincronizar")
    print(f"Almacén sincronizado con {remoto}/{rama}: traje, uní y subí.")
    return 0


def _unir(cli, almacen: Path, remoto: str, rama: str) -> None:
    def git(*args: str) -> None:
        hecho = _git_almacen(almacen, *args)
        if hecho.returncode:
            raise cli.FactoryError(f"git {args[0]} falló en el almacén: {os.fsdecode(hecho.stderr + hecho.stdout).strip()}. "
                                   "Dejé el almacén como estaba")

    if cli.escribir_atributos(almacen):  # contenido versionado, no configuración: va en su propio commit, antes de unir
        git("add", "--", ".gitattributes")
        git("commit", "-q", "--only", "-m", "Factory: sincronizar (.gitattributes)", "--", ".gitattributes")
    git("fetch", "-q", remoto)
    if _git_almacen(almacen, "rev-parse", "-q", "--verify", f"refs/remotes/{remoto}/{rama}").returncode:
        return  # el remoto todavía no tiene la rama: sólo hay que subir
    # Git pisa sin avisar un archivo ignorado (o sin versionar) si la unión trae uno versionado en esa ruta: eso perdería trabajo
    # local. Si lo que agrega el remoto choca con algo que hay en el disco y no está versionado, no se une.
    agregados = os.fsdecode(_git_almacen(almacen, "diff", "--name-only", "-z", "--no-renames", "--diff-filter=A",
                                         f"HEAD...{remoto}/{rama}").stdout).split("\0")
    versionados = set(os.fsdecode(_git_almacen(almacen, "ls-files", "-z").stdout).split("\0"))
    chocan = sorted(n for n in agregados if n and n not in versionados and ((almacen / n).exists() or (almacen / n).is_symlink()))
    if chocan:
        raise cli.FactoryError(f"lo que trae {remoto}/{rama} pisaría archivos locales sin versionar o ignorados: " + ", ".join(chocan[:10])
                               + (" …" if len(chocan) > 10 else "") + ". Movelos o versionalos y volvé a sincronizar. No uní nada")
    drivers = [x for clave, valor in cli.drivers_de_union() for x in ("-c", f"{clave}={valor}")]
    hecho = _git_almacen(almacen, *drivers, "merge", "-q", "--no-edit", f"{remoto}/{rama}")
    if hecho.returncode:
        chocaron = os.fsdecode(_git_almacen(almacen, "diff", "--name-only", "--diff-filter=U").stdout).split()
        raise cli.FactoryError((f"la unión con {remoto}/{rama} chocó en " + ", ".join(chocaron) if chocaron else
                                f"git merge falló: {os.fsdecode(hecho.stderr + hecho.stdout).strip()}")
                               + ". La deshice y dejé el almacén como estaba; resolvelo a mano en el almacén y volvé a sincronizar")
    cli.rehacer_generado()


# Las carpetas y archivos de Factory y de su proyecto Oracle en la raíz de un proyecto (etapa 6: lo que migra al almacén).
REGISTROS_DEL_PROYECTO = (estructura.DIR, "openspec", "tareas", "kb", "catalogos", "corpus", "diferencial", "relaciones",
                          "requisitos", "macros", "oracle.json")


def _lista(salida: bytes) -> list[str]:
    return [os.fsdecode(n) for n in salida.split(b"\0") if n]


def _resumen(nombres: list[str], tope: int = 10) -> str:
    return ", ".join(nombres[:tope]) + (f" y {len(nombres) - tope} más" if len(nombres) > tope else "")


def _destino_sin_registros(cli, destino: Path, producto: Path) -> None:
    if not destino.is_dir() or raiz_git(destino) != destino:
        raise cli.FactoryError(f"{destino} no es la raíz de un repo Git existente: el almacén es un repo Git propio. No cambié nada")
    if destino.is_relative_to(producto) or producto.is_relative_to(destino):
        raise cli.FactoryError(f"el almacén ({destino}) y el producto ({producto}) no pueden estar uno dentro del otro. No cambié nada")
    ocupados = [r for r in REGISTROS_DEL_PROYECTO if (destino / r).exists() or (destino / r).is_symlink()]
    if ocupados:
        raise cli.FactoryError(f"el almacén {destino} ya tiene registros de Factory ({', '.join(ocupados)}): migrar no mezcla dos "
                               "proyectos. Usá un repo sin ellos. No cambié nada")


def _remoto_sin_registros(cli, url: str) -> None:
    """Para `migrar --verificar` con una URL sin clon: un clon superficial en un temporal (que se borra) dice si se puede clonar
    y si el almacén ya tiene registros."""
    with tempfile.TemporaryDirectory(prefix="factory-verificar-") as tmp:
        hecho = _git_almacen(Path(tmp), "clone", "-q", "--depth", "1", "--no-checkout", url, "clon")
        if hecho.returncode:
            raise cli.FactoryError(f"no pude clonar {url}: {os.fsdecode(hecho.stderr).strip()}. No cambié nada")
        arbol = _git_almacen(Path(tmp) / "clon", "ls-tree", "-z", "--name-only", "HEAD")
        nombres = set(_lista(arbol.stdout)) if arbol.returncode == 0 else set()  # sin HEAD: un repo vacío, sin registros
    ocupados = [r for r in REGISTROS_DEL_PROYECTO if r in nombres]
    if ocupados:
        raise cli.FactoryError(f"el almacén {url} ya tiene registros de Factory ({', '.join(ocupados)}): migrar no mezcla dos "
                               "proyectos. Usá un repo sin ellos. No cambié nada")


LIMPIAR = (".gitignore", ".gitattributes")  # los archivos del producto donde Factory escribe líneas suyas


def _sin_lo_de_factory(cli, producto: Path) -> dict[str, bytes | None]:
    """{archivo: contenido sin las líneas de Factory, o None si no queda nada} de los de LIMPIAR que tienen alguna."""
    de_factory = {".gitignore": {estructura.IGNORAR_LOCAL, estructura.IGNORAR_CLUE},
                  ".gitattributes": {cli.ATRIBUTOS_MARCA, *cli.ATRIBUTOS}}  # todas las líneas del bloque se van: la marca también
    cambios: dict[str, bytes | None] = {}
    for nombre, lineas in de_factory.items():
        ruta = producto / nombre
        if not ruta.is_file() or ruta.is_symlink():
            continue
        todas = ruta.read_text(encoding="utf-8").splitlines()
        quedan = [l for l in todas if " ".join(l.split()) not in lineas]  # otro espaciado es la misma línea (escribir_atributos)
        if len(quedan) != len(todas):
            cambios[nombre] = ("\n".join(quedan) + "\n").encode("utf-8") if any(l.strip() for l in quedan) else None
    return cambios


def _hooks_de_factory(cli, producto: Path) -> list[Path]:
    """Los hooks del trailer y de rehacer lo generado que instaló Factory (por su marca): sin registros en el producto, sobran.
    La puerta pre-push no está entre ellos."""
    dice = _git(producto, "rev-parse", "--path-format=absolute", "--git-path", "hooks")
    carpeta = Path(dice) if dice else None
    return [carpeta / n for n in (*cli.HOOKS, "post-commit", "post-merge") if carpeta and (carpeta / n).is_file()
            and not (carpeta / n).is_symlink() and cli.HOOK_MARCA in (carpeta / n).read_text(encoding="utf-8", errors="replace")]


def _foto_de(destino: Path, nombres: tuple[str, ...]) -> dict[str, tuple[bytes | None, str]]:
    """{nombre: (contenido o None si no está, su entrada del índice)} de archivos del almacén, para devolverlos si algo falla."""
    return {n: ((destino / n).read_bytes() if (destino / n).is_file() else None,
                os.fsdecode(_git_almacen(destino, "ls-files", "-s", "--", n).stdout).strip()) for n in nombres}


def _deshacer_copia(destino: Path, rutas: list[str], antes: dict[str, tuple[bytes | None, str]]) -> None:
    """Deja el almacén como estaba antes de copiar: borra las rutas copiadas (no tenía ninguna, ver _destino_sin_registros) y
    devuelve los archivos de `antes` (.gitignore, .gitattributes) y sus entradas del índice."""
    _git_almacen(destino, "rm", "-r", "-q", "--cached", "--ignore-unmatch", "--", *rutas)
    for r in rutas:
        camino = destino / r
        if camino.is_dir() and not camino.is_symlink():
            shutil.rmtree(camino, ignore_errors=True)
        elif camino.exists() or camino.is_symlink():
            camino.unlink()
    for nombre, (contenido, indice) in antes.items():
        if contenido is None:
            (destino / nombre).unlink(missing_ok=True)
        else:
            (destino / nombre).write_bytes(contenido)
        if indice:
            modo, sha = indice.split()[:2]
            _git_almacen(destino, "update-index", "--cacheinfo", f"{modo},{sha},{nombre}")
        else:
            _git_almacen(destino, "rm", "-q", "--cached", "--ignore-unmatch", "--", nombre)


def migrar(cli, almacen: str, verificar: bool) -> int:
    """migrar --almacen ALMACÉN (etapa 6): copia los registros versionados del producto al almacén en un commit, mueve lo no
    versionado de esas carpetas, conecta el producto y borra sus registros dejando la baja en el índice sin commitear."""
    if cli.AGENTE:
        raise cli.FactoryError(f"migrar --almacen es una decisión de una persona (dónde van los registros): corrélo sin --agente; "
                               f"{cli.AGENTE} no puede. No cambié nada")
    producto, llave = raiz_git(cli.ROOT), clave(cli.ROOT)
    if producto is None or llave is None:
        raise cli.FactoryError(f"{cli.ROOT} no está dentro de un repo Git: migrar --almacen necesita el producto. No cambié nada")
    if not (producto / estructura.DIR).is_dir() or (producto / estructura.DIR).is_symlink():
        raise cli.FactoryError(f"el producto ({producto}) no tiene registros propios en {estructura.DIR}/ en su raíz: no hay qué migrar. "
                               "No cambié nada")
    try:
        actual = leer().get(llave)
    except ValueError as e:
        raise cli.FactoryError(str(e)) from e
    if actual is not None:
        raise cli.FactoryError(f"el producto ya está conectado al almacén {actual}: desconectalo antes (oracle-factory desconectar). "
                               "No cambié nada")
    movimientos, problemas, _ = cli.migracion.planear(producto)
    if movimientos or problemas:
        raise cli.FactoryError("el producto tiene registros con el formato anterior a la fase 2: corré primero oracle-factory migrar "
                               "(sin --almacen) y commiteá el resultado. No cambié nada")
    rutas = [r for r in REGISTROS_DEL_PROYECTO if (producto / r).exists() or (producto / r).is_symlink()]
    estado = _git_almacen(producto, "status", "--porcelain", "-z", "--no-renames", "--untracked-files=all", "--", *rutas)
    if estado.returncode:
        raise cli.FactoryError(f"git status falló en el producto: {os.fsdecode(estado.stderr).strip()}. No cambié nada")
    sucios = _lista(estado.stdout)
    sueltos = [n[3:] for n in sucios if n.startswith("?? ")]
    cambiados = [n[3:] for n in sucios if not n.startswith("?? ")]
    if cambiados:
        raise cli.FactoryError(f"los registros del producto tienen cambios sin commitear ({_resumen(cambiados)}): commitealos o "
                               "descartalos antes, así la copia es la de un commit. No cambié nada")
    if sueltos:
        raise cli.FactoryError(f"hay archivos sin versionar en los registros del producto que Git no ignora ({_resumen(sueltos)}): "
                               "commitealos, ignoralos o sacalos antes. No cambié nada")
    limpieza, hooks = _sin_lo_de_factory(cli, producto), _hooks_de_factory(cli, producto)
    if limpieza:
        propios = _lista(_git_almacen(producto, "status", "--porcelain", "-z", "--untracked-files=all", "--", *limpieza).stdout)
        if propios:
            raise cli.FactoryError(f"{', '.join(n[3:] for n in propios)} del producto tiene cambios sin commitear o no está versionado: "
                                   "migrar le saca las líneas de Factory y deja eso en el índice, y se llevaría lo tuyo. Commitealo antes. "
                                   "No cambié nada")
    versionados = _lista(_git_almacen(producto, "ls-files", "-z", "--", *rutas).stdout)
    locales = _lista(_git_almacen(producto, "ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--", *rutas).stdout)
    if es_url(almacen):
        if verificar:  # MIG-003: lo mismo que comprobaría la migración, sin escribir en la carpeta de los clones
            destino, existe = _clon_de(cli, almacen)
            if existe:
                _destino_sin_registros(cli, destino.resolve(), producto)
            else:
                _remoto_sin_registros(cli, almacen)
        else:
            destino = clonar(cli, almacen).resolve()
            _destino_sin_registros(cli, destino, producto)
    else:
        destino = Path(almacen).expanduser().resolve()
        _destino_sin_registros(cli, destino, producto)
    if verificar:
        por_carpeta: dict[str, int] = {}
        for n in versionados:
            por_carpeta[n.split("/", 1)[0]] = por_carpeta.get(n.split("/", 1)[0], 0) + 1
        print(f"Copiaría al almacén {destino} {len(versionados)} archivos versionados ("
              + ", ".join(f"{c}: {k}" for c, k in sorted(por_carpeta.items())) + ") en un commit, "
              f"y movería {len(locales)} archivos sin versionar" + (f": {_resumen(locales, 20)}" if locales else "") + ".")
        if limpieza:
            print("Sacaría las líneas de Factory de " + ", ".join(
                f"{n} (se borraría: no le queda otra)" if c is None else n for n, c in limpieza.items()) + " del producto.")
        if hooks:
            print(f"Sacaría los hooks de Factory {', '.join(h.name for h in hooks)} (el pre-push queda).")
        print("Después conectaría el producto y borraría sus registros dejando la baja sin commitear. No escribí nada.")
        return 0
    cabeza = _git(producto, "rev-parse", "HEAD") or "sin commits"
    quien = cli.actor()
    with bloqueo(destino, PLAZO_DEL_BLOQUEO) as tomado:  # MIG-004: el bloqueo antes de copiar; sin él no se copia nada
        if not tomado:
            raise cli.FactoryError(f"otro comando de Factory tiene tomado el bloqueo del almacén {destino}: volvé a intentar cuando "
                                   "termine. No cambié nada")
        antes = _foto_de(destino, LIMPIAR)
        previo = _git(destino, "rev-parse", "-q", "--verify", "HEAD")  # None si el almacén no tiene commits
        falla = None
        try:  # se copia también lo de la máquina (.factory/local/, paquetes de Clue): el producto no cambia hasta el final
            for n in [*versionados, *locales]:
                copia = destino / n
                copia.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(producto / n, copia, follow_symlinks=False)
            contenido = (antes[".gitignore"][0] or b"").decode("utf-8")
            faltan = [r for r in (estructura.IGNORAR_LOCAL, estructura.IGNORAR_CLUE) if r not in contenido.splitlines()]
            if faltan:
                (destino / ".gitignore").write_text(contenido + ("\n" if contenido and not contenido.endswith("\n") else "")
                                                    + "\n".join(faltan) + "\n", encoding="utf-8")
            atributos = cli.escribir_atributos(destino)  # los drivers de unión siguen a los registros
            rutas_nul = b"\0".join(os.fsencode(n) for n in [*versionados, *([".gitignore"] if faltan else []),
                                                              *([".gitattributes"] if atributos else [])])
            paso = _git_almacen(destino, "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul", entrada=rutas_nul)
            if paso.returncode == 0:
                paso = _git_almacen(destino, "commit", "-q", "--only", "-m", f"Factory: migrar los registros del producto ({cabeza[:12]})",
                                    "-m", f"Producto: {producto}\nCommit de origen: {cabeza}\nActor: {quien['actor']} ({quien['tipo_actor']})",
                                    "--pathspec-from-file=-", "--pathspec-file-nul", entrada=rutas_nul)
            if paso.returncode:
                falla = f"no pude commitear: {os.fsdecode(paso.stderr + paso.stdout).strip()}"
        except (OSError, UnicodeDecodeError) as e:
            falla = f"no pude copiar los registros: {e}"
        if not falla:
            try:
                with actualizando() as vigentes:
                    vigentes[llave] = str(destino)
            except (OSError, ValueError) as e:  # MIG-005: se deshace el commit recién hecho (bajo el bloqueo, sin publicar)
                falla = f"no pude guardar la conexión del producto: {e}"
                hecho = _git(destino, "rev-parse", "HEAD")
                vuelta = _git_almacen(destino, "update-ref", "HEAD", previo, hecho) if previo else \
                    _git_almacen(destino, "update-ref", "-d", "HEAD", hecho)
                if vuelta.returncode:
                    raise cli.FactoryError(f"{falla}; tampoco pude deshacer el commit {hecho} del almacén {destino} "
                                           f"({os.fsdecode(vuelta.stderr).strip()}). El producto sigue como estaba") from e
        if falla:
            _deshacer_copia(destino, rutas, antes)
            raise cli.FactoryError(f"{falla}. Deshice lo copiado en el almacén {destino}: no cambié nada en el producto ni en el almacén")
    baja = _git_almacen(producto, "rm", "-r", "-q", "--cached", "--pathspec-from-file=-", "--pathspec-file-nul",
                        entrada=b"\0".join(os.fsencode(n) for n in versionados))
    if baja.returncode:  # sin la baja en el índice no se borra nada del disco: el producto queda conectado y entero
        raise cli.FactoryError(f"git rm --cached falló en el producto ({os.fsdecode(baja.stderr).strip()}). Los registros ya están "
                               f"commiteados en el almacén {destino} y el producto quedó conectado a él, pero no borré nada del "
                               "producto. Arreglá la causa y terminá con: git rm -r -q --cached -- " + " ".join(rutas)
                               + "; rm -rf -- " + " ".join(rutas))
    try:
        for r in rutas:
            camino = producto / r
            if camino.is_dir() and not camino.is_symlink():
                shutil.rmtree(camino)
            else:
                camino.unlink()
    except OSError as e:  # todo está ya en el almacén y la baja en el índice: sólo falta terminar de borrar
        raise cli.FactoryError(f"no pude borrar los registros del producto ({e}). Ya están commiteados en el almacén {destino}, el "
                               "producto quedó conectado y la baja está en su índice; terminá con: rm -rf -- " + " ".join(rutas)) from e
    try:  # lo último: las líneas y los hooks de Factory que sobran en el producto
        for nombre, contenido in limpieza.items():
            if contenido is None:
                (producto / nombre).unlink()
            else:
                (producto / nombre).write_bytes(contenido)
        if limpieza:
            hecho = _git_almacen(producto, "add", "-A", "--", *limpieza)
            if hecho.returncode:
                raise OSError(os.fsdecode(hecho.stderr).strip())
        for hook in hooks:
            hook.unlink()
    except OSError as e:
        raise cli.FactoryError(f"migré los registros al almacén {destino} y el producto quedó conectado, pero no pude sacar lo de "
                               f"Factory de {', '.join([*limpieza, *(h.name for h in hooks)])} ({e}); sacalo a mano y preparalo con git add") from e
    print(f"Migré {len(versionados)} archivos versionados al almacén {destino} (commit «Factory: migrar…») y moví {len(locales)} "
          "sin versionar; el producto quedó conectado a él.")
    if limpieza or hooks:
        print("Saqué lo de Factory del producto: " + ", ".join([*limpieza, *(f"el hook {h.name}" for h in hooks)]) + ".")
    print("No commiteé en el producto: la baja de los registros quedó preparada en su índice. Revisala con git status y commiteala.")
    return 0
