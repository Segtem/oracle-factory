"""Factory produce los hechos: corre el sensor que declara el proyecto sobre un checkout limpio del commit y dice de dónde salen.

El sensor se declara en `.factory/config.json`:

    "sensor": {"comando": ["{python}", "tools/sensor.py", "--salida", "{salida}"], "tope_minutos": 60, "hechos": "avisar"}

`comando` es una lista de argumentos; sus marcadores se reemplazan al correrlo: `{python}` (el Python de Factory), `{cambio}`,
`{salida}` (la carpeta de evidencia del candidato, que el sensor crea y donde deja `hechos.json`), `{registros}` (dónde están los
registros: el almacén, si está conectado) y `{producto}` (la carpeta del producto, para lo que no se versiona, como `node_modules`).
Con `"hechos": "exigir"`, `cerrar` pide que los hechos del veredicto los haya producido Factory; con `"avisar"` (el valor por
defecto), sólo se avisa.

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo."""
from __future__ import annotations

import os
from pathlib import Path
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
    locales = cli.cambios_locales_de_producto()
    if locales:
        raise cli.FactoryError("el producto tiene cambios sin commitear: " + ", ".join(locales[:10]) + (" …" if len(locales) > 10 else "")
                               + ". La evidencia se produce del commit: commitealos o guardalos aparte. No se corrió nada")
    head = cli.git_producto(["git", "rev-parse", "--verify", "HEAD"]).stdout.strip()
    if not head:
        raise cli.FactoryError("el producto no tiene ningún commit todavía")
    sha = head[:7]
    salida = cli.ruta_segura(estructura.ruta_canonica(cli.ROOT, identificador, "evidencia", sha))
    if salida.exists():
        raise cli.FactoryError(f"ya hay evidencia del candidato {sha} ({salida.relative_to(cli.ROOT)}): un commit nuevo es un candidato "
                               "nuevo; si querés repetirla sobre este, borrá esa carpeta primero")
    base = cli.ruta_segura(cli.ROOT / estructura.DIR / "local" / "sensores")  # local/: Git la ignora, como los checkouts de los revisores
    base.mkdir(parents=True, exist_ok=True)
    registros = cli.ROOT.resolve()
    with tempfile.TemporaryDirectory(prefix=f"{sha}-", dir=base) as tmp:
        checkout = Path(tmp) / "producto"
        p = cli.ejecutar(["git", "clone", "--quiet", "--local", "--no-checkout", str(cli.PRODUCTO or cli.ROOT), str(checkout)])
        if not p.returncode:
            p = cli.ejecutar(["git", "-C", str(checkout), "checkout", "--quiet", "--detach", head])
        for remoto in cli.ejecutar(["git", "-C", str(checkout), "remote"]).stdout.split() if not p.returncode else []:
            p = cli.ejecutar(["git", "-C", str(checkout), "remote", "remove", remoto])  # sin remoto: el sensor no empuja nada
        if p.returncode:
            raise cli.FactoryError(f"no pude preparar el checkout limpio del commit {sha}: {(p.stderr or p.stdout).strip()}")
        valores = {"python": sys.executable, "cambio": identificador, "salida": str(salida), "registros": str(registros),
                   "producto": str((cli.PRODUCTO or cli.ROOT).resolve())}
        argv = [_reemplazar(a, valores) for a in config["comando"]] + list(extra)
        # El checkout no está conectado al almacén (la conexión va por el directorio de Git): almacenes.registros_de lo lee de acá.
        entorno = {**os.environ, "ORACLE_FACTORY_CHECKOUT": str(checkout.resolve()), "ORACLE_FACTORY_REGISTROS": str(registros)}
        inicio = time.monotonic()
        codigo, texto, motivo = procesos.correr_en_grupo(argv, checkout, config["tope_minutos"] * 60, entorno)
        segundos = round(time.monotonic() - inicio, 1)
    sys.stdout.write(texto if texto.endswith("\n") or not texto else texto + "\n")
    hechos = salida / "hechos.json"
    huella = cli.sha256(hechos.read_bytes()) if hechos.is_file() and not hechos.is_symlink() else None
    carpeta, estado = cli.abierto(identificador)  # otra vez: el registro pudo cambiar mientras corría el sensor
    cli.evento(estado, "evidencia_producida", commit=head, codigo=codigo, segundos=segundos, hechos_sha256=huella,
               comando=list(config["comando"]) + list(extra))  # el comando declarado, sin las rutas de esta máquina
    cli.guardar(carpeta, estado)
    if codigo:
        causa = (f" (se pasó del tope de {config['tope_minutos']} min y se detuvo a todo su grupo de procesos)" if motivo == "plazo"
                 else " (no arrancó)" if motivo == "no_arranca" else "")
        raise cli.FactoryError(f"el sensor terminó con código {codigo}{causa}; la corrida quedó registrada en el cambio")
    if huella is None:
        raise cli.FactoryError(f"el sensor terminó bien pero no dejó {hechos.relative_to(cli.ROOT)}; la corrida quedó registrada")
    print(f"Hechos producidos por Factory en {hechos.relative_to(cli.ROOT)} (commit {sha}). Próximo paso: oracle-factory juzgar {identificador}")


def hechos_de(identificador: str, estado: dict) -> dict | None:
    """De dónde salen los hechos del veredicto: producidos por Factory si cada huella juzgada es la de una producción registrada para el
    candidato vigente. None si todavía no hay veredicto."""
    oracle = estado.get("oracle") or {}
    huellas = [h for _, h in cli.hechos_registrados(oracle)]
    if not oracle or not huellas:
        return None
    candidato = cli.candidato_vigente(identificador)
    producidas = {e.get("hechos_sha256") for e in estado.get("eventos") or []
                  if e.get("accion") == "evidencia_producida" and candidato and str(e.get("commit") or "").startswith(candidato)}
    propios = all(h and h in producidas for h in huellas)
    return {"producidos_por_factory": propios, "commit": candidato if propios else None,
            "texto": f"producidos por Factory (oracle-factory evidencia, commit {candidato})" if propios
            else "declarados: no los produjo Factory"}


def politica() -> str:
    return (cli.config_proyecto()["sensor"] or {}).get("hechos", "avisar")


def pendientes(identificador: str, estado: dict) -> list[str]:
    """Con «exigir», lo que falta para cerrar si los hechos del veredicto no los produjo Factory."""
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
