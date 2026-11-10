"""Los almacenes de registros conectados (etapa 2 de 6): en la configuración personal del usuario, nunca en el repo del producto.

`$XDG_CONFIG_HOME/oracle-factory/almacenes.json` (o `~/.config/...`): {directorio común de Git del producto: ruta del almacén}.
No importa cli.py: los errores salen como ValueError y quien llama los muestra."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


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
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text(json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temporal.replace(ruta)


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
            guardar({k: v for k, v in datos.items() if k != llave})
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
        cli.inicializar()
        requisitos = cli.ruta_segura(destino / "requisitos")  # init no la crea y Git no versiona carpetas vacías
        if not requisitos.exists():
            requisitos.mkdir()
            (requisitos / ".gitkeep").write_text("", encoding="utf-8")
    finally:
        os.chdir(cwd)
        cli.ROOT, cli.CHANGES = antes
    guardar({**datos, llave: str(destino)})
    print(f"Producto conectado al almacén {destino}: desde cualquier carpeta o worktree del producto, Factory usa sus registros.")
    return 0
