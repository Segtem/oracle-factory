"""Las decisiones de una persona, firmadas con su llave (cambio firmas).

Con `"firmas": "exigir"` en `.factory/config.json`, cada decisión de una persona que arma `registro_decision` se firma al
escribirse con `ssh-keygen -Y sign` y la llave de la persona (`~/.ssh/oracle-factory`, o la de `ORACLE_FACTORY_LLAVE`), sin
ssh-agent: la frase se escribe en la terminal cada vez. `verificar`, `juzgar` y `cerrar` comprueban cada firma contra
`.factory-firmantes` del producto (formato `allowed_signers` de OpenSSH).

Límites: un proceso del mismo usuario que pueda leer la memoria de `ssh-keygen` (si `ptrace_scope` lo permite) o un registrador
de teclas que capture la frase puede firmar como la persona. La lista de firmantes es tan confiable como el repo del producto."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

NAMESPACE = "oracle-factory-decision"
FIRMANTES = ".factory-firmantes"
VALORES = (None, "no", "exigir")
CAMPOS = ("spec_aprobada", "revision", "cierre", "abandono")
EVENTOS = ("modo_cambiado", "union_decidida", "soltado")  # decisiones de persona que quedan como eventos del cambio
SENSOR = "sensor-aprobado"  # el campo con que se firma una aprobación del sensor (del proyecto, no de un cambio)
FUERA_DEL_TEXTO = ("firma", "firma_llave")
HEREDADAS = ("SSH_AUTH_SOCK", "SSH_AGENT_PID", "SSH_ASKPASS", "SSH_ASKPASS_REQUIRE")
ENTORNO_PRUEBA: dict = {}  # sólo lo llenan las pruebas (la frase por SSH_ASKPASS); Factory no lo toma de su entorno
_POR_FIRMAR: set[str] = set()  # el «cuando» de las decisiones de persona armadas en este proceso: sólo ésas se firman


def exige(config: dict) -> bool:
    return config.get("firmas") == "exigir"


def llave() -> Path:
    return Path(os.environ.get("ORACLE_FACTORY_LLAVE") or Path.home() / ".ssh" / "oracle-factory").expanduser()


def entorno() -> dict:
    """El entorno de ssh-keygen: el de Factory sin ssh-agent ni SSH_ASKPASS heredados, así la frase sale de la terminal."""
    return {**{k: v for k, v in os.environ.items() if k not in HEREDADAS}, **ENTORNO_PRUEBA}


def _ssh_keygen(argumentos: list[str], entrada=None, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(["ssh-keygen", *argumentos], env=entorno(), stdin=entrada, capture_output=True, text=True, timeout=300, **kw)


def lista_para_firmar() -> Path:
    """La llave, si existe y tiene frase; si no, FactoryError con lo que falta (antes de registrar nada)."""
    ruta = llave()
    if not ruta.is_file():
        raise _error(f"falta la llave para firmar la decisión ({ruta}): creala con ssh-keygen -t ed25519 -f {ruta} y agregá su "
                     f"parte pública a {FIRMANTES} del producto, o indicá otra con ORACLE_FACTORY_LLAVE")
    if _ssh_keygen(["-y", "-P", "", "-f", str(ruta)], entrada=subprocess.DEVNULL).returncode == 0:
        raise _error(f"la llave {ruta} no tiene frase: un agente que corre con tu usuario podría firmar con ella; ponele una "
                     f"(ssh-keygen -p -f {ruta}) o usá otra")
    return ruta


def huella(ruta: Path) -> str:
    r = _ssh_keygen(["-lf", str(ruta)], entrada=subprocess.DEVNULL)
    partes = r.stdout.split()
    if r.returncode or len(partes) < 2:
        raise _error(f"no pude leer la huella de la llave {ruta}")
    return partes[1]


def firmar(texto: bytes, entrada=None) -> tuple[str, str]:
    """(firma, huella de la llave) del texto. La frase la pide ssh-keygen en la terminal; si la firma no sale, FactoryError."""
    ruta = lista_para_firmar()
    with tempfile.TemporaryDirectory(prefix="oracle-factory-firma-") as tmp:
        archivo = Path(tmp) / "decision"
        archivo.write_bytes(texto)
        r = _ssh_keygen(["-Y", "sign", "-f", str(ruta), "-n", NAMESPACE, str(archivo)], entrada=entrada)
        firma = archivo.with_name("decision.sig")
        if r.returncode or not firma.is_file():
            raise _error(f"la firma no salió con la llave {ruta}: {(r.stderr or r.stdout).strip() or 'ssh-keygen falló'}; no registré nada")
        return firma.read_text(encoding="utf-8"), huella(ruta)


def texto(cambio: str, campo: str, registro: dict) -> bytes:
    """Lo que se firma: el cambio, el campo y el registro entero de la decisión (sin la firma), en JSON canónico."""
    propio = {k: v for k, v in registro.items() if k not in FUERA_DEL_TEXTO}
    return json.dumps({"cambio": cambio, "campo": campo, "registro": propio}, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def registros(estado: dict) -> list[tuple[str, dict]]:
    """(campo, registro) de cada decisión registrada en el cambio que se firma."""
    salida = [(c, estado[c]) for c in CAMPOS if isinstance(estado.get(c), dict)]
    medidas = estado.get("medidas")
    if isinstance(medidas, dict):
        salida += [(f"medidas/{rid}", r) for rid, r in sorted(medidas.items()) if isinstance(r, dict)]
    eventos = estado.get("eventos")
    if isinstance(eventos, list):
        salida += [(f"eventos/{e['accion']}@{e.get('cuando')}", e) for e in eventos if isinstance(e, dict) and e.get("accion") in EVENTOS]
    return salida


def marcar(registro: dict) -> dict:
    """Con «exigir», deja para firmar al escribirse la decisión de persona que se acaba de armar; comprueba antes la llave."""
    if registro.get("tipo_actor") == "persona" and exige(_cli().config_proyecto()):
        lista_para_firmar()
        _POR_FIRMAR.add(registro["cuando"])
    return registro


def sellar(estado: dict) -> None:
    """Firma, antes de escribir el registro, las decisiones de persona armadas en este proceso que todavía no tienen firma."""
    for campo, registro in registros(estado):
        if registro.get("cuando") in _POR_FIRMAR and "firma" not in registro:
            registro["firma"], registro["firma_llave"] = firmar(texto(estado.get("id", ""), campo, registro))
            _POR_FIRMAR.discard(registro["cuando"])


def problema(cambio: str, campo: str, registro: dict, firmantes: Path) -> str | None:
    """None si la firma de la decisión verifica contra su texto y es de una llave de la lista; si no, qué le pasa."""
    if not isinstance(registro.get("firma"), str):
        return "sin firma"
    if not firmantes.is_file():
        return f"no hay {FIRMANTES} en el producto: ninguna firma cuenta"
    with tempfile.TemporaryDirectory(prefix="oracle-factory-verifica-") as tmp:
        sig = Path(tmp) / "decision.sig"
        sig.write_text(registro["firma"], encoding="utf-8")
        r = _ssh_keygen(["-Y", "find-principals", "-s", str(sig), "-f", str(firmantes)], entrada=subprocess.DEVNULL)
        principales = r.stdout.split()
        if r.returncode or not principales:
            return f"la firma es de una llave que no está en {FIRMANTES}"
        with tempfile.TemporaryFile() as entrada:
            entrada.write(texto(cambio, campo, registro))
            entrada.seek(0)
            r = _ssh_keygen(["-Y", "verify", "-f", str(firmantes), "-I", principales[0], "-n", NAMESPACE, "-s", str(sig)], entrada=entrada)
        if r.returncode:
            return "la firma no corresponde a lo registrado (el registro cambió después de firmarse)"
    return None


def pendientes(estado: dict) -> list[str]:
    """Con «exigir», cada decisión de persona del cambio sin una firma válida, nombrada."""
    cli = _cli()
    if not exige(cli.config_proyecto()):
        return []
    firmantes = (cli.PRODUCTO or cli.ROOT) / FIRMANTES
    salida = []
    for campo, registro in registros(estado):
        if registro.get("tipo_actor") != "persona":
            continue
        falla = problema(estado.get("id", ""), campo, registro, firmantes)
        if falla:
            nombre = campo.replace("medidas/", "medidas de ").replace("eventos/", "").split("@")[0]
            salida.append(f"la decisión «{nombre}» de {registro.get('actor', '?')}: {falla}; no cuenta hasta que una persona la vuelva a tomar")
    return salida


def firmar_aprobacion(aprobacion: dict) -> dict:
    """Con «exigir», la aprobación del sensor que se va a escribir, con su firma."""
    if exige(_cli().config_proyecto()):
        aprobacion["firma"], aprobacion["firma_llave"] = firmar(texto("proyecto", SENSOR, aprobacion))
    return aprobacion


def aprobacion_cuenta(aprobacion: dict) -> bool:
    """Si una aprobación del sensor cuenta: siempre sin «exigir»; con «exigir», sólo con una firma válida de la lista."""
    cli = _cli()
    return not exige(cli.config_proyecto()) or problema("proyecto", SENSOR, aprobacion, (cli.PRODUCTO or cli.ROOT) / FIRMANTES) is None


def avisos(estado: dict) -> list[str]:
    """Sin «exigir», que las decisiones de persona del cambio no están firmadas."""
    if exige(_cli().config_proyecto()) or not any(r.get("tipo_actor") == "persona" for _, r in registros(estado)):
        return []
    return ['las decisiones de persona de este cambio no están firmadas: cualquier proceso con una terminal puede tomarlas; '
            f'con "firmas": "exigir" en .factory/config.json y tu llave en {FIRMANTES}, cada una se firma (ver docs/firmas.md)']


def _error(mensaje: str):
    return _cli().FactoryError(mensaje)


def _cli():
    from . import cli
    return cli
