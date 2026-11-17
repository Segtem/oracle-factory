"""Factory produce los hechos: corre el sensor que declara el proyecto sobre un checkout limpio del commit y dice de dónde salen.

El sensor se declara en `.factory/config.json`:

    "sensor": {"comando": ["{python}", "tools/sensor.py", "--salida", "{salida}"], "tope_minutos": 60, "hechos": "avisar"}

`comando` es una lista de argumentos; sus marcadores se reemplazan al correrlo: `{python}` (el Python de Factory), `{cambio}`,
`{salida}` (la carpeta de evidencia del candidato, que el sensor crea y donde deja `hechos.json`), `{registros}` (dónde están los
registros: el almacén, si está conectado) y `{producto}` (la carpeta del producto, para lo que no se versiona, como `node_modules`).
Con `"hechos": "exigir"`, `cerrar` pide que los hechos del veredicto los haya producido Factory; con `"avisar"` (el valor por
defecto), sólo se avisa.

La declaración la aprueba una persona (`oracle-factory aprobar-sensor`): `evidencia` sólo corre un sensor aprobado y sólo los hechos
de un sensor aprobado cuentan como «producidos por Factory». Las aprobaciones quedan en `.factory/sensor-aprobado.json`. Límite: ese
archivo y el registro no están firmados; quien los escribe a mano puede fingir una aprobación (el límite declarado de Factory).

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from . import estructura, procesos

CLAVES = {"comando", "tope_minutos", "hechos"}
POLITICAS = ("avisar", "exigir")
TOPE_MINUTOS = 60
MARCADORES = ("python", "cambio", "salida", "registros", "producto")
EJEMPLO = '"sensor": {"comando": ["{python}", "tools/sensor.py", "--salida", "{salida}"], "tope_minutos": 60, "hechos": "avisar"}'


def validar(valor) -> dict | None:
    """La declaración del sensor, completa con sus valores por defecto; None si no hay. ValueError si no sirve."""
    if valor is None:
        return None
    if not isinstance(valor, dict) or set(valor) - CLAVES:
        raise ValueError(f"«sensor» es un objeto con {', '.join(sorted(CLAVES))}")
    comando = valor.get("comando")
    if not isinstance(comando, list) or not comando or not all(isinstance(a, str) and a for a in comando):
        raise ValueError("«sensor.comando» es una lista no vacía de argumentos (texto)")
    tope = valor.get("tope_minutos", TOPE_MINUTOS)
    if isinstance(tope, bool) or not isinstance(tope, (int, float)) or tope <= 0:
        raise ValueError("«sensor.tope_minutos» es un número positivo")
    hechos = valor.get("hechos", "avisar")
    if hechos not in POLITICAS:
        raise ValueError(f"«sensor.hechos» es {' o '.join(POLITICAS)}")
    return {"comando": list(comando), "tope_minutos": tope, "hechos": hechos}


APROBADOS = "sensor-aprobado.json"  # en los registros: [{sha256, declaracion, actor, tipo_actor, cuando}], de la más vieja a la más nueva


def _legible(dato) -> str:
    return json.dumps(dato, ensure_ascii=False, indent=2)


def huella(config: dict) -> str:
    """La huella de una declaración ya validada (comando, tope y política): lo que una persona aprueba."""
    return cli.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def aprobados() -> list[dict]:
    """Las declaraciones que aprobó una persona. FactoryError si el archivo no se puede leer o no tiene la forma esperada."""
    ruta = cli.ruta_segura(cli.ROOT / estructura.DIR / APROBADOS)
    if not ruta.is_file():
        return []
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise cli.FactoryError(f"{estructura.DIR}/{APROBADOS} no se puede leer: {e}") from e
    if not isinstance(datos, list) or not all(_aprobacion_valida(a) for a in datos):
        raise cli.FactoryError(f"{estructura.DIR}/{APROBADOS} no tiene la forma esperada: cada aprobación lleva su declaración, la huella "
                               "de esa declaración, quién (una persona) y cuándo. Restauralo desde Git (git restore)")
    return datos


def _aprobacion_valida(a) -> bool:
    """Una aprobación completa, de una persona, cuya huella es la de su declaración (un archivo dañado no cuenta como aprobación)."""
    if not (isinstance(a, dict) and isinstance(a.get("sha256"), str) and isinstance(a.get("declaracion"), dict)
            and isinstance(a.get("actor"), str) and a["actor"] and a.get("tipo_actor") == "persona" and isinstance(a.get("cuando"), str)):
        return False
    try:
        return huella(validar(a["declaracion"])) == a["sha256"]
    except ValueError:
        return False


def aprobado(config: dict) -> bool:
    return huella(config) in {a["sha256"] for a in aprobados()}


def _huellas_aprobadas() -> set[str]:
    """Para las consultas: si el archivo de aprobaciones está roto, ninguna cuenta (y `evidencia` dice por qué)."""
    try:
        return {a["sha256"] for a in aprobados()}
    except cli.FactoryError:
        return set()


def aprobar() -> int:
    """`oracle-factory aprobar-sensor`: una persona aprueba la declaración vigente del sensor."""
    cli.exigir_terminal("«Aprobar este sensor para producir los hechos»")  # con --agente se niega siempre, también si ya está aprobado
    config = cli.config_proyecto()["sensor"]
    if not config:
        raise cli.FactoryError("el proyecto no declara su sensor: agregalo en .factory/config.json, por ejemplo " + EJEMPLO)
    previas = aprobados()
    nueva = huella(config)
    if nueva in {a["sha256"] for a in previas}:
        print("Este sensor ya está aprobado; no hay nada que hacer.")
        return 0
    print(f"Sensor declarado en {estructura.DIR}/config.json (el que correría oracle-factory evidencia):")
    print(_legible(config))
    if previas:
        ultima = previas[-1]
        print(f"Último sensor aprobado ({ultima.get('actor')}, {ultima.get('cuando')}):")
        print(_legible(ultima.get("declaracion")))
    else:
        print("Todavía no hay ningún sensor aprobado en este proyecto.")
    cli.confirmar_persona(("Aprobar este sensor para producir los hechos", "Aprobar el sensor",
                           "oracle-factory evidencia correrá ese comando sobre cada candidato, y sus hechos contarán como producidos por Factory"),
                          "aprobación cancelada; el sensor sigue sin aprobar")
    quien = cli.actor()  # una persona: exigir_terminal y confirmar_persona se niegan con --agente y sin terminal
    if cli.config_proyecto()["sensor"] != config or aprobados() != previas:
        raise cli.FactoryError("la configuración o las aprobaciones cambiaron mientras se aprobaba; volvé a mirarlas. No registré nada")
    ruta = cli.ruta_segura(cli.ROOT / estructura.DIR / APROBADOS)
    # ponytail: una lista en un archivo; dos ramas que aprueban a la vez chocan en Git y lo resuelve una persona.
    cli.escribir_atomico(ruta, (_legible([*previas, {"sha256": nueva, "declaracion": config, **quien, "cuando": cli.ahora()}])
                                + "\n").encode("utf-8"))
    print(f"Sensor aprobado por {quien['actor']}. Quedó en {estructura.DIR}/{APROBADOS}.")
    return 0


CONSERVADAS = ("LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "LC_MESSAGES", "TERM", "TZ")  # lo único del entorno que pasa tal cual


def entorno_minimo() -> dict[str, str]:
    """El entorno del sensor: un PATH fijo (las carpetas del sistema, la del Python de Factory y ~/.local/bin del usuario real), el HOME y
    el usuario de la base del sistema, la carpeta temporal, el idioma, y PYTHONNOUSERSITE. Nada más del entorno de quien lo corre."""
    import pwd
    usuario = pwd.getpwuid(os.getuid())
    # Primero las del sistema: una carpeta del usuario (la del Python de Factory, ~/.local/bin) la puede escribir quien corre
    # evidencia, y un «sh» o un «git» puesto ahí suplantaría al del comando aprobado. Las del usuario sólo agregan lo que el sistema no tiene.
    carpetas = ["/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin",
                str(Path(sys.executable).parent), str(Path(usuario.pw_dir) / ".local" / "bin")]
    return {**{k: os.environ[k] for k in CONSERVADAS if k in os.environ}, "PATH": os.pathsep.join(dict.fromkeys(carpetas)),
            "HOME": usuario.pw_dir, "USER": usuario.pw_name, "LOGNAME": usuario.pw_name, "TMPDIR": tempfile.gettempdir(),
            "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def _git(args: list[str]) -> subprocess.CompletedProcess:
    """Git para elegir el commit y armar el checkout del sensor: el del sistema, con el entorno mínimo, sin la configuración global ni
    la del sistema y sin hooks. El código que corre el sensor es el del commit, no el que deje un «git» o un hook de quien corre
    evidencia. Límite: quien controla el entorno del propio proceso de Factory (su Python o sus módulos) está fuera de este alcance."""
    entorno = {**entorno_minimo(), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    git = shutil.which("git", path=entorno["PATH"]) or "git"
    # Lo que la configuración local del producto podría hacer correr: hooks, fsmonitor, un diff externo o un paginador.
    neutro = [f"core.hooksPath={os.devnull}", "core.fsmonitor=false", "core.pager=cat", "diff.external=", "core.sshCommand=false"]
    return subprocess.run([git, *(x for c in neutro for x in ("-c", c)), *args], capture_output=True, text=True, env=entorno,
                          stdin=subprocess.DEVNULL)


def _reemplazar(argumento: str, valores: dict[str, str]) -> str:
    for nombre in MARCADORES:  # str.replace y no format: un comando de shell puede llevar sus propias llaves
        argumento = argumento.replace("{" + nombre + "}", valores[nombre])
    return argumento


def producir(identificador: str, extra: list[str]) -> None:
    """`oracle-factory evidencia ID`: corre el sensor sobre un checkout limpio de HEAD y registra la producción en el cambio."""
    config = cli.config_proyecto()["sensor"]
    cli.abierto(identificador)
    if not config:
        raise cli.FactoryError("el proyecto no declara su sensor: agregalo en .factory/config.json, por ejemplo " + EJEMPLO)
    if extra:
        raise cli.FactoryError("oracle-factory evidencia no acepta argumentos para el sensor: corre exactamente el comando que aprobó una "
                               "persona (unos argumentos agregados no los aprobó nadie). Si el sensor los necesita, que vayan en su "
                               "declaración y que una persona la apruebe. No se corrió nada")
    if not aprobado(config):
        raise cli.FactoryError("el sensor declarado no es uno que haya aprobado una persona (nunca se aprobó, o cambió desde entonces): "
                               "pedile que lo mire y corra oracle-factory aprobar-sensor. No se corrió nada")
    producto = str(cli.PRODUCTO or cli.ROOT)
    locales = [n for n in (_git(["-C", producto, "diff", "--name-only", "HEAD"]).stdout.splitlines()
                           + _git(["-C", producto, "ls-files", "--others", "--exclude-standard"]).stdout.splitlines()) if cli.es_producto(n)]
    if locales:
        raise cli.FactoryError("el producto tiene cambios sin commitear: " + ", ".join(locales[:10]) + (" …" if len(locales) > 10 else "")
                               + ". La evidencia se produce del commit: commitealos o guardalos aparte. No se corrió nada")
    head = _git(["-C", producto, "rev-parse", "--verify", "HEAD"]).stdout.strip()
    if not head:
        raise cli.FactoryError("el producto no tiene ningún commit todavía")
    sha = head[:7]
    salida = cli.ruta_segura(estructura.ruta_canonica(cli.ROOT, identificador, "evidencia", sha))
    if salida.exists():
        raise cli.FactoryError(f"ya hay evidencia del candidato {sha} ({salida.relative_to(cli.ROOT)}): un commit nuevo es un candidato "
                               "nuevo; si querés repetirla sobre este, borrá esa carpeta primero")
    registros = cli.ROOT.resolve()
    temporal = Path(tempfile.gettempdir()).resolve()
    for nombre, raiz in (("del producto", (cli.PRODUCTO or cli.ROOT).resolve()), ("de los registros", registros)):
        if temporal.is_relative_to(raiz):
            raise cli.FactoryError(f"la carpeta temporal del sistema ({temporal}) está dentro de la carpeta {nombre} ({raiz}): el checkout "
                                   "no puede ir ahí. Elegí otra con TMPDIR (o TEMP, TMP). No se corrió nada")
    # En la carpeta temporal del sistema: fuera del producto y del almacén (un producto dentro de sus registros no corre). --shared toma
    # prestados los objetos del repositorio en lugar de copiarlos, aunque la carpeta temporal esté en otro disco; dura lo que la corrida.
    with tempfile.TemporaryDirectory(prefix=f"oracle-factory-sensor-{sha}-") as tmp:
        checkout = Path(tmp) / "producto"
        p = _git(["clone", "--quiet", "--shared", "--no-checkout", producto, str(checkout)])
        if not p.returncode:
            p = _git(["-C", str(checkout), "checkout", "--quiet", "--detach", head])
        for remoto in _git(["-C", str(checkout), "remote"]).stdout.split() if not p.returncode else []:
            p = _git(["-C", str(checkout), "remote", "remove", remoto])  # sin remoto: el sensor no empuja nada
        if p.returncode:
            raise cli.FactoryError(f"no pude preparar el checkout limpio del commit {sha}: {(p.stderr or p.stdout).strip()}")
        valores = {"python": sys.executable, "cambio": identificador, "salida": str(salida), "registros": str(registros),
                   "producto": str((cli.PRODUCTO or cli.ROOT).resolve())}
        argv = [_reemplazar(a, valores) for a in config["comando"]]
        # Un entorno mínimo, no el heredado: con PYTHONPATH, LD_PRELOAD, BASH_ENV o un PATH propio, quien corre `evidencia` podría
        # cambiar lo que hace el sensor aprobado sin cambiar su declaración. El checkout no está conectado al almacén (la conexión va
        # por el directorio de Git): almacenes.registros_de lo lee de las dos variables de Factory.
        entorno = {**entorno_minimo(), "ORACLE_FACTORY_CHECKOUT": str(checkout.resolve()), "ORACLE_FACTORY_REGISTROS": str(registros)}
        inicio = time.monotonic()
        codigo, texto, motivo = procesos.correr_en_grupo(argv, checkout, config["tope_minutos"] * 60, entorno)
        segundos = round(time.monotonic() - inicio, 1)
    sys.stdout.write(texto if texto.endswith("\n") or not texto else texto + "\n")
    hechos = salida / "hechos.json"
    huella_hechos = cli.sha256(hechos.read_bytes()) if hechos.is_file() and not hechos.is_symlink() else None
    carpeta, estado = cli.abierto(identificador)  # otra vez: el registro pudo cambiar mientras corría el sensor
    cli.evento(estado, "evidencia_producida", commit=head, codigo=codigo, segundos=segundos, hechos_sha256=huella_hechos,
               sensor_sha256=huella(config), comando=list(config["comando"]))  # el aprobado, sin las rutas de esta máquina
    cli.guardar(carpeta, estado)
    if codigo:
        causa = (f" (se pasó del tope de {config['tope_minutos']} min y se detuvo a todo su grupo de procesos)" if motivo == "plazo"
                 else " (no arrancó)" if motivo == "no_arranca" else "")
        raise cli.FactoryError(f"el sensor terminó con código {codigo}{causa}; la corrida quedó registrada en el cambio")
    if huella_hechos is None:
        raise cli.FactoryError(f"el sensor terminó bien pero no dejó {hechos.relative_to(cli.ROOT)}; la corrida quedó registrada")
    print(f"Hechos producidos por Factory en {hechos.relative_to(cli.ROOT)} (commit {sha}). Próximo paso: oracle-factory juzgar {identificador}")


def hechos_de(identificador: str, estado: dict) -> dict | None:
    """De dónde salen los hechos del veredicto: producidos por Factory si cada huella juzgada es la de una producción registrada para el
    candidato vigente que terminó bien (código 0: una corrida que falló o se pasó del tope no respalda sus hechos) y se hizo con un
    sensor aprobado por una persona. None si todavía no hay veredicto."""
    oracle = estado.get("oracle") or {}
    huellas = [h for _, h in cli.hechos_registrados(oracle)]
    if not oracle or not huellas:
        return None
    candidato = cli.candidato_vigente(identificador)
    # El commit entero, no el prefijo de siete caracteres: si el prefijo es ambiguo (dos commits), no se resuelve y nada cuenta.
    completo = _git(["-C", str(cli.PRODUCTO or cli.ROOT), "rev-parse", "--verify", "--quiet", f"{candidato}^{{commit}}"]).stdout.strip() if candidato else ""
    del_sensor = _huellas_aprobadas()  # sólo cuenta una producción hecha con un sensor que aprobó una persona
    producidas = {e.get("hechos_sha256") for e in estado.get("eventos") or []
                  if e.get("accion") == "evidencia_producida" and e.get("codigo") == 0 and completo
                  and e.get("commit") == completo and e.get("sensor_sha256") in del_sensor}
    propios = all(h and h in producidas for h in huellas)
    return {"producidos_por_factory": propios, "commit": candidato if propios else None,
            "texto": f"producidos por Factory (oracle-factory evidencia, commit {candidato})" if propios
            else "declarados: no los produjo Factory"}


def politica() -> str:
    return (cli.config_proyecto()["sensor"] or {}).get("hechos", "avisar")


def pendientes(identificador: str, estado: dict) -> list[str]:
    """Con «exigir», lo que falta para cerrar si los hechos del veredicto no los produjo Factory. Un cambio ya cerrado (o abandonado) no
    pide nada: se cerró con las reglas de su momento, y «exigir» gobierna el cierre, no lo reabre."""
    if estado.get("fase") in ("cerrada", "abandonada"):
        return []
    origen = hechos_de(identificador, estado)
    if not origen or origen["producidos_por_factory"] or politica() != "exigir":
        return []
    return [f"hechos del veredicto: no los produjo Factory para el candidato vigente (el proyecto exige que sí): corré "
            f"oracle-factory evidencia {identificador} y volvé a juzgar"]


def avisos(identificador: str, estado: dict) -> list[str]:
    """Con «avisar», el aviso de que los hechos no los produjo Factory."""
    origen = hechos_de(identificador, estado)
    if not origen or origen["producidos_por_factory"] or politica() == "exigir":
        return []
    return [f"los hechos del veredicto no los produjo Factory: los declaró quien los dejó ahí (oracle-factory evidencia {identificador} los produce)"]


# Al final a propósito, como en los otros módulos: `cli` importa este módulo y lo usa sólo al llamar a sus funciones.
from . import cli  # noqa: E402
