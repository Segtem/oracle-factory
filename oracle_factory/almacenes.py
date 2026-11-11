"""Los almacenes de registros conectados (etapa 2 de 6): en la configuración personal del usuario, nunca en el repo del producto.

`$XDG_CONFIG_HOME/oracle-factory/almacenes.json` (o `~/.config/...`): {directorio común de Git del producto: ruta del almacén}.
No importa cli.py: los errores salen como ValueError y quien llama los muestra."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

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
                               "no se adivina dónde escribir. Quitá la conexión (oracle-factory desconectar) o migrar los registros al almacén "
                               "(etapa 6 de 6, todavía no existe). No se escribió nada.")
    return Path(almacen)


def comando(cli, nombre: str, almacen: Path | None) -> int:
    """conectar [ALMACÉN] / desconectar: la conexión del producto de `cli.ROOT` vive en la configuración personal del usuario."""
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
    destino = almacen.expanduser().resolve()
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

    None si el almacén no es la raíz de un repo Git: ahí no hay dónde commitear."""
    try:
        arriba = _git_almacen(almacen, "rev-parse", "--show-toplevel")
        if arriba.returncode or Path(os.fsdecode(arriba.stdout).strip()).resolve() != almacen.resolve():
            return None
        estado = _git_almacen(almacen, "status", "--porcelain", "-z", "--no-renames", "--untracked-files=all")
    except OSError:
        return None
    ignorado = _git_almacen(almacen, "status", "--porcelain", "-z", "--ignored=traditional", "--untracked-files=all")
    if estado.returncode or ignorado.returncode:
        return None
    vista: dict[str, str | None] = {}
    for entrada in estado.stdout.split(b"\0"):
        if len(entrada) > 3:
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


def _es_local(ruta: str) -> bool:
    """Lo que es de cada máquina por diseño (no se comparte): .factory/local/ y los paquetes de Clue de cada candidato."""
    partes = ruta.split("/")
    return (ruta.startswith(estructura.IGNORAR_LOCAL)
            or (len(partes) > 5 and partes[:2] == [estructura.DIR, "cambios"] and partes[3] == "candidatos" and partes[5] == "clue"))


def _huella(ruta: Path) -> str | None:
    try:
        contenido = os.fsencode(os.readlink(ruta)) if ruta.is_symlink() else ruta.read_bytes() if ruta.is_file() else None
    except OSError:
        contenido = None
    return None if contenido is None else hashlib.sha256(contenido).hexdigest()


def commitear(cli, almacen: Path, antes: dict[str, str | None] | None, comando: str, ident: str | None = None) -> None:
    """Commitea en el almacén exactamente lo que cambió desde `antes` (una `foto`); lo que ya estaba cambiado y sigue igual
    no entra. No escribe configuración de Git, no sube nada y no falla: si Git no puede, avisa y los archivos quedan en el disco.

    ponytail: un archivo que ya estaba cambiado a mano y que el comando volvió a cambiar entra entero (no se separan las dos
    ediciones); si hiciera falta, habría que commitear por trozos."""
    if antes is None:
        return
    try:
        despues = foto(almacen)
        cambiados = sorted(n for n, huella in (despues or {}).items() if n not in antes or antes[n] != huella)
        tocados = [n for n in cambiados if not n.startswith(IGNORADO)]
        ignorados = [n[len(IGNORADO):] for n in cambiados if n.startswith(IGNORADO)]
        if ignorados:
            print("Aviso: el .gitignore del almacén deja afuera registros que este comando escribió, así que no se commitearon: "
                  + ", ".join(ignorados[:10]) + (" …" if len(ignorados) > 10 else "") + ". Si son registros del equipo, sacá esa regla del .gitignore.",
                  file=sys.stderr)
        if not tocados:
            return
        if not (ident and cli.estructura.ID_RE.fullmatch(ident)):  # `nuevo` no recibe el ID: sale de lo que escribió
            ids = {p[2] for p in (Path(n).parts for n in tocados)
                   if len(p) > 3 and p[:2] in ((cli.estructura.DIR, "cambios"), ("openspec", "changes")) and cli.estructura.ID_RE.fullmatch(p[2])}
            ident = ids.pop() if len(ids) == 1 else None
        quien = cli.actor()
        pie = "\n".join([*([f"Cambio: {ident}"] if ident else []), f"Comando: {comando}", f"Actor: {quien['actor']} ({quien['tipo_actor']})"])
        rutas = b"\0".join(os.fsencode(n) for n in tocados)
        paso = _git_almacen(almacen, "add", "--pathspec-from-file=-", "--pathspec-file-nul", entrada=rutas)
        if paso.returncode == 0:  # --only: lo que ya estaba en el índice se queda en el índice, sin entrar al commit
            paso = _git_almacen(almacen, "commit", "-q", "--only", "-m", f"Factory: {comando}{' ' + ident if ident else ''}", "-m", pie,
                                "--pathspec-from-file=-", "--pathspec-file-nul", entrada=rutas)
        motivo = "" if paso.returncode == 0 else (os.fsdecode(paso.stderr + paso.stdout).strip() or f"git terminó con código {paso.returncode}")
    except OSError as e:
        motivo = str(e)
    if motivo:
        print(f"Aviso: no se pudo commitear en el almacén ({almacen}): {motivo}\nLos registros quedaron escritos en el disco; "
              "arreglá la causa y commitealos a mano en el almacén.", file=sys.stderr)
